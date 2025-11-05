from fastapi import APIRouter, HTTPException
from typing import List, Optional
from dao.role_dao import RoleDAO
from schemas.roles import RoleCreate, RoleResponse, RoleUpdate
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RoleDTestApp = APIRouter()
role_dao = RoleDAO()

@RoleDTestApp.post("/create", response_model=RoleResponse)
async def test_create_role(role: RoleCreate):
    """测试创建角色"""
    logger.info(f"开始测试创建角色: {role.name}")
    
    # 创建角色
    role_dict = role.model_dump()
    created_role = await role_dao.create_role(role_dict)
    assert created_role is not None, "角色创建失败"
    logger.info(f"角色创建成功: ID={created_role.id}")
    
    return created_role

@RoleDTestApp.get("/get/{role_id}", response_model=RoleResponse)
async def test_get_role(role_id: int):
    """测试按ID获取角色"""
    logger.info(f"开始测试获取角色: ID={role_id}")
    
    # 获取角色
    role = await role_dao.get_by_id(role_id)
    assert role is not None, f"未找到ID为{role_id}的角色"
    logger.info(f"成功获取角色: {role.name}")
    
    return role

@RoleDTestApp.get("/all", response_model=List[RoleResponse])
async def test_get_all_roles():
    """测试获取所有角色"""
    logger.info("开始测试获取所有角色")
    
    # 获取所有角色
    roles = await role_dao.get_all()
    assert roles is not None, "获取角色列表失败"
    logger.info(f"成功获取角色列表，共{len(roles)}条记录")
    
    return roles

@RoleDTestApp.put("/update/{role_id}", response_model=RoleResponse)
async def test_update_role(role_id: int, role_update: RoleUpdate):
    """测试更新角色"""
    logger.info(f"开始测试更新角色: ID={role_id}")
    
    # 更新前检查角色是否存在
    original_role = await role_dao.get_by_id(role_id)
    assert original_role is not None, f"未找到ID为{role_id}的角色"
    
    # 更新角色
    update_data = {k: v for k, v in role_update.model_dump().items() if v is not None}
    updated_role = await role_dao.update(role_id, **update_data)
    assert updated_role is not None, "角色更新失败"
    logger.info(f"角色更新成功: {updated_role.name}")
    
    return updated_role

@RoleDTestApp.delete("/delete/{role_id}")
async def test_delete_role(role_id: int):
    """测试删除角色"""
    logger.info(f"开始测试删除角色: ID={role_id}")
    
    # 删除前检查角色是否存在
    role = await role_dao.get_by_id(role_id)
    assert role is not None, f"未找到ID为{role_id}的角色"
    
    # 删除角色
    is_deleted = await role_dao.delete(role_id)
    assert is_deleted is True, "角色删除失败"
    logger.info(f"角色删除成功: ID={role_id}")
    
    return {"message": "角色删除成功", "role_id": role_id}