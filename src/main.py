from fastapi import FastAPI
from src.controllers.user import add_user

app = FastAPI()

@app.get("/")
async def root():
    add_user()
    return {
        "message": "Hello World",
    }
