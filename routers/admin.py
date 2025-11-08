from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.users import UserResponse
from dao.user_dao import UserDAO
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permission_checker import requires_permissions
from core.permissions import USER_LIST, USER_READ

router = APIRouter(
    prefix="/admin",
    tags=["管理员"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

# 创建UserDAO实例
user_dao = UserDAO()

@router.get("/users/ids", response_model=List[dict])
async def get_all_user_ids(
    _=requires_permissions([USER_LIST])
):
    """
    获取所有用户的id和用户名信息
    需要USER_LIST权限
    """
    try:
        users = await user_dao.get_all()
        return [{"id": user.id, "username": user.username} for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败：{str(e)}"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    _=requires_permissions([USER_READ])
):
    """
    获取指定ID用户的详细信息
    需要USER_READ权限
    """
    user = await user_dao.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到ID为{user_id}的用户"
        )
    
    # 获取用户角色信息
    roles = await user.roles.all()
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "nickname": user.nickname,
        "bio": user.bio,
        "profile_attributes": user.profile_attributes,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "roles": [{
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "permissions": role.permissions,
            "is_active": role.is_active,
            "created_at": role.created_at,
            "updated_at": role.updated_at
        } for role in roles]
    }
    return user_dict