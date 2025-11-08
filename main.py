from fastapi import FastAPI, APIRouter, Request
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM
from fastapi.security import HTTPBearer
from routers.auth import router as auth_router

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
        {"name": "测试", "description": "测试相关接口"},
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
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# 引入新的认证路由
app.include_router(auth_router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)
