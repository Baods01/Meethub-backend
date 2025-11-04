from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from models.roles import Roles
from .base import BaseDAO


class RoleDAO(BaseDAO[Roles]):
    """角色数据访问对象"""

    def __init__(self):
        super().__init__(Roles)

    async def create_role(self, role_data: dict) -> Optional[Roles]:
        """
        创建角色
        :param role_data: 角色数据字典
        :return: 创建的角色对象
        """
        try:
            return await self.create(**role_data)
        except Exception as e:
            print(f"创建角色失败: {str(e)}")
            return None

    async def get_role_by_name(self, name: str) -> Optional[Roles]:
        """
        通过名称获取角色
        :param name: 角色名称
        :return: 角色对象或None
        """
        try:
            return await Roles.get(name=name)
        except DoesNotExist:
            return None

    async def get_role_by_code(self, code: str) -> Optional[Roles]:
        """
        通过编码获取角色
        :param code: 角色编码
        :return: 角色对象或None
        """
        try:
            return await Roles.get(code=code)
        except DoesNotExist:
            return None

    async def get_active_roles(self) -> List[Roles]:
        """
        获取所有激活的角色
        :return: 角色列表
        """
        return await Roles.filter(is_active=True).all()

    async def update_role_permissions(self, role_id: int, permissions: List[str]) -> Optional[Roles]:
        """
        更新角色权限
        :param role_id: 角色ID
        :param permissions: 权限列表
        :return: 更新后的角色对象
        """
        try:
            role = await self.get_by_id(role_id)
            if not role:
                return None
            
            return await self.update(role_id, permissions=permissions)
        except Exception as e:
            print(f"更新角色权限失败: {str(e)}")
            return None

    async def get_roles_by_ids(self, role_ids: List[int]) -> List[Roles]:
        """
        通过ID列表批量获取角色
        :param role_ids: 角色ID列表
        :return: 角色列表
        """
        return await Roles.filter(id__in=role_ids).all()

    async def toggle_role_status(self, role_id: int, is_active: bool) -> Optional[Roles]:
        """
        切换角色状态
        :param role_id: 角色ID
        :param is_active: 是否激活
        :return: 更新后的角色对象
        """
        return await self.update(role_id, is_active=is_active)