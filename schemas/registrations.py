from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .users import UserBasicInfo
from .activities import ActivityInDB


class RegistrationBase(BaseModel):
    """报名基础模式"""
    comment: Optional[str] = Field(None, description="报名备注")
    additional_info: Optional[Dict] = Field(default={}, description="附加信息")


class RegistrationCreate(RegistrationBase):
    """创建报名模式"""
    activity_id: int = Field(..., description="活动ID")


class RegistrationUpdate(BaseModel):
    """更新报名模式"""
    status: Optional[str] = Field(
        None,
        description="报名状态",
        pattern="^(pending|approved|rejected|cancelled)$"
    )
    comment: Optional[str] = None
    additional_info: Optional[Dict] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    feedback: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

    @validator('check_out_time')
    def validate_check_out_time(cls, v, values):
        if v and 'check_in_time' in values and values['check_in_time'] and v <= values['check_in_time']:
            raise ValueError('签退时间必须晚于签到时间')
        return v


class RegistrationInDB(RegistrationBase):
    """数据库中的报名模式"""
    id: int
    registration_time: datetime
    status: str
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    feedback: Optional[str]
    rating: Optional[int]
    created_at: datetime
    updated_at: datetime
    participant: UserBasicInfo
    activity: ActivityInDB

    class Config:
        from_attributes = True


class RegistrationList(BaseModel):
    """报名列表模式"""
    total: int
    items: List[RegistrationInDB]
    page: int
    page_size: int


class RegistrationStats(BaseModel):
    """报名统计模式"""
    total_registrations: int
    approved_count: int
    pending_count: int
    rejected_count: int
    cancelled_count: int
    check_in_rate: float
    average_rating: Optional[float]


class RegistrationSearch(BaseModel):
    """报名搜索参数模式"""
    activity_id: Optional[int] = None
    status: Optional[str] = Field(
        None,
        pattern="^(pending|approved|rejected|cancelled)$"
    )
    registration_time_range: Optional[Dict[str, datetime]] = None
    sort_by: Optional[str] = Field(
        None,
        pattern="^(registration_time|status|rating)$"
    )
    page: int = Field(1, gt=0)
    page_size: int = Field(10, gt=0, le=100)