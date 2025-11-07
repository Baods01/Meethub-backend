from fastapi import APIRouter, Request, Depends
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permission_checker import requires_permissions
from core.permissions import *
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/test", tags=["测试"])

@router.get(
    "/auth-check",
    description="测试JWT认证",
    summary="验证JWT令牌",
    response_description="认证状态和用户信息"
)
async def check_auth(
    request: Request,
    authorized: bool = Depends(JWTAuthMiddleware())
):
    """
    测试认证中间件的路由
    :param request: 请求对象
    :param token: JWT凭证
    :return: 认证状态
    """
    try:
        if not hasattr(request.state, 'user'):
            return {
                "status": "error",
                "message": "认证失败：用户信息未找到"
            }

        return {
            "status": "success",
            "message": "认证通过",
            "user_id": request.state.user.id,
            "username": request.state.user.username
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"认证失败：{str(e)}"
        }

@router.get(
    "/admin-check",
    description="测试管理员权限",
    summary="验证管理员权限",
    response_description="权限验证结果"
)
async def check_admin_permissions(
    authorized: bool = requires_permissions([
        SYSTEM_SETTINGS,
        USER_CREATE,
        ROLE_CREATE
    ])
):
    """
    测试超级管理员权限的路由
    """
    return {
        "status": "success",
        "message": "超级管理员权限验证通过",
        "permissions_checked": [
            SYSTEM_SETTINGS,
            USER_CREATE,
            ROLE_CREATE
        ]
    }

@router.get(
    "/organizer-check",
    description="测试组织者权限",
    summary="验证组织者权限",
    response_description="权限验证结果"
)
async def check_organizer_permissions(
    authorized: bool = requires_permissions([
        ACTIVITY_CREATE,
        ACTIVITY_UPDATE,
        ENROLLMENT_APPROVE
    ])
):
    """
    测试活动组织者权限的路由
    """
    return {
        "status": "success",
        "message": "活动组织者权限验证通过",
        "permissions_checked": [
            ACTIVITY_CREATE,
            ACTIVITY_UPDATE,
            ENROLLMENT_APPROVE
        ]
    }

@router.get(
    "/user-check",
    description="测试普通用户权限",
    summary="验证普通用户权限",
    response_description="权限验证结果"
)
async def check_user_permissions(
    authorized: bool = requires_permissions([
        ACTIVITY_READ,
        ENROLLMENT_CREATE,
        AI_ASSISTANT_USE
    ])
):
    """
    测试普通用户权限的路由
    """
    return {
        "status": "success",
        "message": "普通用户权限验证通过",
        "permissions_checked": [
            ACTIVITY_READ,
            ENROLLMENT_CREATE,
            AI_ASSISTANT_USE
        ]
    }