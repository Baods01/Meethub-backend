from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.activities import ActivityCreate, ActivityInDB, ActivityStats
from dao.activity_dao import ActivityDAO
from core.permission_checker import requires_permissions
from core.middleware.auth_middleware import JWTAuthMiddleware
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