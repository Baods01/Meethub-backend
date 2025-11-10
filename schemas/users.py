from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, constr
from datetime import datetime
from .roles import RoleResponse


class UserBasicInfo(BaseModel):
    """用户基本信息（用于其他模型的嵌套）"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    profile_attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="用户个性属性",
        example={
            "college": "计算机学院",
            "major": "软件工程",
            "hobby": ["篮球", "编程", "音乐"],
            "gender": "male",
            "grade": "2023级"
        }
    )
    avatar: Optional[str] = Field(None, description="头像URL")
    is_active: bool = Field(True, description="是否激活")


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="密码，至少8个字符",
        examples=["your-strong-password"]
    )
    email: str = Field(..., description="邮箱")  # 创建时邮箱必填


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_active: Optional[bool] = Field(None, description="是否激活")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=64,
        description="密码，至少8个字符",
        examples=["your-strong-password"]
    )


class UserProfileUpdate(BaseModel):
    """更新用户个性属性请求模型"""
    profile_attributes: Dict[str, Any] = Field(
        ...,
        description="用户个性属性",
        example={
            "college": "计算机学院",
            "major": "软件工程",
            "hobby": ["篮球", "编程", "音乐"],
            "gender": "male",
            "grade": "2023级"
        }
    )

class UserBasicUpdate(BaseModel):
    """更新用户基本信息请求模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    profile_attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="用户个性属性",
        example={
            "college": "计算机学院",
            "major": "软件工程",
            "hobby": ["篮球", "编程", "音乐"],
            "gender": "male",
            "grade": "2023级"
        }
    )
    avatar: Optional[str] = Field(None, description="头像URL")

class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    is_verified: bool = Field(..., description="是否验证")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    roles: List[RoleResponse] = Field(default_factory=list, description="用户角色列表")

    class Config:
        from_attributes = True