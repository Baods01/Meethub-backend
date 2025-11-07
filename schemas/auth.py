from pydantic import BaseModel, EmailStr, Field, constr

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

class RefreshTokenResponse(Token):
    """刷新令牌响应模式"""
    pass

class PasswordResetVerify(BaseModel):
    """密码重置验证请求模式"""
    email: str = Field(..., description="用户邮箱")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")

class PasswordReset(BaseModel):
    """密码重置请求模式"""
    email: str = Field(..., description="用户邮箱")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=64, 
        description="新密码，至少8个字符",
        examples=["your-new-strong-password"]
    )