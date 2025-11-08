from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from schemas.users import UserResponse, UserUpdate
from dao.user_dao import UserDAO
from dao.role_dao import RoleDAO
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permission_checker import requires_permissions
from core.permissions import USER_LIST, USER_READ, USER_UPDATE, USER_ROLES

router = APIRouter(
    prefix="/admin",
    tags=["管理员"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

# 创建UserDAO实例
user_dao = UserDAO()
role_dao = RoleDAO()

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

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_details(
    user_id: int,
    user_update: UserUpdate,
    role_ids: Optional[List[int]] = None,
    _=requires_permissions([USER_UPDATE, USER_ROLES])
):
    """
    修改指定ID用户的基本信息和角色
    需要USER_UPDATE和USER_ROLES权限
    :param user_id: 用户ID
    :param user_update: 用户更新信息
    :param role_ids: 角色ID列表，可选
    :return: 更新后的用户信息
    """
    # 获取用户
    user = await user_dao.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到ID为{user_id}的用户"
        )
    
    # 验证用户名唯一性
    if user_update.username and user_update.username != user.username:
        existing_user = await user_dao.get_user_by_username(user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
            
    # 验证邮箱唯一性
    if user_update.email and user_update.email != user.email:
        existing_user = await user_dao.get_user_by_email(user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
            
    # 验证手机号唯一性
    if user_update.phone and user_update.phone != user.phone:
        existing_user = await user_dao.get_user_by_phone(user_update.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已存在"
            )
    
    # 更新用户基本信息
    try:
        update_data = user_update.dict(exclude_unset=True)
        user = await user_dao.update_user(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息时发生错误：{str(e)}"
        )
    
    # 如果提供了角色ID列表，更新用户角色
    if role_ids is not None:
        try:
            # 验证所有角色是否存在且处于激活状态
            roles = await role_dao.get_roles_by_ids(role_ids)
            if len(roles) != len(role_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部分角色ID无效"
                )
            
            inactive_roles = [role.id for role in roles if not role.is_active]
            if inactive_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色 {inactive_roles} 未激活"
                )
            
            # 清除现有角色关系
            await user.roles.clear()
            # 添加新的角色关系
            await user.roles.add(*roles)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新用户角色时发生错误：{str(e)}"
            )
    
    # 获取更新后的用户完整信息
    user = await user_dao.get_by_id(user_id)
    roles = await user.roles.all()
    
    # 构建响应数据
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