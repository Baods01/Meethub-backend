from fastapi import APIRouter, HTTPException
from typing import Optional
from schemas.activities import ActivityCreate, ActivityUpdate, ActivityInDB
from dao.activity_dao import ActivityDAO

router = APIRouter(
    prefix="/dtest/activities",
    tags=["活动测试"]
)


@router.post("/create", response_model=ActivityInDB)
async def create_activity_test(activity: ActivityCreate):
    """测试创建活动"""
    try:
        # 使用模拟的发布者ID (1)
        dao = ActivityDAO()
        created_activity = await dao.create_activity(
            data=activity.model_dump(),
            publisher_id=12  # 使用ID为12的用户作为测试发布者
        )
        return created_activity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{activity_id}", response_model=ActivityInDB)
async def get_activity_test(activity_id: int):
    """测试获取活动详情"""
    try:
        dao = ActivityDAO()
        activity = await dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        return activity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{activity_id}")
async def delete_activity_test(activity_id: int):
    """测试删除活动（软删除）"""
    try:
        dao = ActivityDAO()
        success = await dao.soft_delete(activity_id)
        if not success:
            raise HTTPException(status_code=404, detail="活动不存在")
        return {"message": "活动已删除"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{activity_id}", response_model=ActivityInDB)
async def update_activity_test(activity_id: int, activity: ActivityUpdate):
    """测试更新活动信息"""
    try:
        dao = ActivityDAO()
        # 先检查活动是否存在
        existing = await dao.get_by_id(activity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="活动不存在")
            
        # 更新活动信息
        await dao.update(
            id=activity_id,
            **activity.model_dump(exclude_unset=True)
        )
        
        # 重新获取更新后的活动信息，包含发布者信息
        updated = await dao.get_activity_with_stats(activity_id)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{activity_id}/views")
async def increment_views_test(activity_id: int):
    """测试增加活动浏览量"""
    try:
        dao = ActivityDAO()
        success = await dao.increment_views(activity_id)
        if not success:
            raise HTTPException(status_code=404, detail="活动不存在")
        return {"message": "浏览量已更新"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))