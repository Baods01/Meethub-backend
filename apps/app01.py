from fastapi import APIRouter
from schemas.users import *
from schemas.roles import *
from datetime import datetime

UserApp = APIRouter()

@UserApp.post("/users/")
async def read_users(user: UserCreate):
    current_time = datetime.now()
    user_data = user.dict()
    ruser = UserResponse(
        **user_data,
        id=1,
        is_verified=False,
        created_at=current_time,
        updated_at=current_time,
        last_login=None
    )
    return ruser
    
RoleApp = APIRouter()

@RoleApp.post("/roles/")
async def read_roles(role: RoleCreate):
    rrole = RoleResponse(**role.dict(), id=1, created_at=None, updated_at=None)
    return rrole