from fastapi import FastAPI, APIRouter, Request, Response
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM
from fastapi.security import HTTPBearer
from routers.auth import router as auth_router
from routers.admin import router as admin_router
from routers.users import router as users_router
from routers.activities import router as activities_router
from routers.registrations import router as registrations_router
from routers.uploads import router as uploads_router
from fastapi.staticfiles import StaticFiles

# from apps.app01 import UserApp,RoleApp
# from apps.app00 import app00
# from apps.user_dtest import UserDTestApp
# from apps.roles_dtest import RoleDTestApp
# from apps.auth import router as AuthRouter
# from apps.app02 import router as TestAuthRouter

app = FastAPI(
    title="Meethub API",
    description="Meethub 后端 API 文档",
    version="1.0.0",
    openapi_tags=[
        {"name": "认证", "description": "认证相关接口"},
        {"name": "管理员", "description": "管理员相关接口"},
        {"name": "用户", "description": "用户相关接口"},
        {"name": "活动", "description": "活动相关接口"},
        {"name": "报名", "description": "报名相关接口"},
        {"name": "文件", "description": "文件相关接口"},
    ]
)
# app.include_router(app00,tags=["App01"])
# app.include_router(UserApp,tags=["UserApp"])
# app.include_router(RoleApp,tags=["RoleApp"])
# app.include_router(UserDTestApp,tags=["UserDTestApp"])
# app.include_router(RoleDTestApp,tags=["RoleDTestApp"],prefix='/roledtest')
# app.include_router(AuthRouter)
# app.include_router(TestAuthRouter)

@app.middleware("http")
async def MyCORSHandler(request: Request, call_next):
    """
    自定义CORS中间件，处理跨域请求
    """
    if request.method == "OPTIONS":
        # 处理预检请求
        response = Response()
    else:
        response = await call_next(request)
    
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"  # 预检请求缓存时间
    
    return response

# 引入所有路由

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(activities_router)
app.include_router(registrations_router)
app.include_router(uploads_router)

# 挂载静态文件目录以便直接访问上传的文件
app.mount("/static", StaticFiles(directory="static"), name="static")

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

if __name__ == "__main__":
    uvicorn.run("main:app",host="26.35.145.219",port=8080,reload=True)
