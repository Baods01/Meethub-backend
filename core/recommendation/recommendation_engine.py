"""
推荐引擎 - 核心推荐算法实现
实现多层推荐算法：内容过滤、热度排序、协同过滤、时间衰减
"""
from typing import Optional, List, Dict, Set
from datetime import datetime, timedelta
from dao.recommendation_dao import RecommendationDAO
from models.activities import Activities
from models.users import Users
from .scoring_utils import ScoringUtils


class RecommendationEngine:
    """推荐引擎类 - 实现完整的推荐算法流程"""
    
    def __init__(self):
        """初始化推荐引擎"""
        self.dao = RecommendationDAO()
        self.scorer = ScoringUtils()

    async def recommend_activities(
        self,
        user_id: int,
        count: int = 5,
        layer_weights: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> List[Dict]:
        """
        主推荐方法 - 综合四层推荐算法
        
        流程：
        1. 第1层：内容过滤 - 匹配用户标签与活动受众
        2. 第2层：热度排序 - 热门活动优先
        3. 第3层：协同过滤 - 基于相似用户推荐
        4. 第4层：时间衰减 - 优先推荐新活动
        
        Args:
            user_id: 用户ID
            count: 推荐数量（默认5个）
            layer_weights: 各层权重 {
                'content_filter': 0.35,    # 内容过滤权重
                'hotness': 0.20,           # 热度权重
                'collaborative': 0.25,     # 协同过滤权重
                'freshness': 0.20          # 新鲜度权重
            }
            **kwargs: 其他参数
                - content_match_threshold: 内容匹配最低阈值（默认0.1）
                - hotness_weight_config: 热度计算权重配置
                - collaborative_users_limit: 协同过滤参考用户数（默认5）
                - freshness_half_life: 新鲜度半衰期天数（默认30）
                
        Returns:
            推荐活动列表，每个活动包含：
            - activity_id, title, description等基本信息
            - recommendation_score: 最终推荐分数
            - reasons: 推荐理由列表
            - score_breakdown: 各层分数分解
        """
        if layer_weights is None:
            layer_weights = {
                'content_filter': 0.35,
                'hotness': 0.20,
                'collaborative': 0.25,
                'freshness': 0.20
            }
        
        # 获取用户信息
        user = await Users.get_or_none(id=user_id)
        if not user:
            return []
        
        # 第1层：内容过滤
        content_filtered_activities = await self._layer_content_filter(
            user_id,
            user,
            kwargs.get('content_match_threshold', 0.1)
        )
        
        if not content_filtered_activities:
            return []
        
        # 第2层：热度排序
        hotness_scored = await self._layer_hotness_ranking(
            content_filtered_activities,
            kwargs.get('hotness_weight_config')
        )
        
        # 第3层：协同过滤
        collaborative_scores = await self._layer_collaborative_filtering(
            user_id,
            kwargs.get('collaborative_users_limit', 5)
        )
        
        # 第4层：时间衰减
        freshness_scores = await self._layer_freshness_decay(
            hotness_scored,
            kwargs.get('freshness_half_life', 30)
        )
        
        # 综合打分
        recommendations = await self._synthesize_scores(
            freshness_scores,
            collaborative_scores,
            layer_weights,
            count
        )
        
        return recommendations

    async def _layer_content_filter(
        self,
        user_id: int,
        user: Users,
        match_threshold: float = 0.1
    ) -> List[Dict]:
        """
        第1层：内容过滤 - 根据用户标签和活动受众进行匹配
        
        Args:
            user_id: 用户ID
            user: 用户对象
            match_threshold: 匹配阈值（0-1），低于此阈值的活动被过滤
            
        Returns:
            过滤后的活动列表，每个活动包含content_match_score
        """
        # 获取用户已参与的活动（用于降权，不再排除）
        user_viewed = await self.dao.get_user_viewed_activities(user_id)
        user_registered = await self.dao.get_user_registered_activities(user_id)
        viewed_or_registered_ids = set(user_viewed + user_registered)
        
        # 获取所有可推荐的活动（不再排除已浏览的活动）
        all_activities = await self.dao.get_all_recommendable_activities(None)
        
        if not all_activities:
            return []
        
        user_profile = user.profile_attributes or {}
        filtered_activities = []
        
        for activity in all_activities:
            # 计算内容匹配度
            content_match = await self._calculate_content_match(
                activity,
                user_profile
            )
            
            # 只保留超过阈值的活动
            if content_match >= (match_threshold * 100):
                # 对已浏览/已报名的活动进行降权（降低50%）
                is_viewed_or_registered = activity.id in viewed_or_registered_ids
                adjusted_content_match = content_match * 0.5 if is_viewed_or_registered else content_match
                
                filtered_activities.append({
                    'activity': activity,
                    'content_match_score': adjusted_content_match,
                    'is_viewed_or_registered': is_viewed_or_registered
                })
        
        return filtered_activities

    async def _calculate_content_match(
        self,
        activity: Activities,
        user_profile: Dict
    ) -> float:
        """
        计算单个活动的内容匹配度
        
        匹配维度：
        - 年级匹配：用户年级是否在目标年级内
        - 标签匹配：用户爱好与活动标签/分类的相似度
        - 时间匹配：活动时间是否在未来
        
        Args:
            activity: 活动对象
            user_profile: 用户个性属性
            
        Returns:
            匹配度分数（0-100）
        """
        scores = {}
        weights = {'grade': 0.25, 'tags': 0.50, 'time': 0.25}
        
        # 年级匹配
        user_grade = user_profile.get('grade', '')
        target_grades = activity.target_audience.get('Targeted_people', [])
        grade_score = self.scorer.grade_match_score(user_grade, target_grades)
        scores['grade'] = grade_score
        
        # 标签匹配
        user_hobbies = set(user_profile.get('hobby', []))
        activity_tags = set(activity.tags or [])
        activity_classes = set(activity.target_audience.get('Activity_class', []))
        
        tag_score = self.scorer.calculate_tag_match_score(
            user_hobbies,
            activity_tags,
            activity_classes
        )
        scores['tags'] = tag_score
        
        # 时间匹配
        time_score = self.scorer.time_proximity_score(activity.start_time)
        scores['time'] = time_score
        
        # 加权融合
        content_match = self.scorer.weighted_fusion(scores, weights)
        
        return content_match

    async def _layer_hotness_ranking(
        self,
        activities_with_content_score: List[Dict],
        weight_config: Optional[Dict] = None
    ) -> List[Dict]:
        """
        第2层：热度排序 - 根据活动热度排序
        
        Args:
            activities_with_content_score: 包含content_match_score的活动列表
            weight_config: 热度计算权重配置
            
        Returns:
            按热度排序的活动列表，添加hotness_score
        """
        if not activities_with_content_score:
            return []
        
        if weight_config is None:
            weight_config = {
                'views_weight': 0.3,
                'registration_weight': 0.4,
                'rating_weight': 0.3,
                'max_views': 1000
            }
        
        # 批量获取活动统计
        activity_ids = [item['activity'].id for item in activities_with_content_score]
        activity_stats = await self.dao.get_activities_engagement_stats(activity_ids)
        
        # 计算每个活动的热度分数
        for item in activities_with_content_score:
            activity = item['activity']
            stats = activity_stats.get(activity.id, {})
            
            views_count = stats.get('views', 0)
            registrations = stats.get('registrations', 0)
            avg_rating = stats.get('average_rating', 0.0)
            
            # 计算报名占比
            registration_ratio = (
                registrations / activity.max_participants
                if activity.max_participants > 0 else 0.0
            )
            
            # 计算热度分数
            hotness = self.scorer.calculate_hotness_score(
                views_count,
                registration_ratio,
                avg_rating,
                views_weight=weight_config.get('views_weight', 0.3),
                registration_weight=weight_config.get('registration_weight', 0.4),
                rating_weight=weight_config.get('rating_weight', 0.3),
                max_views=weight_config.get('max_views', 1000)
            )
            
            item['hotness_score'] = hotness
        
        # 按热度排序
        activities_with_content_score.sort(
            key=lambda x: x['hotness_score'],
            reverse=True
        )
        
        return activities_with_content_score

    async def _layer_collaborative_filtering(
        self,
        user_id: int,
        similar_users_limit: int = 5
    ) -> Dict[int, float]:
        """
        第3层：协同过滤 - 根据相似用户的喜好推荐
        
        Args:
            user_id: 用户ID
            similar_users_limit: 参考相似用户数量
            
        Returns:
            活动ID到协同过滤分数的映射
        """
        # 使用DAO的现有方法获取协同过滤分数
        collaborative_scores = await self.dao.get_activities_from_similar_users(
            user_id,
            similar_users_limit
        )
        
        # 标准化分数到0-100
        if collaborative_scores:
            max_score = max(collaborative_scores.values())
            if max_score > 0:
                collaborative_scores = {
                    activity_id: (score / max_score) * 100
                    for activity_id, score in collaborative_scores.items()
                }
        
        return collaborative_scores

    async def _layer_freshness_decay(
        self,
        activities_with_hotness: List[Dict],
        half_life_days: int = 30
    ) -> List[Dict]:
        """
        第4层：时间衰减 - 优先推荐新活动
        
        使用指数衰减模型，新活动获得高分，随时间衰减
        
        Args:
            activities_with_hotness: 包含hotness_score的活动列表
            half_life_days: 半衰期天数
            
        Returns:
            添加freshness_score的活动列表
        """
        for item in activities_with_hotness:
            activity = item['activity']
            
            freshness = self.scorer.calculate_time_decay_score(
                activity.created_at,
                activity.start_time,
                base_score=100.0,
                half_life_days=half_life_days
            )
            
            item['freshness_score'] = freshness
        
        return activities_with_hotness

    async def _synthesize_scores(
        self,
        activities_with_all_scores: List[Dict],
        collaborative_scores: Dict[int, float],
        layer_weights: Dict[str, float],
        count: int
    ) -> List[Dict]:
        """
        综合打分 - 融合所有维度的分数生成最终推荐
        
        Args:
            activities_with_all_scores: 包含所有维度分数的活动列表
            collaborative_scores: 协同过滤分数映射
            layer_weights: 各层权重
            count: 返回数量
            
        Returns:
            最终推荐列表
        """
        recommendations = []
        
        for item in activities_with_all_scores:
            activity = item['activity']
            
            # 获取协同过滤分数，如果没有则为0
            collab_score = collaborative_scores.get(activity.id, 0.0)
            
            # 融合所有维度的分数
            scores = {
                'content_filter': item['content_match_score'],
                'hotness': item['hotness_score'],
                'collaborative': collab_score,
                'freshness': item['freshness_score']
            }
            
            # 加权融合
            total_score = self.scorer.weighted_fusion(scores, layer_weights)
            
            # 生成推荐理由
            reasons = self._generate_reasons(scores, item['activity'])
            
            # 构建推荐结果
            recommendations.append({
                'activity_id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'cover_image': activity.cover_image,
                'location': activity.location,
                'start_time': activity.start_time,
                'end_time': activity.end_time,
                'max_participants': activity.max_participants,
                'current_participants': activity.current_participants,
                'status': activity.status,
                'views_count': activity.views_count,
                'tags': activity.tags,
                'target_audience': activity.target_audience,
                'benefits': activity.benefits,
                'publisher': {
                    'id': activity.publisher.id,
                    'username': activity.publisher.username,
                    'nickname': activity.publisher.nickname or activity.publisher.username,
                    'avatar': activity.publisher.avatar
                },
                'recommendation_score': total_score,
                'reasons': reasons,
                'score_breakdown': {
                    'content_match': scores['content_filter'],
                    'hotness': scores['hotness'],
                    'collaborative': scores['collaborative'],
                    'freshness': scores['freshness']
                }
            })
        
        # 按总分排序
        recommendations.sort(
            key=lambda x: x['recommendation_score'],
            reverse=True
        )
        
        # 返回前N个
        return recommendations[:count]

    def _generate_reasons(
        self,
        scores: Dict[str, float],
        activity: Activities
    ) -> List[str]:
        """
        根据各维度分数生成推荐理由
        
        Args:
            scores: 各维度分数
            activity: 活动对象
            
        Returns:
            推荐理由列表
        """
        reasons = []
        
        # 内容匹配理由
        if scores['content_filter'] > 70:
            reasons.append("符合你的兴趣爱好")
        
        # 热度理由
        if scores['hotness'] > 65:
            reasons.append("热门活动，评价不错")
        
        # 新鲜度理由
        if scores['freshness'] > 70:
            reasons.append("最新发布的活动")
        
        # 协同过滤理由
        if scores['collaborative'] > 30:
            reasons.append("与你有相同兴趣的用户也感兴趣")
        
        # 如果没有生成理由，返回默认
        if not reasons:
            reasons.append("值得一试的活动")
        
        return reasons

    async def get_user_preference_profile(self, user_id: int) -> Dict:
        """
        获取用户的偏好档案（用于调试和分析）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户偏好档案
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            return {}
        
        # 获取用户行为统计
        behavior_stats = await self.dao.get_user_behavior_stats(user_id)
        
        # 获取用户的标签频率
        tag_frequency = await self.dao.get_activity_tags_frequency(user_id, limit=10)
        
        # 获取用户的分类频率
        category_frequency = await self.dao.get_activity_categories_frequency(user_id, limit=10)
        
        return {
            'user_id': user_id,
            'username': user.username,
            'profile_attributes': user.profile_attributes or {},
            'behavior_stats': behavior_stats,
            'top_tags': tag_frequency,
            'top_categories': category_frequency
        }

    async def adjust_recommendation_weights(
        self,
        default_weights: Optional[Dict[str, float]] = None,
        user_behavior_intensity: Optional[str] = None
    ) -> Dict[str, float]:
        """
        根据用户行为强度动态调整推荐权重
        
        Args:
            default_weights: 默认权重
            user_behavior_intensity: 用户行为强度（'low', 'medium', 'high'）
            
        Returns:
            调整后的权重
        """
        if default_weights is None:
            default_weights = {
                'content_filter': 0.35,
                'hotness': 0.20,
                'collaborative': 0.25,
                'freshness': 0.20
            }
        
        # 根据行为强度调整权重
        if user_behavior_intensity == 'high':
            # 行为活跃用户更多依赖协同过滤
            adjusted = {
                'content_filter': 0.25,
                'hotness': 0.15,
                'collaborative': 0.40,
                'freshness': 0.20
            }
        elif user_behavior_intensity == 'low':
            # 行为不活跃的用户更依赖内容过滤
            adjusted = {
                'content_filter': 0.50,
                'hotness': 0.15,
                'collaborative': 0.10,
                'freshness': 0.25
            }
        else:
            # 中等强度使用默认权重
            adjusted = default_weights
        
        return adjusted
