from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from .users import UserBasicInfo
from .activities import ActivityInDB


class UserOperationLogBase(BaseModel):
    """用户操作日志基础模式"""
    operation_type: str = Field(
        ...,
        description="操作类型",
        pattern="^(view_activity|register_activity)$"
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="附加数据(JSON格式，用于扩展信息)",
        example={"duration": 120, "source": "search"}
    )


class UserOperationLogCreate(BaseModel):
    """创建用户操作日志模式"""
    activity_id: int = Field(..., description="活动ID")
    operation_type: str = Field(
        ...,
        description="操作类型",
        pattern="^(view_activity|register_activity)$"
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="附加数据(JSON格式，用于扩展信息)"
    )


class UserOperationLogUpdate(BaseModel):
    """更新用户操作日志模式"""
    extra_data: Optional[Dict[str, Any]] = Field(
        None,
        description="附加数据(JSON格式，用于扩展信息)"
    )


class UserOperationLogInDB(UserOperationLogBase):
    """数据库中的用户操作日志模式"""
    id: int
    created_at: datetime
    user_id: int = Field(..., description="用户ID")
    activity_id: int = Field(..., description="活动ID")

    class Config:
        from_attributes = True


class UserOperationLogDetail(UserOperationLogBase):
    """用户操作日志详细模式（含关联信息）"""
    id: int
    created_at: datetime
    user: UserBasicInfo = Field(..., description="操作用户")
    activity: ActivityInDB = Field(..., description="关联活动")

    class Config:
        from_attributes = True


class UserOperationLogWithActivity(UserOperationLogBase):
    """用户操作日志详细模式（包含活动信息）"""
    id: int
    created_at: datetime
    activity: ActivityInDB = Field(..., description="关联活动详细信息")

    class Config:
        from_attributes = True


class UserOperationLogList(BaseModel):
    """用户操作日志列表模式"""
    total: int = Field(..., description="总条数")
    items: List[UserOperationLogInDB] = Field(..., description="日志列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class UserOperationLogWithActivityList(BaseModel):
    """用户操作日志列表模式（包含活动详细信息）"""
    total: int = Field(..., description="总条数")
    items: List[UserOperationLogWithActivity] = Field(..., description="日志列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class UserOperationLogStats(BaseModel):
    """用户操作日志统计模式"""
    total_views: int = Field(..., description="总浏览次数")
    total_registrations: int = Field(..., description="总报名次数")
    unique_viewed_activities: int = Field(
        ...,
        description="浏览过的不同活动数量"
    )
    unique_registered_activities: int = Field(
        ...,
        description="报名过的不同活动数量"
    )
    last_operation_time: Optional[datetime] = Field(
        None,
        description="最后操作时间"
    )


class UserOperationLogSearch(BaseModel):
    """用户操作日志搜索参数模式"""
    user_id: Optional[int] = Field(None, description="用户ID")
    activity_id: Optional[int] = Field(None, description="活动ID")
    operation_type: Optional[str] = Field(
        None,
        description="操作类型",
        pattern="^(view_activity|register_activity)$"
    )
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    sort_by: Optional[str] = Field(
        None,
        pattern="^(-?created_at|-?operation_type)$",
        description="排序字段：前缀'-'表示倒序"
    )
    page: int = Field(1, gt=0, description="页码")
    page_size: int = Field(10, gt=0, le=100, description="每页数量")
