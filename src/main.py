from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.controllers.user import add_user, auth_user, delete_user, update_user, get_users
from src.controllers.token import verify_token
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

# # authentification middleware
# @app.middleware("http")
# async def auth_middleware(request: Request, call_next):
#     if request.url.path == "/auth":
#         return await call_next(request)

#     if request.headers.get("Authorization") == "Bearer token":
#         response = await call_next(request)
#         return response

# This is the root route
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
async def delete_user_route(id: int, request: Request):
    verify_token(request.headers.get("Authorization"), id)
    return delete_user(id)

@app.put("/user/{id}", status_code=200)
async def update_user_route(id: int, user: User, request: Request):
    verify_token(request.headers.get("Authorization"), id)
    return update_user(id, user)

@app.get("/users", status_code=200)
async def get_users_route():
    return get_users()
