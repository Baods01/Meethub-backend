from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.registrations import (
    RegistrationCreate,
    RegistrationInDB,
    RegistrationList,
    RegistrationSearch
)
from schemas.activities import ActivityInDB
from dao.registration_dao import RegistrationDAO
from dao.activity_dao import ActivityDAO
from core.permission_checker import requires_permissions
from core.middleware.auth_middleware import JWTAuthMiddleware
from typing import List

router = APIRouter(
    prefix="/registrations",
    tags=["报名"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

registration_dao = RegistrationDAO()
activity_dao = ActivityDAO()

@router.post(
    "/",
    response_model=RegistrationInDB,
    status_code=status.HTTP_201_CREATED
)
async def create_registration(
    registration: RegistrationCreate,
    request: Request
):
    """
    创建活动报名
    - 需要登录用户
    - 验证活动状态和报名条件
    - 创建报名记录
    """
    try:
        # 获取当前用户信息
        participant_id = request.state.user.id

        # 检查活动是否存在且可报名
        activity = await activity_dao.get_activity_with_stats(registration.activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        if activity.status != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="活动当前状态不可报名"
            )

        if activity.current_participants >= activity.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="活动报名人数已满"
            )

        # 创建报名记录
        registration_data = registration.model_dump(exclude={"activity_id"})
        created_registration = await registration_dao.create_registration(
            activity_id=registration.activity_id,
            participant_id=participant_id,
            data=registration_data
        )

        # 更新活动当前报名人数
        await activity_dao.update_participants_count(registration.activity_id, increment=True)

        return created_registration

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建报名失败: {str(e)}"
        )

@router.get(
    "/my",
    response_model=RegistrationList
)
async def get_my_registrations(
    request: Request,
    status: str = None,
    page: int = 1,
    page_size: int = 10
):
    """
    获取个人报名记录
    - 需要登录用户
    - 支持按状态筛选
    - 支持分页
    """
    try:
        user_id = request.state.user.id
        registrations = await registration_dao.get_user_registrations(
            user_id=user_id,
            status=status,
            page=page,
            page_size=page_size
        )
        return registrations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报名记录失败: {str(e)}"
        )

@router.get(
    "/activity/{activity_id}",
    response_model=RegistrationList
)
async def get_activity_registrations(
    activity_id: int,
    request: Request,
    status: str = None,
    page: int = 1,
    page_size: int = 10
):
    """
    获取活动报名记录
    - 需要活动发布者权限
    - 支持按状态筛选
    - 支持分页
    """
    try:
        # 验证用户是否为活动发布者
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        if activity.publisher.id != request.state.user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以查看报名记录"
            )

        registrations = await registration_dao.get_activity_registrations(
            activity_id=activity_id,
            status=status,
            page=page,
            page_size=page_size
        )
        return registrations
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取活动报名记录失败: {str(e)}"
        )

@router.get(
    "/{registration_id}",
    response_model=RegistrationInDB
)
async def get_registration_detail(
    registration_id: int,
    request: Request
):
    """
    获取报名详情
    - 需要是报名者本人或活动发布者
    """
    try:
        # 获取报名详情
        registration = await registration_dao.get_registration_detail(registration_id)
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报名记录不存在"
            )

        # 验证权限
        current_user_id = request.state.user.id
        if (current_user_id != registration.participant.id and 
            current_user_id != registration.activity.publisher.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有报名者本人或活动发布者可以查看报名详情"
            )

        return registration
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报名详情失败: {str(e)}"
        )