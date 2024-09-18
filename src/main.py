from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.controllers.user import add_user, auth_user, delete_user
from src.models import User, Auth, MyException
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

# This route will authenticate a user
@app.post("/auth", status_code=201)
async def auth_route(auth: Auth):
    # This is a dummy function that will always return a 401
    return auth_user(auth.login, auth.password)

# This route will delete a user from the database
@app.delete("/user/{id}", status_code=204)
async def delete_user_route(id: int):
    return delete_user(id)
