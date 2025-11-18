"""
用户操作日志中间件
用于记录用户的关键操作，如浏览活动、报名等
"""
from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any
from core.auth.jwt_handler import JWTHandler
from dao.user_logs_dao import UserOperationLogsDAO
import logging

logger = logging.getLogger(__name__)


class OperationLogger:
    """操作日志记录器"""
    
    def __init__(self):
        self.log_dao = UserOperationLogsDAO()
    
    async def log_activity_view(
        self,
        request: Request,
        activity_id: int,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录用户浏览活动的操作
        
        Args:
            request: FastAPI请求对象（包含用户信息）
            activity_id: 活动ID
            extra_data: 附加数据
        
        Returns:
            是否记录成功
        """
        try:
            # 获取用户信息
            user = request.state.user
            if not user:
                logger.warning("无法获取用户信息，跳过操作日志记录")
                return False
            
            # 记录日志
            await self.log_dao.create_log(
                user_id=user.id,
                activity_id=activity_id,
                operation_type="view_activity",
                extra_data=extra_data or {}
            )
            
            logger.info(f"用户 {user.id} 浏览了活动 {activity_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录活动浏览日志失败: {str(e)}")
            return False
    
    async def log_activity_registration(
        self,
        request: Request,
        activity_id: int,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录用户报名活动的操作
        
        Args:
            request: FastAPI请求对象（包含用户信息）
            activity_id: 活动ID
            extra_data: 附加数据
        
        Returns:
            是否记录成功
        """
        try:
            # 获取用户信息
            user = request.state.user
            if not user:
                logger.warning("无法获取用户信息，跳过操作日志记录")
                return False
            
            # 记录日志
            await self.log_dao.create_log(
                user_id=user.id,
                activity_id=activity_id,
                operation_type="register_activity",
                extra_data=extra_data or {}
            )
            
            logger.info(f"用户 {user.id} 报名了活动 {activity_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录活动报名日志失败: {str(e)}")
            return False
    
    async def log_custom_operation(
        self,
        request: Request,
        activity_id: int,
        operation_type: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录自定义操作类型
        
        Args:
            request: FastAPI请求对象（包含用户信息）
            activity_id: 活动ID
            operation_type: 操作类型
            extra_data: 附加数据
        
        Returns:
            是否记录成功
        """
        try:
            # 获取用户信息
            user = request.state.user
            if not user:
                logger.warning("无法获取用户信息，跳过操作日志记录")
                return False
            
            # 记录日志
            await self.log_dao.create_log(
                user_id=user.id,
                activity_id=activity_id,
                operation_type=operation_type,
                extra_data=extra_data or {}
            )
            
            logger.info(f"用户 {user.id} 执行了操作 {operation_type} 在活动 {activity_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录操作日志失败: {str(e)}")
            return False

    async def log_operation(
        self,
        user_id: int,
        operation_type: str,
        activity_id: int = 0,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录用户操作（通用方法）
        
        Args:
            user_id: 用户ID
            operation_type: 操作类型
            activity_id: 活动ID（可选，默认为0表示非活动相关操作）
            extra_data: 附加数据
        
        Returns:
            是否记录成功
        """
        try:
            # 记录日志
            await self.log_dao.create_log(
                user_id=user_id,
                activity_id=activity_id,
                operation_type=operation_type,
                extra_data=extra_data or {}
            )
            
            logger.info(f"用户 {user_id} 执行了操作 {operation_type}")
            return True
            
        except Exception as e:
            logger.error(f"记录操作日志失败: {str(e)}")
            return False


# 全局日志记录器实例
operation_logger = OperationLogger()
