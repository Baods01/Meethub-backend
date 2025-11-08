from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.users import UserResponse, UserBasicUpdate
from dao.user_dao import UserDAO
from core.middleware.auth_middleware import JWTAuthMiddleware

router = APIRouter(
    prefix="/users",
    tags=["用户"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

# 创建UserDAO实例
user_dao = UserDAO()

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    request: Request,
    user_update: UserBasicUpdate
):
    """
    更新当前用户的基本信息
    用户只能修改自己的基本信息（昵称、个人简介、个性属性、头像）
    """
    # 从请求状态中获取当前用户
    current_user = request.state.user
    
    # 构建更新数据字典，只包含允许修改的字段
    update_data = user_update.dict(exclude_unset=True)
    
    try:
        # 更新用户信息
        updated_user = await user_dao.update_user(current_user.id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )
        
        # 获取用户角色信息
        roles = await updated_user.roles.all()
        
        # 构建响应数据
        user_dict = {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "phone": updated_user.phone,
            "avatar": updated_user.avatar,
            "nickname": updated_user.nickname,
            "bio": updated_user.bio,
            "profile_attributes": updated_user.profile_attributes,
            "is_active": updated_user.is_active,
            "is_verified": updated_user.is_verified,
            "created_at": updated_user.created_at,
            "updated_at": updated_user.updated_at,
            "last_login": updated_user.last_login,
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
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息时发生错误：{str(e)}"
        )