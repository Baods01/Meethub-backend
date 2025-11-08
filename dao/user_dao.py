from typing import Optional, List
import bcrypt
from tortoise.exceptions import DoesNotExist
from models.users import Users
from .base import BaseDAO


class UserDAO(BaseDAO[Users]):
    """用户数据访问对象"""

    def __init__(self):
        """初始化用户 DAO"""
        super().__init__(model=Users)

    async def create_user(self, user_data: dict) -> Optional[Users]:
        """
        创建用户
        :param user_data: 用户数据字典
        :return: 创建的用户对象
        """
        # 检查密码长度并进行哈希处理
        if "password" in user_data:
            try:
                # 将密码编码为字节
                password = user_data["password"]
                password_bytes = password.encode('utf-8')
                
                # 检查并截断密码（bcrypt的72字节限制）
                if len(password_bytes) > 72:
                    print(f"警告: 密码超过72字节限制，已自动截断: {len(password_bytes)} -> 72 bytes")
                    password_bytes = password_bytes[:72]
                
                # 直接使用bcrypt进行哈希
                hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                
                # 将字节转换为字符串存储
                user_data["password"] = hashed_password.decode('utf-8')
                
            except Exception as e:
                print(f"密码哈希处理失败: {str(e)}")
                return None
        
        try:
            return await self.create(**user_data)
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            # 打印用户数据时排除密码
            user_data_debug = user_data.copy()
            if "password" in user_data_debug:
                user_data_debug["password"] = "***HIDDEN***"
            print(f"用户数据: {user_data_debug}")
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

    async def get_user_by_phone(self, phone: str) -> Optional[Users]:
        """
        通过手机号获取用户
        :param phone: 用户手机号
        :return: 用户对象或None
        """
        try:
            return await Users.get(phone=phone)
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
            password_bytes = update_data["password"].encode('utf-8')
            if len(password_bytes) > 72:
                print("密码长度超过72字节限制")
                return None
            update_data["password"] = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        
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
            
            # 从models.Roles导入Roles模型
            from models.roles import Roles
            role = await Roles.get(id=role_id)
            if not role:
                return False
            
            # 使用 Tortoise-ORM 的多对多关系方法
            await user.roles.add(role)
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
        try:
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            stored_password = user.password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, stored_password)
        except Exception as e:
            print(f"密码验证失败: {str(e)}")
            return False

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