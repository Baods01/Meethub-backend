from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Roles(models.Model):
    """角色模型"""
    id = fields.IntField(pk=True, description="角色ID")
    name = fields.CharField(max_length=50, unique=True, description="角色名称")
    code = fields.CharField(max_length=50, unique=True, description="角色编码")
    description = fields.TextField(null=True, description="角色描述")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    permissions = fields.JSONField(null=True, description="权限列表")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        table = "roles"
        table_description = "角色表"

# 创建Pydantic模型
RolePydantic = pydantic_model_creator(Roles, name="Role")
RoleInPydantic = pydantic_model_creator(Roles, name="RoleIn", exclude_readonly=True)