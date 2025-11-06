from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import LoginRequest, Token
from dao.user_dao import UserDAO
from core.auth.jwt_handler import JWTHandler
import bcrypt

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    :param form_data: 表单数据，包含username和password
    :return: JWT令牌
    """
    # 获取用户数据访问对象
    user_dao = UserDAO()
    
    # 查询用户
    user = await user_dao.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    # 处理密码长度限制
    password_bytes = form_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # 验证密码
    stored_password = user.password.encode('utf-8')
    if not bcrypt.checkpw(password_bytes, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成JWT令牌
    token_data = JWTHandler.create_token_response(user.id)
    
    return Token(**token_data)