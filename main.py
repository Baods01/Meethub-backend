from fastapi import FastAPI,APIRouter
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM

app01 = APIRouter()

@app01.get("/")
async def get():
    return {"message": "Hello World"}

app = FastAPI()
app.include_router(app01,tags=["App01"])

register_tortoise(
    app,
    config=TORTOISE_ORM,
)

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)
