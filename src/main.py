from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.controllers.user import add_user
from src.models import User, MyException
app = FastAPI()

# Exception handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: MyException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
        },
    )

@app.get("/")
async def root():
    return {
        "message": "Hello World",
    }

# This route will add a user to the database
@app.post("/user", status_code=201)
async def add_user_route(user: User):
    return add_user(user)
        