from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Registrations(models.Model):
    """活动报名模型"""
    id = fields.IntField(pk=True, description="报名ID")
    registration_time = fields.DatetimeField(auto_now_add=True, description="报名时间")
    status = fields.CharField(
        max_length=20,
        description="报名状态",
        default="pending"  # pending-待审核, approved-已通过, rejected-已拒绝, cancelled-已取消
    )
    comment = fields.TextField(null=True, description="报名备注")
    additional_info = fields.JSONField(null=True, description="附加信息", default=dict)
    check_in_time = fields.DatetimeField(null=True, description="签到时间")
    check_out_time = fields.DatetimeField(null=True, description="签退时间")
    feedback = fields.TextField(null=True, description="活动反馈")
    rating = fields.IntField(null=True, description="活动评分(1-5)")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    # 与用户的外键关系（报名者）
    participant = fields.ForeignKeyField(
        'models.Users',
        related_name='registrations',
        description="报名者"
    )

    # 与活动的外键关系
    activity = fields.ForeignKeyField(
        'models.Activities',
        related_name='registrations',
        description="所属活动"
    )

    def __str__(self):
        return f"Registration {self.id} for {self.activity}"

    class Meta:
        table = "registrations"
        table_description = "活动报名表"
        unique_together = [("participant", "activity")]  # 确保每个用户只能报名一次

# 创建Pydantic模型
RegistrationPydantic = pydantic_model_creator(Registrations, name="Registration")
RegistrationInPydantic = pydantic_model_creator(Registrations, name="RegistrationIn", exclude_readonly=True)