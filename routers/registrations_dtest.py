from fastapi import APIRouter, HTTPException
from typing import Optional
from schemas.registrations import RegistrationCreate, RegistrationUpdate, RegistrationInDB, RegistrationList
from dao.registration_dao import RegistrationDAO
from dao.activity_dao import ActivityDAO

router = APIRouter(
    prefix="/dtest/registrations",
    tags=["报名测试"]
)


@router.post("/create", response_model=RegistrationInDB)
async def create_registration_test(registration: RegistrationCreate):
    """测试创建报名记录"""
    try:
        # 使用模拟的参与者ID (2)
        dao = RegistrationDAO()
        
        # 先检查活动是否存在
        activity_dao = ActivityDAO()
        activity = await activity_dao.get_by_id(registration.activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
            
        # 创建报名记录
        created = await dao.create_registration(
            activity_id=registration.activity_id,
            participant_id=12,  # 使用ID为2的用户作为测试参与者
            data=registration.model_dump(exclude={'activity_id'})
        )
        
        if not created:
            raise HTTPException(status_code=400, detail="已经报名过该活动")
            
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{registration_id}")
async def cancel_registration_test(registration_id: int):
    """测试取消报名"""
    try:
        dao = RegistrationDAO()
        # 获取报名记录详情以获取活动ID
        registration = await dao.get_registration_detail(registration_id)
        if not registration:
            raise HTTPException(status_code=404, detail="报名记录不存在")
            
        # 更新状态为已取消
        updated = await dao.update_registration_status(
            registration_id=registration_id,
            status="cancelled",
            activity_id=registration.activity.id
        )
        
        return {"message": "报名已取消"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{registration_id}", response_model=RegistrationInDB)
async def get_registration_test(registration_id: int):
    """测试获取报名详情"""
    try:
        dao = RegistrationDAO()
        registration = await dao.get_registration_detail(registration_id)
        if not registration:
            raise HTTPException(status_code=404, detail="报名记录不存在")
        return registration
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{registration_id}/check-in")
async def check_in_test(registration_id: int):
    """测试签到"""
    try:
        dao = RegistrationDAO()
        registration = await dao.check_in(registration_id)
        if not registration:
            raise HTTPException(status_code=404, detail="报名记录不存在或未通过审核")
        return {"message": "签到成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{registration_id}/check-out")
async def check_out_test(
    registration_id: int,
    feedback: Optional[str] = None,
    rating: Optional[int] = None
):
    """测试签退"""
    try:
        dao = RegistrationDAO()
        registration = await dao.check_out(
            registration_id=registration_id,
            feedback=feedback,
            rating=rating
        )
        if not registration:
            raise HTTPException(status_code=404, detail="报名记录不存在或未签到")
        return {"message": "签退成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))