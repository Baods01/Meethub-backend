from fastapi import FastAPI,APIRouter
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM

from apps.app01 import UserApp,RoleApp
from apps.app00 import app00
from apps.user_dtest import UserDTestApp

app = FastAPI()
app.include_router(app00,tags=["App01"])
app.include_router(UserApp,tags=["UserApp"])
app.include_router(RoleApp,tags=["RoleApp"])
app.include_router(UserDTestApp,tags=["UserDTestApp"])

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)
