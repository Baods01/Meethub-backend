from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.activities import ActivityCreate, ActivityInDB
from dao.activity_dao import ActivityDAO
from core.permission_checker import requires_permissions
from core.middleware.auth_middleware import JWTAuthMiddleware
from fastapi.security import HTTPBearer
from typing import List

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