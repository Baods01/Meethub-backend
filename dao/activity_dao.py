from typing import Optional, List, Dict
from datetime import datetime
from tortoise.expressions import F, Q
from tortoise.functions import Count
from .base import BaseDAO
from models.activities import Activities
from models.registrations import Registrations


class ActivityDAO(BaseDAO[Activities]):
    """活动数据访问对象"""
    
    def __init__(self):
        super().__init__(Activities)

    async def create_activity(self, data: Dict, publisher_id: int) -> Activities:
        """创建活动"""
        activity = await self.create(publisher_id=publisher_id, **data)
        # 重新获取活动信息以包含发布者信息
        return await self.model.get(id=activity.id).prefetch_related('publisher')

    async def get_activity_with_stats(self, activity_id: int) -> Optional[Activities]:
        """获取活动详情及统计信息"""
        return await self.model.get_or_none(
            id=activity_id,
            is_deleted=False
        ).prefetch_related('publisher', 'registrations')

    async def update_activity_status(self, activity_id: int, status: str) -> Optional[Activities]:
        """更新活动状态"""
        activity = await self.get_by_id(activity_id)
        if activity:
            activity.status = status
            await activity.save()
        return activity

    async def increment_views(self, activity_id: int) -> bool:
        """增加浏览量"""
        rows_affected = await self.model.filter(id=activity_id).update(
            views_count=F('views_count') + 1
        )
        return rows_affected > 0

    async def update_participants_count(self, activity_id: int, increment: bool = True) -> bool:
        """更新参与人数"""
        delta = 1 if increment else -1
        rows_affected = await self.model.filter(id=activity_id).update(
            current_participants=F('current_participants') + delta
        )
        return rows_affected > 0

    async def search_activities(
        self,
        keyword: Optional[str] = None,
        benefits: Optional[List[str]] = None,
        audience: Optional[Dict] = None,
        categories: Optional[List[str]] = None,
        time_range: Optional[Dict[str, datetime]] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """搜索活动"""
        query = self.model.filter(is_deleted=False)

        # 关键词搜索
        if keyword:
            query = query.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword)
            )

        # 收益类型筛选
        if benefits:
            query = query.filter(benefits__contains={"benefit": benefits})

        # 目标受众筛选
        if audience:
            for key, value in audience.items():
                if isinstance(value, list):
                    # 如果value是列表，检查目标受众中是否包含这些值
                    query = query.filter(target_audience__contains={key: value})

        # 活动类型筛选
        if categories:
            query = query.filter(tags__overlap=categories)

        # 时间范围筛选
        if time_range:
            if start_time := time_range.get('start'):
                query = query.filter(start_time__gte=start_time)
            if end_time := time_range.get('end'):
                query = query.filter(end_time__lte=end_time)

        # 统计总数（在排序之前）
        total = await query.count()

        # 排序
        if sort_by:
            # 处理降序排序（以'-'开头的字段）
            if sort_by.startswith('-'):
                field = sort_by[1:]
                query = query.order_by(f"-{field}")
            else:
                query = query.order_by(sort_by)
        else:
            query = query.order_by('-created_at')

        # 统计总数
        total = await query.count()

        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 预加载关联数据
        activities = await query.prefetch_related('publisher')

        return {
            'total': total,
            'items': activities,
            'page': page,
            'page_size': page_size
        }

    async def get_activity_stats(self, activity_id: int) -> Dict:
        """获取活动统计信息"""
        activity = await self.get_by_id(activity_id)
        if not activity:
            return None

        registrations = await Registrations.filter(activity_id=activity_id)
        
        total_registrations = len(registrations)
        completed_registrations = len([r for r in registrations if r.check_out_time])
        ratings = [r.rating for r in registrations if r.rating is not None]
        
        return {
            'total_participants': activity.current_participants,
            'completion_rate': completed_registrations / total_registrations if total_registrations > 0 else 0,
            'average_rating': sum(ratings) / len(ratings) if ratings else None,
            'total_views': activity.views_count
        }

    async def soft_delete(self, activity_id: int) -> bool:
        """软删除活动"""
        activity = await self.get_by_id(activity_id)
        if activity:
            activity.is_deleted = True
            await activity.save()
            return True
        return False