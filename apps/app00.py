from fastapi import APIRouter

app00 = APIRouter()

@app00.get("/")
async def get():
    return {"message": "Hello World"}