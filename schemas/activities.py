from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .users import UserBasicInfo


class ActivityBase(BaseModel):
    """活动基础模式"""
    title: str = Field(default="华南农业大学活动", description="活动名称", min_length=1, max_length=100)
    description: str = Field(default="这是一个华南农业大学的活动", description="活动简介")
    cover_image: str = Field(default=None, description="封面图片URL", max_length=255)
    location: str = Field(default="华南农业大学", description="活动地点", max_length=255)
    start_time: datetime = Field(default="2025-11-20T00:37:32.249Z", description="活动开始时间")
    end_time: datetime = Field(default="2025-11-30T00:37:32.249Z", description="活动结束时间")
    max_participants: int = Field(default= 100, description="招募人数上限", gt=0)
    tags: List[str] = Field(default=[], description="活动标签")
    target_audience: Dict = Field(
        default={
            "Targeted_people":["大一","大二"],
            "Activity_class":["就业创业","学术调研"],
            }, 
        description="面向人群(专业/年级)"
        )
    benefits: Dict = Field(
        default={"benefit" : ["综测加分","志愿时","其他"]}, 
        description="活动收益(志愿时/综测等)"
        )

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """验证结束时间必须晚于开始时间"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class ActivityCreate(ActivityBase):
    """创建活动模式"""
    pass


class ActivityUpdate(BaseModel):
    """更新活动模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    target_audience: Optional[Dict] = None
    benefits: Optional[Dict] = None
    status: Optional[str] = Field(
        None,
        description="活动状态",
        pattern="^(draft|published|ongoing|ended|cancelled)$"
    )

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class ActivityInDB(ActivityBase):
    """数据库中的活动模式"""
    id: int
    current_participants: int = 0
    status: str
    views_count: int = 0
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    publisher: UserBasicInfo

    class Config:
        from_attributes = True


class ActivityList(BaseModel):
    """活动列表模式"""
    total: int
    items: List[ActivityInDB]
    page: int
    page_size: int


class ActivityStats(BaseModel):
    """活动统计模式"""
    total_participants: int
    completion_rate: float
    average_rating: Optional[float]
    total_views: int


class ActivitySearch(BaseModel):
    """活动搜索参数模式"""
    keyword: Optional[str] = None
    benefits: Optional[List[str]] = None
    audience: Optional[Dict] = None
    categories: Optional[List[str]] = None
    time_range: Optional[Dict[str, datetime]] = None
    sort_by: Optional[str] = Field(
        None,
        pattern="^(created_at|start_time|views_count|current_participants)$"
    )
    page: int = Field(1, gt=0)
    page_size: int = Field(10, gt=0, le=100)