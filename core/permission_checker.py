"""
权限验证工具模块
提供权限验证相关的函数和依赖项
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from .middleware.auth_middleware import JWTAuthMiddleware
from dao.user_dao import UserDAO
from dao.role_dao import RoleDAO

oauth2_scheme = HTTPBearer()
user_dao = UserDAO()
role_dao = RoleDAO()

class PermissionChecker:
    """权限验证器类"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    async def __call__(self, token: str = Depends(JWTAuthMiddleware())):
        if not hasattr(token, 'credentials'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证"
            )
            
        # 获取用户角色及其权限
        try:
            from core.auth.jwt_handler import JWTHandler
            payload = JWTHandler.verify_token(token.credentials)
            user_id = int(payload.get("sub"))
            
            # 获取用户信息
            user = await user_dao.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在"
                )
                
            # 获取用户的所有角色
            user_roles = await user.roles.all()
            if not user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户没有任何角色"
                )
            
            # 检查每个角色的权限
            user_permissions = set()
            for role in user_roles:
                if role.is_active and role.permissions:
                    user_permissions.update(set(role.permissions))
            
            # 验证是否具有所需的所有权限
            missing_permissions = set(self.required_permissions) - user_permissions
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少所需权限: {', '.join(missing_permissions)}"
                )
                
            print(f"权限验证通过 - 用户ID: {user_id}, 角色: {[role.name for role in user_roles]}")
            return True
            
        except Exception as e:
            print(f"权限验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限验证失败: {str(e)}"
            )

def requires_permissions(permissions: List[str]):
    """
    权限验证装饰器
    :param permissions: 所需权限列表
    :return: 权限验证依赖项
    """
    return Depends(PermissionChecker(permissions))