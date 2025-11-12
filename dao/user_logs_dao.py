from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dao.base import BaseDAO
from models.user_logs import UserOperationLogs
from schemas.user_logs import (
    UserOperationLogCreate,
    UserOperationLogInDB,
    UserOperationLogList,
    UserOperationLogStats
)
from tortoise.expressions import Q


class UserOperationLogsDAO(BaseDAO):
    """用户操作日志数据访问对象"""

    def __init__(self):
        super().__init__(UserOperationLogs)

    async def create_log(
        self,
        user_id: int,
        activity_id: int,
        operation_type: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> UserOperationLogs:
        """
        创建操作日志
        
        Args:
            user_id: 用户ID
            activity_id: 活动ID
            operation_type: 操作类型 (view_activity | register_activity)
            extra_data: 附加数据
        
        Returns:
            创建的日志记录
        """
        return await self.model.create(
            user_id=user_id,
            activity_id=activity_id,
            operation_type=operation_type,
            extra_data=extra_data or {}
        )

    async def create_from_schema(
        self,
        user_id: int,
        log_data: UserOperationLogCreate
    ) -> UserOperationLogs:
        """
        从Schema创建操作日志
        
        Args:
            user_id: 用户ID
            log_data: 日志数据Schema
        
        Returns:
            创建的日志记录
        """
        return await self.create_log(
            user_id=user_id,
            activity_id=log_data.activity_id,
            operation_type=log_data.operation_type,
            extra_data=log_data.extra_data
        )

    async def get_user_logs(
        self,
        user_id: int,
        operation_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> UserOperationLogList:
        """
        获取用户的操作日志列表
        
        Args:
            user_id: 用户ID
            operation_type: 操作类型（可选）
            page: 页码
            page_size: 每页数量
        
        Returns:
            分页的日志列表
        """
        query = self.model.filter(user_id=user_id)
        
        if operation_type:
            query = query.filter(operation_type=operation_type)
        
        total = await query.count()
        
        logs = await query.order_by('-created_at') \
            .offset((page - 1) * page_size) \
            .limit(page_size)
        
        return UserOperationLogList(
            total=total,
            items=logs,
            page=page,
            page_size=page_size
        )

    async def get_activity_logs(
        self,
        activity_id: int,
        operation_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> UserOperationLogList:
        """
        获取活动的操作日志列表
        
        Args:
            activity_id: 活动ID
            operation_type: 操作类型（可选）
            page: 页码
            page_size: 每页数量
        
        Returns:
            分页的日志列表
        """
        query = self.model.filter(activity_id=activity_id)
        
        if operation_type:
            query = query.filter(operation_type=operation_type)
        
        total = await query.count()
        
        logs = await query.order_by('-created_at') \
            .offset((page - 1) * page_size) \
            .limit(page_size)
        
        return UserOperationLogList(
            total=total,
            items=logs,
            page=page,
            page_size=page_size
        )

    async def get_unique_viewed_activities(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[int]:
        """
        获取用户浏览过的不同活动ID列表
        
        Args:
            user_id: 用户ID
            limit: 限制数量
        
        Returns:
            活动ID列表
        """
        logs = await self.model.filter(
            user_id=user_id,
            operation_type="view_activity"
        ).order_by('-created_at').limit(limit).distinct()
        
        return [log.activity_id for log in logs]

    async def get_unique_registered_activities(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[int]:
        """
        获取用户报名过的不同活动ID列表
        
        Args:
            user_id: 用户ID
            limit: 限制数量
        
        Returns:
            活动ID列表
        """
        logs = await self.model.filter(
            user_id=user_id,
            operation_type="register_activity"
        ).order_by('-created_at').limit(limit).distinct()
        
        return [log.activity_id for log in logs]

    async def get_user_stats(self, user_id: int) -> UserOperationLogStats:
        """
        获取用户的操作统计
        
        Args:
            user_id: 用户ID
        
        Returns:
            操作统计信息
        """
        # 总浏览次数
        total_views = await self.model.filter(
            user_id=user_id,
            operation_type="view_activity"
        ).count()
        
        # 总报名次数
        total_registrations = await self.model.filter(
            user_id=user_id,
            operation_type="register_activity"
        ).count()
        
        # 浏览过的不同活动数（使用子查询）
        viewed_logs = await self.model.filter(
            user_id=user_id,
            operation_type="view_activity"
        ).distinct()
        unique_viewed = len(set(log.activity_id for log in viewed_logs))
        
        # 报名过的不同活动数
        registered_logs = await self.model.filter(
            user_id=user_id,
            operation_type="register_activity"
        ).distinct()
        unique_registered = len(set(log.activity_id for log in registered_logs))
        
        # 最后操作时间
        last_log = await self.model.filter(
            user_id=user_id
        ).order_by('-created_at').first()
        
        last_operation_time = last_log.created_at if last_log else None
        
        return UserOperationLogStats(
            total_views=total_views,
            total_registrations=total_registrations,
            unique_viewed_activities=unique_viewed,
            unique_registered_activities=unique_registered,
            last_operation_time=last_operation_time
        )

    async def get_activity_stats(
        self,
        activity_id: int
    ) -> Dict[str, int]:
        """
        获取活动的操作统计
        
        Args:
            activity_id: 活动ID
        
        Returns:
            包含view_count和register_count的统计字典
        """
        view_count = await self.model.filter(
            activity_id=activity_id,
            operation_type="view_activity"
        ).count()
        
        register_count = await self.model.filter(
            activity_id=activity_id,
            operation_type="register_activity"
        ).count()
        
        unique_viewers = await self.model.filter(
            activity_id=activity_id,
            operation_type="view_activity"
        ).distinct()
        unique_view_count = len(set(log.user_id for log in unique_viewers))
        
        unique_registrants = await self.model.filter(
            activity_id=activity_id,
            operation_type="register_activity"
        ).distinct()
        unique_register_count = len(set(log.user_id for log in unique_registrants))
        
        return {
            "total_views": view_count,
            "total_registrations": register_count,
            "unique_viewers": unique_view_count,
            "unique_registrants": unique_register_count
        }

    async def search_logs(
        self,
        user_id: Optional[int] = None,
        activity_id: Optional[int] = None,
        operation_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sort_by: Optional[str] = "-created_at",
        page: int = 1,
        page_size: int = 10
    ) -> UserOperationLogList:
        """
        多条件搜索日志
        
        Args:
            user_id: 用户ID（可选）
            activity_id: 活动ID（可选）
            operation_type: 操作类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            sort_by: 排序方式，支持 -created_at（倒序）或 created_at（正序）
            page: 页码
            page_size: 每页数量
        
        Returns:
            分页的日志列表
        """
        query = self.model.all()
        
        # 构建查询条件
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if activity_id:
            filters['activity_id'] = activity_id
        if operation_type:
            filters['operation_type'] = operation_type
        
        if filters:
            query = query.filter(**filters)
        
        # 时间范围
        if start_time and end_time:
            query = query.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
        elif start_time:
            query = query.filter(created_at__gte=start_time)
        elif end_time:
            query = query.filter(created_at__lte=end_time)
        
        # 总数
        total = await query.count()
        
        # 排序和分页
        if sort_by and sort_by.startswith('-'):
            query = query.order_by(sort_by)
        else:
            query = query.order_by(sort_by or '-created_at')
        
        logs = await query.offset((page - 1) * page_size).limit(page_size)
        
        return UserOperationLogList(
            total=total,
            items=logs,
            page=page,
            page_size=page_size
        )

    async def get_recent_logs(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 100
    ) -> List[UserOperationLogs]:
        """
        获取用户最近N天的操作日志
        
        Args:
            user_id: 用户ID
            days: 天数
            limit: 限制数量
        
        Returns:
            日志列表
        """
        start_time = datetime.now() - timedelta(days=days)
        
        return await self.model.filter(
            user_id=user_id,
            created_at__gte=start_time
        ).order_by('-created_at').limit(limit)

    async def check_activity_viewed(
        self,
        user_id: int,
        activity_id: int
    ) -> bool:
        """
        检查用户是否浏览过该活动
        
        Args:
            user_id: 用户ID
            activity_id: 活动ID
        
        Returns:
            是否浏览过
        """
        log = await self.model.filter(
            user_id=user_id,
            activity_id=activity_id,
            operation_type="view_activity"
        ).first()
        
        return log is not None

    async def check_activity_registered(
        self,
        user_id: int,
        activity_id: int
    ) -> bool:
        """
        检查用户是否报名过该活动
        
        Args:
            user_id: 用户ID
            activity_id: 活动ID
        
        Returns:
            是否报名过
        """
        log = await self.model.filter(
            user_id=user_id,
            activity_id=activity_id,
            operation_type="register_activity"
        ).first()
        
        return log is not None
