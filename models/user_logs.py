from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class UserOperationLogs(models.Model):
    """用户操作日志模型"""
    id = fields.IntField(pk=True, description="日志ID")
    
    # 用户和活动的外键关系
    user = fields.ForeignKeyField(
        'models.Users',
        related_name='operation_logs',
        description="操作用户"
    )
    
    activity = fields.ForeignKeyField(
        'models.Activities',
        related_name='user_logs',
        null=True,
        on_delete=fields.CASCADE,
        description="关联活动（可选，某些操作不涉及活动）"
    )
    
    # 操作类型：view_activity（浏览活动）、register_activity（报名活动）
    operation_type = fields.CharField(
        max_length=50,
        description="操作类型",
        index=True
    )
    
    # 时间戳
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="操作时间",
        index=True
    )
    
    # 附加数据，用于存储操作的额外信息
    # 例如：浏览时长、报名时的参数、ip地址等
    extra_data = fields.JSONField(
        null=True,
        default=dict,
        description="附加数据(JSON格式，用于扩展信息)"
    )

    def __str__(self):
        return f"Log {self.id}: {self.user.username} - {self.operation_type} - Activity {self.activity.id}"

    class Meta:
        table = "user_operation_logs"
        table_description = "用户操作日志表"
        # 创建复合索引以优化查询性能
        indexes = [
            ("user_id", "operation_type", "created_at"),
            ("activity_id", "operation_type"),
            ("user_id", "created_at")
        ]


# 创建Pydantic模型
UserOperationLogPydantic = pydantic_model_creator(
    UserOperationLogs,
    name="UserOperationLog"
)
UserOperationLogInPydantic = pydantic_model_creator(
    UserOperationLogs,
    name="UserOperationLogIn",
    exclude_readonly=True
)
