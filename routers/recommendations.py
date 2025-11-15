"""
推荐系统路由
提供推荐功能接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional, Dict
from datetime import datetime, timedelta
import random
from schemas.recommendations import (
    RecommendationRequest, RecommendationResponse,
    RecommendationDebugRequest, RecommendationDebugResponse,
    RecommendedActivity, RecommendationScoreBreakdown,
    UserPreferenceProfile
)
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.middleware.logging_middleware import operation_logger
from core.permission_checker import requires_permissions
from core.permissions import ACTIVITY_READ
from dao.recommendation_dao import RecommendationDAO
from core.recommendation.recommendation_engine import RecommendationEngine
from models.users import Users
from models.activities import Activities


router = APIRouter(
    prefix="/recommendations",
    tags=["推荐"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

recommendation_dao = RecommendationDAO()
recommendation_engine = RecommendationEngine()


@router.post(
    "/for-me",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions([ACTIVITY_READ])]
)
async def get_recommendations_for_current_user(
    request: Request,
    rec_request: RecommendationRequest
):
    """
    为当前用户推荐活动
    
    此接口使用推荐引擎的默认参数为当前用户生成个性化活动推荐。
    
    Args:
        rec_request: 推荐请求参数
            - count: 推荐活动数量（默认5）
            - exclude_viewed: 是否排除已浏览活动（默认true）
            - exclude_registered: 是否排除已报名活动（默认true）
            - exclude_ended: 是否排除已结束活动（默认true）
    
    Returns:
        RecommendationResponse: 包含推荐活动列表和推荐理由
    
    Raises:
        HTTPException: 当用户不存在或推荐失败时
    """
    try:
        # 从请求获取当前用户ID
        user_id = request.state.user.id
        
        # 获取用户信息
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 调用推荐引擎获取推荐
        recommendations = await recommendation_engine.recommend_activities(
            user_id=user_id,
            count=rec_request.count
        )
        
        # 根据请求参数过滤和调整活动分数
        if rec_request.exclude_viewed or rec_request.exclude_registered or rec_request.exclude_ended:
            adjusted_recommendations = await _filter_recommendations(
                user_id=user_id,
                recommendations=recommendations,
                exclude_viewed=rec_request.exclude_viewed,
                exclude_registered=rec_request.exclude_registered,
                exclude_ended=rec_request.exclude_ended
            )
            
            # 在调整分数后，需要重新排序
            adjusted_recommendations.sort(
                key=lambda x: x['recommendation_score'],
                reverse=True
            )
            filtered_recommendations = adjusted_recommendations
        else:
            filtered_recommendations = recommendations
        
        # 引入随机性机制：添加随机噪声到分数，使推荐多样化
        filtered_recommendations = _add_randomness_to_scores(filtered_recommendations)
        
        # 限制返回数量
        filtered_recommendations = filtered_recommendations[:rec_request.count]
        
        # 构建响应
        recommended_items = []
        for rec in filtered_recommendations:
            # 获取完整的活动信息
            activity = await Activities.get_or_none(id=rec['activity_id']).prefetch_related('publisher')
            if activity:
                rec_item = RecommendedActivity(
                    activity=activity,
                    recommendation_score=rec.get('recommendation_score', 0),
                    reasons=rec.get('reasons', []),
                    score_breakdown=RecommendationScoreBreakdown(
                        content_filter_score=rec.get('score_breakdown', {}).get('content_filter', 0),
                        hotness_score=rec.get('score_breakdown', {}).get('hotness', 0),
                        collaborative_score=rec.get('score_breakdown', {}).get('collaborative', 0),
                        freshness_score=rec.get('score_breakdown', {}).get('freshness', 0),
                        final_score=rec.get('recommendation_score', 0)
                    )
                )
                recommended_items.append(rec_item)
                
                # 记录推荐的活动到日志中间件（模拟用户浏览）
                await operation_logger.log_activity_view(
                    request,
                    activity.id,
                    extra_data={'source': 'recommendation'}
                )
        
        return RecommendationResponse(
            success=True,
            user_id=user_id,
            recommendations=recommended_items,
            total_count=len(recommended_items),
            parameters_used={
                'count': rec_request.count,
                'exclude_viewed': rec_request.exclude_viewed,
                'exclude_registered': rec_request.exclude_registered,
                'exclude_ended': rec_request.exclude_ended
            },
            message="推荐成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推荐失败: {str(e)}"
        )


@router.post(
    "/debug",
    response_model=RecommendationDebugResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions([ACTIVITY_READ])]
)
async def get_recommendations_with_debug(
    request: Request,
    debug_request: RecommendationDebugRequest
):
    """
    为当前用户推荐活动（带调试信息和参数调整）
    
    此接口用于调试和优化推荐算法参数。支持自定义推荐层权重、
    内容匹配阈值、协同过滤参考用户数等参数。
    
    Args:
        debug_request: 调试推荐请求参数
            - count: 推荐活动数量（1-20）
            - exclude_viewed: 是否排除已浏览活动
            - exclude_registered: 是否排除已报名活动
            - exclude_ended: 是否排除已结束活动
            - layer_weights: 各推荐层的权重配置
            - content_match_threshold: 内容匹配最低阈值
            - collaborative_users_limit: 协同过滤参考用户数
            - freshness_half_life: 新鲜度半衰期天数
    
    Returns:
        RecommendationDebugResponse: 包含详细的推荐信息和调试数据
    
    Raises:
        HTTPException: 当用户不存在或推荐失败时
    """
    try:
        # 从请求获取当前用户ID
        user_id = request.state.user.id
        
        # 获取用户信息
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 构建推荐参数
        recommendation_kwargs = {}
        if debug_request.content_match_threshold is not None:
            recommendation_kwargs['content_match_threshold'] = debug_request.content_match_threshold
        if debug_request.collaborative_users_limit is not None:
            recommendation_kwargs['collaborative_users_limit'] = debug_request.collaborative_users_limit
        if debug_request.freshness_half_life is not None:
            recommendation_kwargs['freshness_half_life'] = debug_request.freshness_half_life
        
        # 调用推荐引擎获取推荐
        recommendations = await recommendation_engine.recommend_activities(
            user_id=user_id,
            count=debug_request.count,
            layer_weights=debug_request.layer_weights,
            **recommendation_kwargs
        )
        
        # 根据请求参数过滤和调整活动分数
        if debug_request.exclude_viewed or debug_request.exclude_registered or debug_request.exclude_ended:
            adjusted_recommendations = await _filter_recommendations(
                user_id=user_id,
                recommendations=recommendations,
                exclude_viewed=debug_request.exclude_viewed,
                exclude_registered=debug_request.exclude_registered,
                exclude_ended=debug_request.exclude_ended
            )
            
            # 在调整分数后，需要重新排序
            adjusted_recommendations.sort(
                key=lambda x: x['recommendation_score'],
                reverse=True
            )
            filtered_recommendations = adjusted_recommendations
        else:
            filtered_recommendations = recommendations
        
        # 引入随机性机制：添加随机噪声到分数，使推荐多样化
        filtered_recommendations = _add_randomness_to_scores(filtered_recommendations)
        
        # 限制返回数量
        filtered_recommendations = filtered_recommendations[:debug_request.count]
        
        # 获取用户偏好档案
        user_profile = await _build_user_preference_profile(user_id)
        
        # 构建响应
        recommended_items = []
        for rec in filtered_recommendations:
            # 获取完整的活动信息
            activity = await Activities.get_or_none(id=rec['activity_id']).prefetch_related('publisher')
            if activity:
                rec_item = RecommendedActivity(
                    activity=activity,
                    recommendation_score=rec.get('recommendation_score', 0),
                    reasons=rec.get('reasons', []),
                    score_breakdown=RecommendationScoreBreakdown(
                        content_filter_score=rec.get('score_breakdown', {}).get('content_filter', 0),
                        hotness_score=rec.get('score_breakdown', {}).get('hotness', 0),
                        collaborative_score=rec.get('score_breakdown', {}).get('collaborative', 0),
                        freshness_score=rec.get('score_breakdown', {}).get('freshness', 0),
                        final_score=rec.get('recommendation_score', 0)
                    )
                )
                recommended_items.append(rec_item)
                
                # 记录推荐的活动到日志中间件（模拟用户浏览）
                await operation_logger.log_activity_view(
                    request,
                    activity.id,
                    extra_data={'source': 'recommendation_debug'}
                )
        
        # 构建调试信息
        debug_info = {
            'layer_weights': debug_request.layer_weights or _get_default_weights(),
            'content_match_threshold': debug_request.content_match_threshold or 0.1,
            'collaborative_users_limit': debug_request.collaborative_users_limit or 5,
            'freshness_half_life': debug_request.freshness_half_life or 30,
            'total_recommendations_generated': len(recommendations),
            'total_after_filtering': len(filtered_recommendations),
            'filtering_criteria': {
                'exclude_viewed': debug_request.exclude_viewed,
                'exclude_registered': debug_request.exclude_registered,
                'exclude_ended': debug_request.exclude_ended
            }
        }
        
        return RecommendationDebugResponse(
            success=True,
            user_id=user_id,
            user_profile=user_profile,
            recommendations=recommended_items,
            total_count=len(recommended_items),
            parameters_used={
                'count': debug_request.count,
                'exclude_viewed': debug_request.exclude_viewed,
                'exclude_registered': debug_request.exclude_registered,
                'exclude_ended': debug_request.exclude_ended,
                'layer_weights': debug_request.layer_weights,
                'content_match_threshold': debug_request.content_match_threshold,
                'collaborative_users_limit': debug_request.collaborative_users_limit,
                'freshness_half_life': debug_request.freshness_half_life
            },
            debug_info=debug_info,
            message="推荐成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推荐失败: {str(e)}"
        )


# ============ 辅助函数 ============

async def _filter_recommendations(
    user_id: int,
    recommendations: list,
    exclude_viewed: bool = True,
    exclude_registered: bool = True,
    exclude_ended: bool = True
) -> list:
    """
    根据条件过滤和调整推荐的活动
    
    不再完全排除已浏览/已报名的活动，而是通过降低其推荐分数来处理，
    确保推荐数量充足。仅过滤已结束的活动。
    
    Args:
        user_id: 用户ID
        recommendations: 推荐活动列表
        exclude_viewed: 是否降低已浏览活动的分数
        exclude_registered: 是否降低已报名活动的分数
        exclude_ended: 是否排除已结束活动
    
    Returns:
        调整后的推荐列表
    """
    if not recommendations:
        return []
    
    # 获取用户已浏览和已报名的活动（用于降权）
    viewed_activities = set()
    registered_activities = set()
    
    if exclude_viewed:
        viewed_activities = set(await recommendation_dao.get_user_viewed_activities(user_id))
    
    if exclude_registered:
        registered_activities = set(await recommendation_dao.get_user_registered_activities(user_id))
    
    adjusted = []
    for rec in recommendations:
        activity_id = rec['activity_id']
        
        # 仅排除已结束的活动
        if exclude_ended:
            activity = await Activities.get_or_none(id=activity_id)
            if activity and activity.status == 'ended':
                continue
        
        # 对已浏览/已报名的活动进行降权（额外降低30%）
        adjusted_rec = rec.copy()
        penalty_factor = 1.0
        
        if exclude_viewed and activity_id in viewed_activities:
            penalty_factor *= 0.7
        if exclude_registered and activity_id in registered_activities:
            penalty_factor *= 0.7
        
        # 应用降权系数
        if penalty_factor < 1.0:
            adjusted_rec['recommendation_score'] = rec['recommendation_score'] * penalty_factor
        
        adjusted.append(adjusted_rec)
    
    return adjusted


async def _build_user_preference_profile(user_id: int) -> UserPreferenceProfile:
    """
    构建用户偏好档案
    
    Args:
        user_id: 用户ID
    
    Returns:
        用户偏好档案
    """
    user = await Users.get_or_none(id=user_id)
    if not user:
        return UserPreferenceProfile(user_id=user_id)
    
    # 从profile_attributes中提取用户属性
    profile_attrs = user.profile_attributes or {}
    
    # 获取用户行为统计
    viewed_count = len(await recommendation_dao.get_user_viewed_activities(user_id))
    registered_count = len(await recommendation_dao.get_user_registered_activities(user_id))
    
    # 判断行为强度
    total_actions = viewed_count + registered_count
    if total_actions == 0:
        behavior_intensity = "low"
    elif total_actions < 10:
        behavior_intensity = "low"
    elif total_actions < 30:
        behavior_intensity = "moderate"
    else:
        behavior_intensity = "high"
    
    return UserPreferenceProfile(
        user_id=user_id,
        interests=profile_attrs.get('interests', []),
        grade=profile_attrs.get('grade'),
        major=profile_attrs.get('major'),
        college=profile_attrs.get('college'),
        viewed_activities_count=viewed_count,
        registered_activities_count=registered_count,
        behavior_intensity=behavior_intensity
    )


def _get_default_weights() -> Dict[str, float]:
    """
    获取推荐层的默认权重
    
    Returns:
        权重字典
    """
    return {
        'content_filter': 0.35,
        'hotness': 0.20,
        'collaborative': 0.25,
        'freshness': 0.20
    }


def _add_randomness_to_scores(recommendations: list, noise_factor: float = 0.08) -> list:
    """
    为推荐分数添加随机噪声，实现多样化推荐
    
    通过添加随机噪声（±noise_factor的百分比）到每个推荐的分数，
    确保用户多次请求推荐时会得到不同的结果，避免推荐重复。
    
    Args:
        recommendations: 推荐列表
        noise_factor: 噪声因子（0.08表示±8%的随机波动）
    
    Returns:
        添加随机性后的推荐列表
    """
    if not recommendations:
        return recommendations
    
    # 为每个推荐添加随机噪声
    randomized = []
    for rec in recommendations:
        rec_copy = rec.copy()
        original_score = rec_copy.get('recommendation_score', 0)
        
        # 计算随机噪声（范围：-noise_factor到+noise_factor）
        noise = random.uniform(-noise_factor, noise_factor) * original_score
        randomized_score = max(0, original_score + noise)  # 确保分数不为负
        
        rec_copy['recommendation_score'] = round(randomized_score, 2)
        randomized.append(rec_copy)
    
    # 根据随机化后的分数重新排序
    randomized.sort(
        key=lambda x: x['recommendation_score'],
        reverse=True
    )
    
    return randomized
