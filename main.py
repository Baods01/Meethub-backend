from fastapi import FastAPI,APIRouter
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM
from tests.app01 import UserApp,RoleApp 

app00 = APIRouter()

@app00.get("/")
async def get():
    return {"message": "Hello World"}

app = FastAPI()
app.include_router(app00,tags=["App01"])
app.include_router(UserApp,tags=["UserApp"])
app.include_router(RoleApp,tags=["RoleApp"])

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)
