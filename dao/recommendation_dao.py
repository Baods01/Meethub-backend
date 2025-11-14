from typing import Optional, List, Dict, Set, Tuple
from datetime import datetime, timedelta
from tortoise.expressions import F, Q
from tortoise.functions import Count
from .base import BaseDAO
from models.activities import Activities
from models.registrations import Registrations
from models.user_logs import UserOperationLogs
from models.users import Users


class RecommendationDAO(BaseDAO[Activities]):
    """推荐算法数据访问对象"""
    
    def __init__(self):
        super().__init__(Activities)

    # ============ 基础数据获取方法 ============

    async def get_user_viewed_activities(
        self, 
        user_id: int
    ) -> List[int]:
        """
        获取用户已浏览的活动ID列表（去重）
        
        :param user_id: 用户ID
        :return: 活动ID列表
        """
        logs = await UserOperationLogs.filter(
            user_id=user_id,
            operation_type='view_activity'
        ).values_list('activity_id', flat=True)
        
        # 返回去重的列表
        return list(set(logs))

    async def get_user_registered_activities(
        self, 
        user_id: int
    ) -> List[int]:
        """
        获取用户已报名的活动ID列表（去重）
        
        :param user_id: 用户ID
        :return: 活动ID列表
        """
        registrations = await Registrations.filter(
            participant_id=user_id
        ).values_list('activity_id', flat=True)
        
        # 返回去重的列表
        return list(set(registrations))

    async def get_user_behavior_stats(
        self, 
        user_id: int
    ) -> Dict:
        """
        获取用户行为统计
        
        :param user_id: 用户ID
        :return: 行为统计字典
        """
        # 获取浏览统计
        view_count = await UserOperationLogs.filter(
            user_id=user_id,
            operation_type='view_activity'
        ).count()
        
        # 获取报名统计
        registration_count = await Registrations.filter(
            participant_id=user_id
        ).count()
        
        # 获取已参加活动（签退）统计
        attended_count = await Registrations.filter(
            participant_id=user_id,
            check_out_time__isnull=False
        ).count()
        
        # 获取用户评分的活动
        rated_activities = await Registrations.filter(
            participant_id=user_id,
            rating__isnull=False
        ).values_list('activity_id', flat=True)
        
        # 计算平均评分
        ratings = await Registrations.filter(
            participant_id=user_id,
            rating__isnull=False
        ).values_list('rating', flat=True)
        
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # 获取用户个性属性
        user = await Users.get_or_none(id=user_id)
        profile_attributes = user.profile_attributes if user else {}
        
        return {
            'view_count': view_count,
            'registration_count': registration_count,
            'attended_count': attended_count,
            'rated_activities_count': len(set(rated_activities)),
            'average_rating': round(avg_rating, 2),
            'profile_attributes': profile_attributes
        }

    async def get_all_recommendable_activities(
        self, 
        exclude_ids: Optional[List[int]] = None
    ) -> List[Activities]:
        """
        获取所有可推荐的活动（未删除、已发布）
        
        :param exclude_ids: 要排除的活动ID列表
        :return: 活动列表
        """
        query = self.model.filter(
            is_deleted=False,
            status__in=['published', 'ongoing']
        )
        
        if exclude_ids:
            query = query.filter(id__not_in=exclude_ids)
        
        # 预加载发布者信息
        return await query.prefetch_related('publisher')

    # ============ 热度和新鲜度计算方法 ============

    async def calculate_activity_hotness_score(
        self, 
        activity_id: int,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        计算活动热度分数
        
        :param activity_id: 活动ID
        :param weights: 权重字典 {'views': 0.3, 'registrations': 0.4, 'ratings': 0.3}
        :return: 热度分数（0-100）
        """
        if weights is None:
            weights = {'views': 0.3, 'registrations': 0.4, 'ratings': 0.3}
        
        activity = await self.get_by_id(activity_id)
        if not activity:
            return 0.0
        
        # 获取活动的浏览量
        views_score = min(activity.views_count / 100, 1.0) * 100  # 标准化到100
        
        # 获取活动的报名人数占比
        registration_ratio = min(
            activity.current_participants / activity.max_participants, 
            1.0
        ) if activity.max_participants > 0 else 0.0
        registration_score = registration_ratio * 100
        
        # 获取活动的评分
        registrations = await Registrations.filter(
            activity_id=activity_id,
            rating__isnull=False
        ).values_list('rating', flat=True)
        
        avg_rating = (sum(registrations) / len(registrations)) if registrations else 0.0
        rating_score = (avg_rating / 5.0) * 100  # 标准化到100
        
        # 加权计算热度分数
        hotness_score = (
            views_score * weights['views'] +
            registration_score * weights['registrations'] +
            rating_score * weights['ratings']
        )
        
        return round(hotness_score, 2)

    async def calculate_activity_freshness_score(
        self, 
        activity_id: int,
        base_score: float = 100,
        days_decay: int = 30
    ) -> float:
        """
        计算活动新鲜度分数（基于创建时间和开始时间）
        
        :param activity_id: 活动ID
        :param base_score: 基础分数
        :param days_decay: 衰减天数（天数后分数衰减50%）
        :return: 新鲜度分数（0-100）
        """
        activity = await self.get_by_id(activity_id)
        if not activity:
            return 0.0
        
        # 处理时区问题：如果created_at有时区信息，先移除
        created_at = activity.created_at
        if created_at.tzinfo is not None:
            created_at = created_at.replace(tzinfo=None)
        
        now = datetime.now()
        days_since_created = (now - created_at).days
        
        # 指数衰减：base_score * (0.5)^(days_since_created/days_decay)
        freshness_score = base_score * (0.5 ** (days_since_created / days_decay))
        
        return round(max(0, min(freshness_score, base_score)), 2)

    # ============ 协同过滤方法 ============

    async def get_similar_users(
        self, 
        user_id: int,
        min_common_activities: int = 2,
        limit: int = 20
    ) -> List[Dict]:
        """
        获取相似用户（基于共同浏览/报名活动）
        
        :param user_id: 用户ID
        :param min_common_activities: 最小共同活动数
        :param limit: 返回的相似用户限制数
        :return: 相似用户列表，每个用户包含ID和相似度
        """
        # 获取目标用户的浏览和报名活动
        viewed = await self.get_user_viewed_activities(user_id)
        registered = await self.get_user_registered_activities(user_id)
        user_activities = set(viewed + registered)
        
        if not user_activities:
            return []
        
        # 查找有共同活动的其他用户
        similar_users_with_scores = []
        
        # 找出浏览/报名过这些活动的其他用户
        other_users = await Users.filter(id__not=user_id).all()
        
        for other_user in other_users:
            other_viewed = await self.get_user_viewed_activities(other_user.id)
            other_registered = await self.get_user_registered_activities(other_user.id)
            other_activities = set(other_viewed + other_registered)
            
            # 计算共同活动数
            common_count = len(user_activities & other_activities)
            
            if common_count >= min_common_activities:
                # 计算杰卡德相似度
                union_count = len(user_activities | other_activities)
                similarity = common_count / union_count if union_count > 0 else 0.0
                
                similar_users_with_scores.append({
                    'user_id': other_user.id,
                    'similarity': round(similarity, 3),
                    'common_activities_count': common_count
                })
        
        # 按相似度排序
        similar_users_with_scores.sort(
            key=lambda x: x['similarity'], 
            reverse=True
        )
        
        return similar_users_with_scores[:limit]

    async def get_activities_from_similar_users(
        self,
        user_id: int,
        similar_users_limit: int = 5
    ) -> Dict[int, float]:
        """
        基于相似用户获取推荐活动及推荐分数
        
        :param user_id: 用户ID
        :param similar_users_limit: 相似用户限制
        :return: {activity_id: recommendation_score}
        """
        # 获取相似用户
        similar_users = await self.get_similar_users(
            user_id, 
            limit=similar_users_limit
        )
        
        if not similar_users:
            return {}
        
        # 获取当前用户的活动
        user_activities = set(
            await self.get_user_viewed_activities(user_id) +
            await self.get_user_registered_activities(user_id)
        )
        
        # 收集相似用户参与的活动及权重分数
        activity_scores = {}
        
        for similar_user in similar_users:
            similar_user_id = similar_user['user_id']
            similarity_score = similar_user['similarity']
            
            # 获取相似用户参与的活动
            similar_viewed = set(
                await self.get_user_viewed_activities(similar_user_id)
            )
            similar_registered = set(
                await self.get_user_registered_activities(similar_user_id)
            )
            
            similar_activities = similar_viewed | similar_registered
            
            # 排除当前用户已参与的活动
            new_activities = similar_activities - user_activities
            
            # 加权计算推荐分数
            for activity_id in new_activities:
                if activity_id not in activity_scores:
                    activity_scores[activity_id] = 0.0
                
                activity_scores[activity_id] += similarity_score
        
        return activity_scores

    # ============ 内容过滤方法 ============

    async def calculate_activity_match_score(
        self,
        activity_id: int,
        user_profile: Dict
    ) -> float:
        """
        基于用户标签计算活动匹配度
        
        :param activity_id: 活动ID
        :param user_profile: 用户个性属性
        :return: 匹配度分数（0-100）
        """
        activity = await self.get_by_id(activity_id)
        if not activity:
            return 0.0
        
        match_score = 0.0
        match_count = 0
        
        # 年级匹配
        user_grade = user_profile.get('grade', '')
        target_people = activity.target_audience.get('Targeted_people', [])
        
        if user_grade and target_people:
            if user_grade in target_people:
                match_score += 30
            match_count += 1
        
        # 专业匹配
        user_major = user_profile.get('major', '')
        # 注：如果target_audience中有major字段，可以在此处理
        if user_major:
            match_count += 1
        
        # 爱好匹配（与活动标签和分类匹配）
        user_hobbies = set(user_profile.get('hobby', []))
        activity_classes = set(activity.target_audience.get('Activity_class', []))
        activity_tags = set(activity.tags)
        
        all_activity_features = activity_classes | activity_tags
        
        if user_hobbies and all_activity_features:
            hobby_match_count = len(user_hobbies & all_activity_features)
            hobby_match_ratio = hobby_match_count / len(user_hobbies)
            match_score += hobby_match_ratio * 40
            match_count += 1
        
        # 时间匹配（活动时间在未来）
        start_time = activity.start_time
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        
        if start_time > datetime.now():
            match_score += 30
        else:
            # 已进行的活动扣分
            match_score -= 10
        
        match_count += 1
        
        # 计算平均匹配度
        if match_count > 0:
            avg_match = match_score / match_count
        else:
            avg_match = 0.0
        
        return round(max(0, min(avg_match, 100)), 2)

    # ============ 批量获取方法 ============

    async def get_activities_engagement_stats(
        self,
        activity_ids: List[int]
    ) -> Dict[int, Dict]:
        """
        批量获取活动的浏览/报名人数及统计
        
        :param activity_ids: 活动ID列表
        :return: {activity_id: {'views': int, 'registrations': int, 'attended': int}}
        """
        stats = {}
        
        for activity_id in activity_ids:
            # 获取浏览量
            views = await UserOperationLogs.filter(
                activity_id=activity_id,
                operation_type='view_activity'
            ).count()
            
            # 获取报名人数
            registrations = await Registrations.filter(
                activity_id=activity_id
            ).count()
            
            # 获取已签退人数（已参加）
            attended = await Registrations.filter(
                activity_id=activity_id,
                check_out_time__isnull=False
            ).count()
            
            # 获取平均评分
            ratings = await Registrations.filter(
                activity_id=activity_id,
                rating__isnull=False
            ).values_list('rating', flat=True)
            
            avg_rating = (sum(ratings) / len(ratings)) if ratings else 0.0
            
            stats[activity_id] = {
                'views': views,
                'registrations': registrations,
                'attended': attended,
                'average_rating': round(avg_rating, 2)
            }
        
        return stats

    # ============ 核心推荐方法 ============

    async def recommend_activities(
        self,
        user_id: int,
        count: int = 5,
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        为用户推荐活动
        
        :param user_id: 用户ID
        :param count: 推荐数量
        :param weights: 推荐权重 {
            'hotness': 0.2,        # 热度权重
            'freshness': 0.15,     # 新鲜度权重
            'collaborative': 0.25, # 协同过滤权重
            'content_match': 0.4   # 内容匹配权重
        }
        :return: 推荐活动列表，包含活动信息和推荐理由
        """
        if weights is None:
            weights = {
                'hotness': 0.2,
                'freshness': 0.15,
                'collaborative': 0.25,
                'content_match': 0.4
            }
        
        # 获取用户信息
        user = await Users.get_or_none(id=user_id)
        if not user:
            return []
        
        user_profile = user.profile_attributes if user.profile_attributes else {}
        
        # 获取已参与的活动
        user_viewed = await self.get_user_viewed_activities(user_id)
        user_registered = await self.get_user_registered_activities(user_id)
        excluded_ids = list(set(user_viewed + user_registered))
        
        # 获取所有可推荐活动
        all_activities = await self.get_all_recommendable_activities(excluded_ids)
        
        if not all_activities:
            return []
        
        # 获取协同过滤推荐分数
        collaborative_scores = await self.get_activities_from_similar_users(user_id)
        
        # 计算每个活动的综合推荐分数
        activity_scores = []
        
        for activity in all_activities:
            # 计算各个维度的分数
            hotness = await self.calculate_activity_hotness_score(activity.id)
            freshness = await self.calculate_activity_freshness_score(activity.id)
            collaborative = collaborative_scores.get(activity.id, 0.0) * 20  # 标准化
            content_match = await self.calculate_activity_match_score(activity.id, user_profile)
            
            # 计算综合分数
            total_score = (
                hotness * weights['hotness'] +
                freshness * weights['freshness'] +
                collaborative * weights['collaborative'] +
                content_match * weights['content_match']
            )
            
            # 收集推荐理由
            reasons = []
            if content_match > 60:
                reasons.append("符合你的兴趣爱好")
            if hotness > 50:
                reasons.append("热门活动")
            if freshness > 60:
                reasons.append("最新发布")
            if collaborative > 10:
                reasons.append("类似用户感兴趣")
            
            activity_scores.append({
                'activity': activity,
                'total_score': round(total_score, 2),
                'hotness': hotness,
                'freshness': freshness,
                'collaborative': collaborative,
                'content_match': content_match,
                'reasons': reasons if reasons else ["推荐理由暂无"]
            })
        
        # 按总分排序并返回前N个
        activity_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 构建返回数据
        recommendations = []
        for item in activity_scores[:count]:
            activity = item['activity']
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
                'publisher': {
                    'id': activity.publisher.id,
                    'username': activity.publisher.username,
                    'nickname': activity.publisher.nickname,
                    'avatar': activity.publisher.avatar
                },
                'recommendation_score': item['total_score'],
                'reasons': item['reasons'],
                'score_breakdown': {
                    'content_match': item['content_match'],
                    'hotness': item['hotness'],
                    'freshness': item['freshness'],
                    'collaborative': item['collaborative']
                }
            })
        
        return recommendations

    # ============ 辅助方法 ============

    async def get_activity_tags_frequency(
        self,
        user_id: int,
        limit: int = 10
    ) -> Dict[str, int]:
        """
        获取用户浏览/报名活动的标签频率
        
        :param user_id: 用户ID
        :param limit: 返回的标签限制数
        :return: {tag: frequency}
        """
        # 获取用户参与的活动
        user_activities_ids = (
            await self.get_user_viewed_activities(user_id) +
            await self.get_user_registered_activities(user_id)
        )
        
        # 获取活动的标签
        activities = await self.model.filter(id__in=user_activities_ids).all()
        
        tag_frequency = {}
        for activity in activities:
            tags = activity.tags if activity.tags else []
            for tag in tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        
        # 按频率排序
        sorted_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_tags[:limit])

    async def get_activity_categories_frequency(
        self,
        user_id: int,
        limit: int = 10
    ) -> Dict[str, int]:
        """
        获取用户浏览/报名活动的分类频率
        
        :param user_id: 用户ID
        :param limit: 返回的分类限制数
        :return: {category: frequency}
        """
        # 获取用户参与的活动
        user_activities_ids = (
            await self.get_user_viewed_activities(user_id) +
            await self.get_user_registered_activities(user_id)
        )
        
        # 获取活动的分类
        activities = await self.model.filter(id__in=user_activities_ids).all()
        
        category_frequency = {}
        for activity in activities:
            categories = activity.target_audience.get('Activity_class', [])
            for category in categories:
                category_frequency[category] = category_frequency.get(category, 0) + 1
        
        # 按频率排序
        sorted_categories = sorted(category_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_categories[:limit])
