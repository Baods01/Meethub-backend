"""
活动与报名状态实时更新器
- 启动时进行一次状态检查与纠正
- 自动更新活动与报名的状态（基于当前时间与开始/结束时间对比）
"""
import logging
from datetime import datetime
from tortoise.expressions import F, Q
from models.activities import Activities
from models.registrations import Registrations

logger = logging.getLogger(__name__)


class StatusUpdater:
    """活动与报名状态更新器"""
    
    @staticmethod
    async def check_and_fix_all_statuses():
        """启动时检查并纠正所有异常状态"""
        logger.info("开始检查活动和报名状态...")
        
        # 检查并纠正活动状态
        await StatusUpdater._check_and_fix_activity_statuses()
        
        # 检查并纠正报名状态
        await StatusUpdater._check_and_fix_registration_statuses()
        
        logger.info("状态检查和纠正完成")
    
    @staticmethod
    async def _check_and_fix_activity_statuses():
        """检查并纠正活动状态"""
        now = datetime.now()
        
        # 获取所有非草稿、非已取消的活动
        activities = await Activities.filter(
            Q(status__in=['published', 'ongoing', 'ended']) & 
            Q(is_deleted=False)
        )
        
        corrections = {
            'should_be_published': [],  # 应该是published的
            'should_be_ongoing': [],    # 应该是ongoing的
            'should_be_ended': []       # 应该是ended的
        }
        
        for activity in activities:
            correct_status = None
            
            # 移除时区信息以进行比较
            start_time = activity.start_time.replace(tzinfo=None) if activity.start_time.tzinfo else activity.start_time
            end_time = activity.end_time.replace(tzinfo=None) if activity.end_time.tzinfo else activity.end_time
            
            # 判断正确状态：
            # 1. 当前时间小于开始时间 -> published
            # 2. 开始时间 <= 当前时间 < 结束时间 -> ongoing
            # 3. 当前时间 >= 结束时间 -> ended
            
            if now < start_time:
                correct_status = 'published'
            elif start_time <= now < end_time:
                correct_status = 'ongoing'
            else:  # now >= end_time
                correct_status = 'ended'
            
            # 如果当前状态不正确，记录并纠正
            if activity.status != correct_status:
                corrections[f'should_be_{correct_status}'].append(activity.id)
                activity.status = correct_status
                await activity.save()
                logger.warning(
                    f"活动 {activity.id} ({activity.title}) 状态已纠正: "
                    f"{activity.status} -> {correct_status}"
                )
        
        # 日志汇总
        for key, ids in corrections.items():
            if ids:
                logger.info(f"{key}: {ids}")
    
    @staticmethod
    async def _check_and_fix_registration_statuses():
        """检查并纠正报名状态"""
        now = datetime.now()
        
        # 获取所有已通过的报名记录
        registrations = await Registrations.filter(
            status='approved'
        ).prefetch_related('activity')
        
        corrections = {
            'should_check_in': [],   # 签到了但未签退
            'should_check_out': []   # 已签退但check_out_time为空
        }
        
        for registration in registrations:
            activity = registration.activity
            
            # 移除时区信息以进行比较
            end_time = activity.end_time.replace(tzinfo=None) if activity.end_time.tzinfo else activity.end_time
            
            # 如果报名的活动已结束，但报名状态未签退
            if now >= end_time and registration.check_out_time is None:
                # 记录异常，但不自动修改签退时间（因为这需要确切的签退时间）
                corrections['should_check_out'].append(registration.id)
                logger.warning(
                    f"报名 {registration.id} 所属活动已结束，但未签退"
                )
        
        # 日志汇总
        for key, ids in corrections.items():
            if ids:
                logger.info(f"{key}: {ids}")
    
    @staticmethod
    async def auto_update_statuses():
        """自动更新活动和报名的状态
        
        基于数据库实时计算的策略：
        - 检查所有非草稿、非已取消的活动
        - 根据当前时间自动更新状态
        """
        now = datetime.now()
        
        # 更新应该为ongoing的活动
        await Activities.filter(
            Q(status__in=['published', 'ended']) &
            Q(start_time__lte=now) &
            Q(end_time__gt=now) &
            Q(is_deleted=False)
        ).update(status='ongoing')
        
        # 更新应该为ended的活动
        await Activities.filter(
            Q(status__in=['published', 'ongoing']) &
            Q(end_time__lte=now) &
            Q(is_deleted=False)
        ).update(status='ended')
        
        # 更新应该为published的活动（如果异常处于ongoing/ended状态）
        await Activities.filter(
            Q(status__in=['ongoing', 'ended']) &
            Q(start_time__gt=now) &
            Q(is_deleted=False)
        ).update(status='published')
