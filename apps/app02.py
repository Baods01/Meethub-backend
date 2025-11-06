from fastapi import APIRouter, Request, Depends, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.middleware.auth_middleware import JWTAuthMiddleware
from typing import Optional
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/test", tags=["测试"])

# 创建安全校验器实例
oauth2_scheme = HTTPBearer(
    scheme_name="JWT认证",
    description="输入格式：Bearer your-token",
    auto_error=True
)

@router.get(
    "/auth-check",
    description="测试JWT认证",
    summary="验证JWT令牌",
    response_description="认证状态和用户信息"
)
async def check_auth(
    request: Request,
    authorization: Optional[str] = Header(None),
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """
    测试认证中间件的路由
    :param request: 请求对象
    :param token: JWT凭证
    :return: 认证状态
    """
    try:
        # 使用中间件验证 token
        auth_middleware = JWTAuthMiddleware()
        await auth_middleware(request)
        
        if not hasattr(request.state, 'user'):
            return {
                "status": "error",
                "message": "认证失败：用户信息未找到"
            }

        return {
            "status": "success",
            "message": "认证通过",
            "user_id": request.state.user.id,
            "username": request.state.user.username,
            "token_type": token.scheme,
            "token": token.credentials
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"认证失败：{str(e)}"
        }