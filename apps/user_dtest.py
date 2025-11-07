from fastapi import APIRouter, HTTPException
from typing import List, Optional
from dao.user_dao import UserDAO
from dao.role_dao import RoleDAO
import schemas.users as schemas

UserDTestApp = APIRouter()
user_dao = UserDAO()
role_dao = RoleDAO()

class TestResponse(schemas.BaseModel):
    """测试响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None

@UserDTestApp.post("/dtest/create", response_model=TestResponse)
async def test_create_user(user: schemas.UserCreate):
    """测试创建用户"""
    try:
        print("\n=== 测试创建用户 ===")
        created_user = await user_dao.create_user(user.dict())
        if created_user:
            # 获取普通用户角色并分配给新用户
            normal_role = await role_dao.get_role_by_code("normal_user")
            if normal_role:
                await user_dao.add_user_role(created_user.id, normal_role.id)
                print(f"✓ 成功创建用户并分配普通用户角色: ID={created_user.id}, Username={created_user.username}")
            else:
                print(f"警告: 未找到普通用户角色，仅创建用户: ID={created_user.id}")
            
            return TestResponse(
                success=True,
                message="用户创建成功",
                data={"user_id": created_user.id}
            )
        return TestResponse(
            success=False,
            message="用户创建失败",
            error="数据库操作失败"
        )
    except Exception as e:
        print(f"✗ 创建用户失败: {str(e)}")
        return TestResponse(
            success=False,
            message="用户创建失败",
            error=str(e)
        )

@UserDTestApp.get("/dtest/query/{user_id}", response_model=TestResponse)
async def test_query_user(user_id: int):
    """测试查询用户"""
    try:
        print(f"\n=== 测试查询用户 (ID: {user_id}) ===")
        user = await user_dao.get_by_id(user_id)
        if user:
            print(f"✓ 成功查询到用户: Username={user.username}")
            return TestResponse(
                success=True,
                message="用户查询成功",
                data={"user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active
                }}
            )
        print(f"✗ 未找到用户: ID={user_id}")
        return TestResponse(
            success=False,
            message=f"未找到ID为{user_id}的用户",
            error="用户不存在"
        )
    except Exception as e:
        print(f"✗ 查询用户失败: {str(e)}")
        return TestResponse(
            success=False,
            message="查询用户失败",
            error=str(e)
        )

@UserDTestApp.get("/dtest/list", response_model=TestResponse)
async def test_list_users():
    """测试获取所有用户列表"""
    try:
        print("\n=== 测试获取用户列表 ===")
        users = await user_dao.get_all()
        users_data = [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active
        } for user in users]
        print(f"✓ 成功获取用户列表: 共{len(users)}条记录")
        return TestResponse(
            success=True,
            message="获取用户列表成功",
            data={"users": users_data}
        )
    except Exception as e:
        print(f"✗ 获取用户列表失败: {str(e)}")
        return TestResponse(
            success=False,
            message="获取用户列表失败",
            error=str(e)
        )

@UserDTestApp.put("/dtest/update/{user_id}", response_model=TestResponse)
async def test_update_user(user_id: int, user_update: schemas.UserUpdate):
    """测试更新用户"""
    try:
        print(f"\n=== 测试更新用户 (ID: {user_id}) ===")
        # 先检查用户是否存在
        existing_user = await user_dao.get_by_id(user_id)
        if not existing_user:
            print(f"✗ 更新失败: 未找到ID为{user_id}的用户")
            return TestResponse(
                success=False,
                message=f"未找到ID为{user_id}的用户",
                error="用户不存在"
            )
            
        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        updated_user = await user_dao.update_user(user_id, update_data)
        if updated_user:
            print(f"✓ 成功更新用户: ID={updated_user.id}")
            return TestResponse(
                success=True,
                message="用户更新成功",
                data={"user": {
                    "id": updated_user.id,
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "is_active": updated_user.is_active
                }}
            )
        return TestResponse(
            success=False,
            message="用户更新失败",
            error="数据库操作失败"
        )
    except Exception as e:
        print(f"✗ 更新用户失败: {str(e)}")
        return TestResponse(
            success=False,
            message="更新用户失败",
            error=str(e)
        )

@UserDTestApp.delete("/dtest/delete/{user_id}", response_model=TestResponse)
async def test_delete_user(user_id: int):
    """测试删除用户"""
    try:
        print(f"\n=== 测试删除用户 (ID: {user_id}) ===")
        # 先检查用户是否存在
        existing_user = await user_dao.get_by_id(user_id)
        if not existing_user:
            print(f"✗ 删除失败: 未找到ID为{user_id}的用户")
            return TestResponse(
                success=False,
                message=f"未找到ID为{user_id}的用户",
                error="用户不存在"
            )
            
        # 删除用户
        deleted = await user_dao.delete(user_id)
        if deleted:
            print(f"✓ 成功删除用户: ID={user_id}")
            return TestResponse(
                success=True,
                message="用户删除成功",
                data={"user_id": user_id}
            )
        return TestResponse(
            success=False,
            message="用户删除失败",
            error="数据库操作失败"
        )
    except Exception as e:
        print(f"✗ 删除用户失败: {str(e)}")
        return TestResponse(
            success=False,
            message="删除用户失败",
            error=str(e)
        )

@UserDTestApp.post("/dtest/assign_role/{user_id}/{role_code}", response_model=TestResponse)
async def test_assign_role(user_id: int, role_code: str):
    """测试为用户分配角色
    role_code可选值: super_admin, organizer, normal_user
    """
    try:
        print(f"\n=== 测试为用户分配角色 (用户ID: {user_id}, 角色代码: {role_code}) ===")
        
        # 验证角色代码是否有效
        valid_role_codes = ["super_admin", "organizer", "normal_user"]
        if role_code not in valid_role_codes:
            print(f"✗ 无效的角色代码: {role_code}")
            return TestResponse(
                success=False,
                message="无效的角色代码",
                error=f"角色代码必须是以下之一: {', '.join(valid_role_codes)}"
            )
        
        # 检查用户是否存在
        user = await user_dao.get_by_id(user_id)
        if not user:
            print(f"✗ 未找到用户: ID={user_id}")
            return TestResponse(
                success=False,
                message=f"未找到ID为{user_id}的用户",
                error="用户不存在"
            )
        
        # 获取角色
        role = await role_dao.get_role_by_code(role_code)
        if not role:
            print(f"✗ 未找到角色: code={role_code}")
            return TestResponse(
                success=False,
                message=f"未找到角色代码为{role_code}的角色",
                error="角色不存在"
            )
        
        # 分配角色
        success = await user_dao.add_user_role(user_id, role.id)
        if success:
            print(f"✓ 成功为用户分配角色: User={user.username}, Role={role.name}")
            # 获取用户当前的所有角色
            current_roles = await user_dao.get_user_roles(user_id)
            return TestResponse(
                success=True,
                message=f"成功为用户分配角色: {role.name}",
                data={
                    "user_id": user_id,
                    "role_id": role.id,
                    "role_name": role.name,
                    "current_roles": current_roles
                }
            )
        
        print(f"✗ 角色分配失败")
        return TestResponse(
            success=False,
            message="角色分配失败",
            error="数据库操作失败"
        )
        
    except Exception as e:
        print(f"✗ 分配角色时发生错误: {str(e)}")
        return TestResponse(
            success=False,
            message="分配角色失败",
            error=str(e)
        )

@UserDTestApp.get("/dtest/user_roles/{user_id}", response_model=TestResponse)
async def test_get_user_roles(user_id: int):
    """测试获取用户的所有角色"""
    try:
        print(f"\n=== 测试获取用户角色 (用户ID: {user_id}) ===")
        
        # 检查用户是否存在
        user = await user_dao.get_by_id(user_id)
        if not user:
            print(f"✗ 未找到用户: ID={user_id}")
            return TestResponse(
                success=False,
                message=f"未找到ID为{user_id}的用户",
                error="用户不存在"
            )
        
        # 获取用户的所有角色
        roles = await user_dao.get_user_roles(user_id)
        print(f"✓ 成功获取用户角色: User={user.username}, Roles={[role['name'] for role in roles]}")
        
        return TestResponse(
            success=True,
            message="成功获取用户角色",
            data={
                "user_id": user_id,
                "username": user.username,
                "roles": roles
            }
        )
        
    except Exception as e:
        print(f"✗ 获取用户角色时发生错误: {str(e)}")
        return TestResponse(
            success=False,
            message="获取用户角色失败",
            error=str(e)
        )