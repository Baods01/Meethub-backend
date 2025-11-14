"""
推荐系统数据模型
提供推荐接口所需的所有数据结构
"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from .activities import ActivityInDB


class RecommendationScoreBreakdown(BaseModel):
    """推荐分数分解模型"""
    content_filter_score: float = Field(
        default=0.0,
        description="内容过滤分数（用户标签匹配度）"
    )
    hotness_score: float = Field(
        default=0.0,
        description="热度分数（浏览量、报名人数）"
    )
    collaborative_score: float = Field(
        default=0.0,
        description="协同过滤分数（相似用户行为）"
    )
    freshness_score: float = Field(
        default=0.0,
        description="新鲜度分数（时间衰减）"
    )
    final_score: float = Field(
        default=0.0,
        description="最终综合推荐分数"
    )


class RecommendedActivity(BaseModel):
    """推荐活动项模型"""
    activity: ActivityInDB = Field(description="活动详情")
    recommendation_score: float = Field(
        description="推荐分数（0-100）"
    )
    reasons: List[str] = Field(
        default_factory=list,
        description="推荐理由列表"
    )
    score_breakdown: RecommendationScoreBreakdown = Field(
        description="各层分数分解"
    )

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    success: bool = Field(
        default=True,
        description="操作是否成功"
    )
    user_id: int = Field(
        description="推荐的用户ID"
    )
    recommendations: List[RecommendedActivity] = Field(
        description="推荐的活动列表"
    )
    total_count: int = Field(
        description="推荐活动总数"
    )
    parameters_used: Dict = Field(
        description="使用的推荐参数"
    )
    message: str = Field(
        default="推荐成功",
        description="响应消息"
    )


class RecommendationRequest(BaseModel):
    """推荐请求模型"""
    count: int = Field(
        default=5,
        gt=0,
        le=20,
        description="推荐活动数量（1-20）"
    )
    exclude_viewed: bool = Field(
        default=True,
        description="是否排除已浏览的活动"
    )
    exclude_registered: bool = Field(
        default=True,
        description="是否排除已报名的活动"
    )
    exclude_ended: bool = Field(
        default=True,
        description="是否排除已结束的活动"
    )

    class Config:
        from_attributes = True


class RecommendationDebugRequest(BaseModel):
    """推荐调试请求模型（带参数调整）"""
    count: int = Field(
        default=5,
        gt=0,
        le=20,
        description="推荐活动数量（1-20）"
    )
    exclude_viewed: bool = Field(
        default=True,
        description="是否排除已浏览的活动"
    )
    exclude_registered: bool = Field(
        default=True,
        description="是否排除已报名的活动"
    )
    exclude_ended: bool = Field(
        default=True,
        description="是否排除已结束的活动"
    )
    layer_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="各推荐层的权重配置 {'content_filter': 0.35, 'hotness': 0.20, 'collaborative': 0.25, 'freshness': 0.20}"
    )
    content_match_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="内容匹配最低阈值（0.0-1.0）"
    )
    collaborative_users_limit: Optional[int] = Field(
        default=None,
        gt=0,
        description="协同过滤参考用户数"
    )
    freshness_half_life: Optional[int] = Field(
        default=None,
        gt=0,
        description="新鲜度半衰期天数"
    )

    class Config:
        from_attributes = True


class UserPreferenceProfile(BaseModel):
    """用户偏好档案模型"""
    user_id: int = Field(description="用户ID")
    interests: List[str] = Field(
        default_factory=list,
        description="用户兴趣标签"
    )
    grade: Optional[str] = Field(
        default=None,
        description="用户年级"
    )
    major: Optional[str] = Field(
        default=None,
        description="用户专业"
    )
    college: Optional[str] = Field(
        default=None,
        description="用户学院"
    )
    viewed_activities_count: int = Field(
        default=0,
        description="已浏览活动数"
    )
    registered_activities_count: int = Field(
        default=0,
        description="已报名活动数"
    )
    behavior_intensity: str = Field(
        default="moderate",
        description="行为强度（low, moderate, high）"
    )


class RecommendationDebugResponse(BaseModel):
    """推荐调试响应模型（详细信息）"""
    success: bool = Field(
        default=True,
        description="操作是否成功"
    )
    user_id: int = Field(
        description="推荐的用户ID"
    )
    user_profile: UserPreferenceProfile = Field(
        description="用户偏好档案"
    )
    recommendations: List[RecommendedActivity] = Field(
        description="推荐的活动列表"
    )
    total_count: int = Field(
        description="推荐活动总数"
    )
    parameters_used: Dict = Field(
        description="使用的推荐参数"
    )
    debug_info: Dict = Field(
        default_factory=dict,
        description="调试信息（包含各步骤的中间数据）"
    )
    message: str = Field(
        default="推荐成功",
        description="响应消息"
    )
