from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from schemas.activities import (
    ActivityCreate, ActivityInDB, ActivityStats, ActivityUpdate
)
from dao.activity_dao import ActivityDAO
from core.permission_checker import requires_permissions
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permissions import ACTIVITY_UPDATE, ACTIVITY_DELETE
from fastapi.security import HTTPBearer
from typing import List, Dict

router = APIRouter(
    prefix="/activities",
    tags=["活动"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

activity_dao = ActivityDAO()

@router.post(
    "/",
    response_model=ActivityInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[requires_permissions(["activity:publish"])]
)
async def create_activity(
    activity: ActivityCreate,
    request: Request
):
    """
    创建新活动
    - 需要活动发布权限
    - 验证请求数据
    - 保存到数据库
    """
    try:
        # 从请求状态中获取当前用户（发布者）信息
        publisher_id = request.state.user.id  # 通过 JWTAuthMiddleware 注入的用户信息

        # 创建活动
        created_activity = await activity_dao.create_activity(
            data=activity.model_dump(exclude={"publisher"}),
            publisher_id=publisher_id
        )
        
        return created_activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建活动失败: {str(e)}"
        )

@router.get(
    "/{activity_id}",
    response_model=Dict,
    status_code=status.HTTP_200_OK
)
async def get_activity_details(
    activity_id: int,
    request: Request
):
    """
    获取活动详情
    - 任何已登录用户可访问
    - 返回活动详细信息和统计数据
    """
    try:
        # 获取活动详情
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 增加浏览量
        await activity_dao.increment_views(activity_id)

        # 获取活动统计信息
        stats = await activity_dao.get_activity_stats(activity_id)

        # 组合返回数据
        activity_data = ActivityInDB.from_orm(activity).model_dump()
        return {
            "activity": activity_data,
            "stats": stats
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取活动详情失败: {str(e)}"
        )

@router.put(
    "/{activity_id}",
    response_model=ActivityInDB,
    status_code=status.HTTP_200_OK
)
async def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    request: Request
):
    """
    更新活动信息
    - 需要是活动发布者
    - 验证请求数据
    - 更新活动信息
    """
    try:
        # 获取活动信息
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 验证用户是否为活动发布者
        current_user_id = request.state.user.id
        if current_user_id != activity.publisher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以更新活动信息"
            )

        # 更新活动
        update_data = activity_update.model_dump(exclude_unset=True)
        if update_data:
            for key, value in update_data.items():
                setattr(activity, key, value)
            await activity.save()
            # 重新获取更新后的活动信息
            activity = await activity_dao.get_activity_with_stats(activity_id)

        return activity

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新活动失败: {str(e)}"
        )

@router.delete(
    "/{activity_id}",
    response_model=Dict,
    status_code=status.HTTP_200_OK
)
async def delete_activity(
    activity_id: int,
    request: Request
):
    """
    删除活动（软删除）
    - 需要是活动发布者
    - 执行软删除操作
    - 返回删除结果信息
    """
    try:
        # 获取活动信息
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 验证用户是否为活动发布者
        current_user_id = request.state.user.id
        if current_user_id != activity.publisher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以删除活动"
            )

        # 执行软删除
        success = await activity_dao.soft_delete(activity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除活动失败"
            )

        # 返回成功响应
        return {
            "success": True,
            "message": f"活动 '{activity.title}' 已成功删除",
            "activity_id": activity_id
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除活动失败: {str(e)}"
        )

@router.patch(
    "/{activity_id}/status",
    response_model=ActivityInDB,
    status_code=status.HTTP_200_OK
)
async def update_activity_status(
    request: Request,
    activity_id: int,
    status: str = Query(
        ...,
        description="活动状态",
        regex="^(draft|published|ongoing|ended|cancelled)$"
    )
):
    """
    更新活动状态
    - 需要是活动发布者
    - 更新活动状态
    
    可用状态:
    - draft: 草稿
    - published: 已发布
    - ongoing: 进行中
    - ended: 已结束
    - cancelled: 已取消
    """
    try:
        # 获取活动信息
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 验证用户是否为活动发布者
        current_user_id = request.state.user.id
        if current_user_id != activity.publisher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以更新活动状态"
            )

        # 更新状态
        updated_activity = await activity_dao.update_activity_status(activity_id, status)
        if not updated_activity:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新活动状态失败"
            )

        # 重新获取完整的活动信息
        return await activity_dao.get_activity_with_stats(activity_id)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新活动状态失败: {str(e)}"
        )