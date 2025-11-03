from fastapi import FastAPI,APIRouter
import uvicorn

app01 = APIRouter()

@app01.get("/")
async def get():
    return {"message": "Hello World"}

app = FastAPI()
app.include_router(app01,tags=["App01"])

if __name__ == "__main__":
    uvicorn.run("main:app",port=8080,reload=True)
