"""
用户操作日志相关的路由
提供日志信息的查询和删除接口
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from schemas.user_logs import (
    UserOperationLogInDB,
    UserOperationLogList,
    UserOperationLogSearch
)
from dao.user_logs_dao import UserOperationLogsDAO
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permission_checker import requires_permissions
from core.permissions import USER_LIST
from typing import Optional

router = APIRouter(
    prefix="/user-logs",
    tags=["用户日志"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

user_logs_dao = UserOperationLogsDAO()


@router.get(
    "",
    response_model=UserOperationLogList,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions(["user:list"])]
)
async def get_all_logs(
    request: Request,
    user_id: Optional[int] = Query(None, description="用户ID"),
    activity_id: Optional[int] = Query(None, description="活动ID"),
    operation_type: Optional[str] = Query(
        None,
        description="操作类型",
        regex="^(view_activity|register_activity)$"
    ),
    start_time: Optional[str] = Query(None, description="开始时间(ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间(ISO格式)"),
    sort_by: Optional[str] = Query(
        "-created_at",
        description="排序字段：前缀'-'表示倒序",
        regex="^(-?created_at|-?operation_type)$"
    ),
    page: int = Query(1, gt=0, description="页码"),
    page_size: int = Query(10, gt=0, le=100, description="每页数量")
):
    """
    获取所有用户操作日志
    - 需要用户列表查看权限（超级管理员）
    - 支持多条件筛选
    - 支持分页和排序
    """
    try:
        # 将ISO格式字符串转换为datetime对象
        from datetime import datetime
        start_dt = None
        end_dt = None
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="开始时间格式无效，请使用ISO格式"
                )
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="结束时间格式无效，请使用ISO格式"
                )
        
        # 调用DAO查询日志
        result = await user_logs_dao.search_logs(
            user_id=user_id,
            activity_id=activity_id,
            operation_type=operation_type,
            start_time=start_dt,
            end_time=end_dt,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )
        
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询日志失败: {str(e)}"
        )


@router.get(
    "/{log_id}",
    response_model=UserOperationLogInDB,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions(["user:list"])]
)
async def get_log_detail(
    log_id: int,
    request: Request
):
    """
    获取单条用户操作日志详情
    - 需要用户列表查看权限（超级管理员）
    """
    try:
        log = await user_logs_dao.get_by_id(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志不存在"
            )
        
        return log
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取日志失败: {str(e)}"
        )


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[requires_permissions(["user:list"])]
)
async def delete_log(
    log_id: int,
    request: Request
):
    """
    删除单条用户操作日志
    - 需要用户列表管理权限（超级管理员）
    """
    try:
        # 检查日志是否存在
        log = await user_logs_dao.get_by_id(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志不存在"
            )
        
        # 删除日志
        result = await user_logs_dao.delete(log_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除日志失败"
            )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除日志失败: {str(e)}"
        )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[requires_permissions(["user:list"])]
)
async def delete_logs_batch(
    request: Request,
    log_ids: str = Query(..., description="要删除的日志ID列表，逗号分隔")
):
    """
    批量删除用户操作日志
    - 需要用户列表管理权限（超级管理员）
    - log_ids: 逗号分隔的日志ID，例如：1,2,3
    """
    try:
        # 解析日志ID列表
        try:
            ids = [int(id_str.strip()) for id_str in log_ids.split(',') if id_str.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日志ID列表格式无效，请使用逗号分隔的整数"
            )
        
        if not ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日志ID列表不能为空"
            )
        
        # 删除每条日志
        from models.user_logs import UserOperationLogs
        deleted_count = 0
        for log_id in ids:
            # 检查日志是否存在
            log = await user_logs_dao.get_by_id(log_id)
            if log:
                result = await user_logs_dao.delete(log_id)
                if result:
                    deleted_count += 1
        
        # 如果没有删除任何日志，返回错误
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="没有找到要删除的日志"
            )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除日志失败: {str(e)}"
        )
