from typing import Optional, List
from passlib.hash import bcrypt
from tortoise.exceptions import DoesNotExist
from models.users import Users
from .base import BaseDAO


class UserDAO(BaseDAO[Users]):
    """用户数据访问对象"""

    def __init__(self):
        super().__init__(Users)

    async def create_user(self, user_data: dict) -> Optional[Users]:
        """
        创建用户
        :param user_data: 用户数据字典
        :return: 创建的用户对象
        """
        # 对密码进行哈希处理
        if "password" in user_data:
            user_data["password"] = bcrypt.hash(user_data["password"])
        
        try:
            return await self.create(**user_data)
        except Exception as e:
            # 这里可以添加日志记录
            print(f"创建用户失败: {str(e)}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[Users]:
        """
        通过邮箱获取用户
        :param email: 用户邮箱
        :return: 用户对象或None
        """
        try:
            return await Users.get(email=email)
        except DoesNotExist:
            return None

    async def get_user_by_username(self, username: str) -> Optional[Users]:
        """
        通过用户名获取用户
        :param username: 用户名
        :return: 用户对象或None
        """
        try:
            return await Users.get(username=username)
        except DoesNotExist:
            return None

    async def update_user(self, user_id: int, update_data: dict) -> Optional[Users]:
        """
        更新用户信息
        :param user_id: 用户ID
        :param update_data: 更新数据字典
        :return: 更新后的用户对象或None
        """
        if "password" in update_data:
            update_data["password"] = bcrypt.hash(update_data["password"])
        
        return await self.update(user_id, **update_data)

    async def add_user_role(self, user_id: int, role_id: int) -> bool:
        """
        为用户添加角色
        :param user_id: 用户ID
        :param role_id: 角色ID
        :return: 是否添加成功
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            # 使用 Tortoise-ORM 的多对多关系方法
            await user.roles.add(role_id)
            return True
        except Exception as e:
            print(f"添加用户角色失败: {str(e)}")
            return False

    async def remove_user_role(self, user_id: int, role_id: int) -> bool:
        """
        移除用户的角色
        :param user_id: 用户ID
        :param role_id: 角色ID
        :return: 是否移除成功
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            await user.roles.remove(role_id)
            return True
        except Exception as e:
            print(f"移除用户角色失败: {str(e)}")
            return False

    async def verify_password(self, user: Users, password: str) -> bool:
        """
        验证用户密码
        :param user: 用户对象
        :param password: 待验证的密码
        :return: 密码是否正确
        """
        return bcrypt.verify(password, user.password)

    async def get_user_roles(self, user_id: int) -> List[dict]:
        """
        获取用户的所有角色
        :param user_id: 用户ID
        :return: 角色列表
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return []
            
            roles = await user.roles.all()
            return [{"id": role.id, "name": role.name, "code": role.code} for role in roles]
        except Exception as e:
            print(f"获取用户角色失败: {str(e)}")
            return []