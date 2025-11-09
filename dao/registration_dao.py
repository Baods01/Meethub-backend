from typing import Optional, List, Dict
from datetime import datetime
from tortoise.expressions import F, Q
from tortoise.functions import Count
from .base import BaseDAO
from models.registrations import Registrations


class RegistrationDAO(BaseDAO[Registrations]):
    """报名表数据访问对象"""
    
    def __init__(self):
        super().__init__(Registrations)

    async def create_registration(
        self, 
        activity_id: int, 
        participant_id: int, 
        data: Dict
    ) -> Optional[Registrations]:
        """创建报名记录"""
        # 检查是否已经报名
        exists = await self.model.filter(
            activity_id=activity_id,
            participant_id=participant_id
        ).exists()
        
        if exists:
            return None
            
        registration = await self.create(
            activity_id=activity_id,
            participant_id=participant_id,
            **data
        )
        
        # 重新获取报名记录以包含关联数据
        return await self.model.get(id=registration.id).prefetch_related('participant', 'activity__publisher')

    async def get_registration_detail(self, registration_id: int) -> Optional[Registrations]:
        """获取报名详情"""
        return await self.model.get_or_none(
            id=registration_id
        ).prefetch_related('participant', 'activity', 'activity__publisher')

    async def update_registration_status(
        self, 
        registration_id: int, 
        status: str,
        activity_id: int = None
    ) -> Optional[Registrations]:
        """更新报名状态"""
        registration = await self.get_by_id(registration_id)
        if registration:
            old_status = registration.status
            registration.status = status
            await registration.save()
            
            # 如果状态从非approved变为approved，增加活动参与人数
            if old_status != 'approved' and status == 'approved':
                from .activity_dao import ActivityDAO
                await ActivityDAO().update_participants_count(activity_id, True)
            # 如果状态从approved变为其他状态，减少活动参与人数
            elif old_status == 'approved' and status != 'approved':
                from .activity_dao import ActivityDAO
                await ActivityDAO().update_participants_count(activity_id, False)
                
        return registration

    async def check_in(self, registration_id: int) -> Optional[Registrations]:
        """签到"""
        registration = await self.get_by_id(registration_id)
        if registration and registration.status == 'approved':
            registration.check_in_time = datetime.now()
            await registration.save()
        return registration

    async def check_out(
        self, 
        registration_id: int, 
        feedback: Optional[str] = None,
        rating: Optional[int] = None
    ) -> Optional[Registrations]:
        """签退"""
        registration = await self.get_by_id(registration_id)
        if registration and registration.check_in_time:
            registration.check_out_time = datetime.now()
            if feedback:
                registration.feedback = feedback
            if rating:
                registration.rating = rating
            await registration.save()
        return registration

    async def get_user_registrations(
        self, 
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """获取用户的报名记录"""
        query = self.model.filter(participant_id=user_id)
        
        if status:
            query = query.filter(status=status)
            
        total = await query.count()
        
        query = query.order_by('-registration_time')\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .prefetch_related('activity', 'activity__publisher', 'participant')
            
        registrations = await query
        
        return {
            'total': total,
            'items': registrations,
            'page': page,
            'page_size': page_size
        }

    async def get_activity_registrations(
        self,
        activity_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """获取活动的报名记录"""
        query = self.model.filter(activity_id=activity_id)
        
        if status:
            query = query.filter(status=status)
            
        total = await query.count()
        
        query = query.order_by('-registration_time')\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .prefetch_related(
                'participant',
                'activity',
                'activity__publisher'
            )
            
        registrations = await query
        
        return {
            'total': total,
            'items': registrations,
            'page': page,
            'page_size': page_size
        }

    async def get_registration_stats(self, activity_id: int) -> Dict:
        """获取报名统计信息"""
        query = self.model.filter(activity_id=activity_id)
        
        # 计算各状态的数量
        status_counts = await query.annotate(
            count=Count('id')
        ).group_by('status').values('status', 'count')
        
        # 统计签到率
        total_approved = await query.filter(status='approved').count()
        total_checked_in = await query.filter(
            status='approved',
            check_in_time__isnull=False
        ).count()
        
        # 计算平均评分
        ratings = [r.rating for r in await query.filter(rating__isnull=False)]
        
        stats = {
            'total_registrations': await query.count(),
            'approved_count': 0,
            'pending_count': 0,
            'rejected_count': 0,
            'cancelled_count': 0,
            'check_in_rate': total_checked_in / total_approved if total_approved > 0 else 0,
            'average_rating': sum(ratings) / len(ratings) if ratings else None
        }
        
        # 更新各状态计数
        for item in status_counts:
            if item['status'] == 'approved':
                stats['approved_count'] = item['count']
            elif item['status'] == 'pending':
                stats['pending_count'] = item['count']
            elif item['status'] == 'rejected':
                stats['rejected_count'] = item['count']
            elif item['status'] == 'cancelled':
                stats['cancelled_count'] = item['count']
                
        return stats