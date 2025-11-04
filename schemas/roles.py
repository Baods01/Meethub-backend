from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    code: str = Field(..., min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: Optional[list[str]] = Field(None, description="权限列表")
    is_active: bool = Field(True, description="是否激活")


class RoleCreate(RoleBase):
    """创建角色请求模型"""
    pass


class RoleUpdate(BaseModel):
    """更新角色请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: Optional[list[str]] = Field(None, description="权限列表")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int = Field(..., description="角色ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True