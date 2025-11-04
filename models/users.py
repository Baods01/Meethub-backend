from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    """用户模型"""
    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password = fields.CharField(max_length=128, description="密码")
    email = fields.CharField(max_length=255, unique=True, null=True, description="邮箱")
    phone = fields.CharField(max_length=11, unique=True, null=True, description="手机号")
    avatar = fields.CharField(max_length=255, null=True, description="头像URL")
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    bio = fields.TextField(null=True, description="个人简介")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_verified = fields.BooleanField(default=False, description="是否验证")
    created_at = fields.DatetimeField(default='2025-01-01',auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(default='2025-01-01',auto_now=True, description="更新时间")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")

    # 与角色的多对多关系
    roles = fields.ManyToManyField(
        'models.Roles',
        related_name='users',
        through='user_roles',
        description="用户角色"
    )

    def __str__(self):
        return f"{self.username}"

    class Meta:
        table = "users"
        table_description = "用户表"

# 创建Pydantic模型
UserPydantic = pydantic_model_creator(Users, name="User")
UserInPydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)