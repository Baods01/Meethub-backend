from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
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
from routers.user_logs import router as user_logs_router
from fastapi.staticfiles import StaticFiles

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
        {"name": "日志", "description": "用户操作日志相关接口"},
    ]
)

# 配置CORS中间件
# 这个中间件能够正确处理预检请求，并对所有路由（包括静态文件）应用CORS头
# 可以让分离部署的网站访问后端的静态文件和API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源（生产环境应该限制具体的域名）
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],  # 暴露所有响应头
    max_age=3600,  # 预检请求缓存时间（秒）
)

# 引入所有路由

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(activities_router)
app.include_router(registrations_router)
app.include_router(uploads_router)
app.include_router(user_logs_router)

# 挂载静态文件目录以便直接访问上传的文件
app.mount("/static", StaticFiles(directory="static"), name="static")

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)
