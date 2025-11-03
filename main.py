from fastapi import FastAPI

@app.get("/")
async def get():
    return {"message": "Hello World"}

print("hello world")
