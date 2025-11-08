from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Activities(models.Model):
    """活动模型"""
    id = fields.IntField(pk=True, description="活动ID")
    title = fields.CharField(max_length=100, description="活动名称")
    description = fields.TextField(description="活动简介")
    cover_image = fields.CharField(max_length=255, description="封面图片URL")
    location = fields.CharField(max_length=255, description="活动地点")
    start_time = fields.DatetimeField(description="活动开始时间")
    end_time = fields.DatetimeField(description="活动结束时间")
    max_participants = fields.IntField(description="招募人数上限")
    current_participants = fields.IntField(default=0, description="当前报名人数")
    tags = fields.JSONField(description="活动标签", default=list)
    target_audience = fields.JSONField(description="面向人群(专业/年级)", default=dict)
    benefits = fields.JSONField(description="活动收益(志愿时/综测等)", default=dict)
    status = fields.CharField(
        max_length=20,
        description="活动状态",
        default="draft"  # draft-草稿, published-已发布, ongoing-进行中, ended-已结束, cancelled-已取消
    )
    views_count = fields.IntField(default=0, description="浏览量")
    is_deleted = fields.BooleanField(default=False, description="是否删除")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    # 与用户的外键关系（发布者）
    publisher = fields.ForeignKeyField(
        'models.Users',
        related_name='published_activities',
        description="活动发布者"
    )

    # 与报名表的反向关系
    registrations = fields.ReverseRelation['Registrations']

    def __str__(self):
        return f"{self.title}"

    class Meta:
        table = "activities"
        table_description = "活动表"

# 创建Pydantic模型
ActivityPydantic = pydantic_model_creator(Activities, name="Activity")
ActivityInPydantic = pydantic_model_creator(Activities, name="ActivityIn", exclude_readonly=True)