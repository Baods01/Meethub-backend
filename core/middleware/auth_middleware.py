from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.auth.jwt_handler import JWTHandler
from typing import Optional
from dao.user_dao import UserDAO
import logging

logger = logging.getLogger(__name__)

class JWTAuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTAuthMiddleware, self).__init__(auto_error=auto_error)
        self.user_dao = UserDAO()

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        """
        验证 JWT 令牌并注入用户信息
        :param request: FastAPI 请求对象
        :return: 认证凭证
        """
        # 检查是否是公开路由
        if self._is_public_path(request.url.path):
            return None

        # 获取凭证
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证令牌无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            # 验证令牌
            payload = JWTHandler.verify_token(credentials.credentials)
            user_id = int(payload.get("sub"))
            
            # 获取用户信息
            user = await self.user_dao.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                )
                
            # 将用户信息注入请求状态
            request.state.user = user
            return credentials
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌验证失败",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def _is_public_path(path: str) -> bool:
        """
        检查路径是否为公开访问
        :param path: 请求路径
        :return: 是否为公开路径
        """
        public_paths = {
            "/auth/login",
            "/auth/reset-password/verify",
            "/auth/reset-password",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        return path in public_paths