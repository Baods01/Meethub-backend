"""
打分工具模块 - 提供推荐算法中的各种打分方法
"""
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
import math


class ScoringUtils:
    """推荐算法打分工具类"""

    @staticmethod
    def calculate_tag_match_score(
        user_tags: Set[str],
        activity_tags: Set[str],
        activity_categories: Set[str]
    ) -> float:
        """
        计算用户标签与活动标签的匹配度
        
        Args:
            user_tags: 用户标签集合（如爱好、兴趣）
            activity_tags: 活动标签集合
            activity_categories: 活动分类集合
            
        Returns:
            匹配度分数（0-100）
        """
        if not user_tags:
            return 0.0
        
        all_activity_features = activity_tags | activity_categories
        
        if not all_activity_features:
            return 0.0
        
        # 计算交集和并集
        intersection = len(user_tags & all_activity_features)
        union = len(user_tags | all_activity_features)
        
        # 使用杰卡德相似度（Jaccard Similarity）
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        return round(jaccard_similarity * 100, 2)

    @staticmethod
    def calculate_hotness_score(
        views_count: int,
        registration_ratio: float,
        average_rating: float,
        views_weight: float = 0.3,
        registration_weight: float = 0.4,
        rating_weight: float = 0.3,
        max_views: int = 1000
    ) -> float:
        """
        计算活动热度分数
        
        Args:
            views_count: 浏览次数
            registration_ratio: 报名人数占比（已报名/最大人数）
            average_rating: 平均评分（0-5）
            views_weight: 浏览量权重
            registration_weight: 报名人数权重
            rating_weight: 评分权重
            max_views: 浏览量归一化的上限
            
        Returns:
            热度分数（0-100）
        """
        # 标准化浏览量
        views_score = min(views_count / max_views, 1.0) * 100
        
        # 报名人数占比本身就是0-1之间的比例
        registration_score = min(registration_ratio, 1.0) * 100
        
        # 评分标准化（0-5映射到0-100）
        rating_score = (average_rating / 5.0) * 100
        
        # 加权计算
        hotness = (
            views_score * views_weight +
            registration_score * registration_weight +
            rating_score * rating_weight
        )
        
        return round(hotness, 2)

    @staticmethod
    def calculate_time_decay_score(
        created_at: datetime,
        start_time: datetime,
        base_score: float = 100.0,
        half_life_days: int = 30
    ) -> float:
        """
        计算活动新鲜度分数（时间衰减）
        
        使用指数衰减模型：score = base_score * 0.5^(days_elapsed / half_life_days)
        
        Args:
            created_at: 活动创建时间
            start_time: 活动开始时间
            base_score: 基础分数
            half_life_days: 半衰期（天数），用于控制衰减速度
            
        Returns:
            新鲜度分数（0-100）
        """
        now = datetime.now()
        
        # 处理时区问题
        created_at = ScoringUtils._remove_timezone(created_at)
        start_time = ScoringUtils._remove_timezone(start_time)
        
        # 优先使用创建时间，如果没有则使用开始时间
        reference_time = created_at if created_at else start_time
        
        days_elapsed = (now - reference_time).days
        
        # 确保天数不为负
        days_elapsed = max(0, days_elapsed)
        
        # 指数衰减
        decay_score = base_score * (0.5 ** (days_elapsed / half_life_days))
        
        return round(max(0, min(decay_score, base_score)), 2)

    @staticmethod
    def calculate_cosine_similarity(
        vector_a: List[float],
        vector_b: List[float]
    ) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vector_a: 向量A
            vector_b: 向量B
            
        Returns:
            相似度分数（0-1）
        """
        if len(vector_a) != len(vector_b):
            raise ValueError("向量维度必须相同")
        
        if not vector_a or not vector_b:
            return 0.0
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        
        # 计算模
        magnitude_a = math.sqrt(sum(a ** 2 for a in vector_a))
        magnitude_b = math.sqrt(sum(b ** 2 for b in vector_b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        # 余弦相似度
        cosine_sim = dot_product / (magnitude_a * magnitude_b)
        
        return round(cosine_sim, 3)

    @staticmethod
    def calculate_jaccard_similarity(
        set_a: Set,
        set_b: Set
    ) -> float:
        """
        计算两个集合的杰卡德相似度
        
        Args:
            set_a: 集合A
            set_b: 集合B
            
        Returns:
            相似度分数（0-1）
        """
        if not set_a and not set_b:
            return 1.0
        
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        if union == 0:
            return 0.0
        
        return round(intersection / union, 3)

    @staticmethod
    def weighted_fusion(
        scores: Dict[str, float],
        weights: Dict[str, float],
        normalize: bool = True
    ) -> float:
        """
        多因子加权融合分数
        
        Args:
            scores: 各维度的分数 {'content_match': 80, 'hotness': 60, ...}
            weights: 各维度的权重 {'content_match': 0.4, 'hotness': 0.2, ...}
            normalize: 是否对最终分数进行归一化（除以权重总和）
            
        Returns:
            融合后的总分
        """
        if not scores or not weights:
            return 0.0
        
        # 验证权重
        total_weight = sum(weights.values())
        if total_weight <= 0:
            return 0.0
        
        # 计算加权分
        total_score = 0.0
        for key, score in scores.items():
            weight = weights.get(key, 0.0)
            total_score += score * weight
        
        # 归一化（如果权重和不为1）
        if normalize and total_weight != 1.0:
            total_score = total_score / total_weight
        
        return round(total_score, 2)

    @staticmethod
    def normalize_score(
        score: float,
        min_val: float = 0.0,
        max_val: float = 100.0
    ) -> float:
        """
        将分数归一化到指定范围
        
        Args:
            score: 原始分数
            min_val: 目标范围最小值
            max_val: 目标范围最大值
            
        Returns:
            归一化后的分数
        """
        normalized = max(min_val, min(max_val, score))
        return round(normalized, 2)

    @staticmethod
    def grade_match_score(
        user_grade: str,
        target_grades: List[str]
    ) -> float:
        """
        计算用户年级与活动目标年级的匹配分数
        
        Args:
            user_grade: 用户年级（如"大一"、"大二"）
            target_grades: 活动面向的目标年级列表
            
        Returns:
            匹配分数（0-100），完全匹配返回100，部分匹配返回50，无匹配返回0
        """
        if not user_grade or not target_grades:
            return 50.0  # 缺少信息时返回中等分数
        
        if user_grade in target_grades:
            return 100.0
        
        return 0.0

    @staticmethod
    def time_proximity_score(
        activity_start_time: datetime,
        days_ahead: int = 30
    ) -> float:
        """
        计算活动时间接近度分数（活动越接近现在越高分）
        
        Args:
            activity_start_time: 活动开始时间
            days_ahead: 参考天数范围（超出此范围的活动得分较低）
            
        Returns:
            接近度分数（0-100）
        """
        now = datetime.now()
        activity_start_time = ScoringUtils._remove_timezone(activity_start_time)
        
        # 如果活动已结束
        if activity_start_time <= now:
            return 0.0
        
        # 计算距离天数
        days_diff = (activity_start_time - now).days
        
        # 在days_ahead范围内，线性递减
        if days_diff <= days_ahead:
            score = (1.0 - days_diff / days_ahead) * 100
        else:
            # 超出范围的活动低分
            score = 20.0
        
        return round(max(0, score), 2)

    @staticmethod
    def behavioral_engagement_score(
        view_count: int,
        registration_count: int,
        attended_count: int,
        view_weight: float = 0.2,
        registration_weight: float = 0.3,
        attended_weight: float = 0.5
    ) -> float:
        """
        基于用户行为的参与度评分
        
        Args:
            view_count: 浏览次数
            registration_count: 报名次数
            attended_count: 参加次数
            view_weight: 浏览权重
            registration_weight: 报名权重
            attended_weight: 参加权重
            
        Returns:
            参与度评分（0-100）
        """
        # 标准化各个指标
        view_score = min(view_count / 50.0, 1.0) * 100  # 50次浏览为满分
        registration_score = min(registration_count / 20.0, 1.0) * 100  # 20次报名为满分
        attended_score = min(attended_count / 10.0, 1.0) * 100  # 10次参加为满分
        
        # 加权融合
        engagement_score = (
            view_score * view_weight +
            registration_score * registration_weight +
            attended_score * attended_weight
        )
        
        return round(engagement_score, 2)

    @staticmethod
    def _remove_timezone(dt: datetime) -> datetime:
        """
        移除datetime的时区信息
        
        Args:
            dt: datetime对象
            
        Returns:
            无时区的datetime对象
        """
        if dt and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
