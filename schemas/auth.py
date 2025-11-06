from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """登录请求模式"""
    username: str
    password: str

class Token(BaseModel):
    """令牌响应模式"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模式"""
    user_id: int = None