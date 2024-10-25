from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.controllers.user import add_user, auth_user, delete_user, update_user, get_users, get_user_by_id
from src.controllers.token import verify_token
from src.models import User, Auth, MyException, GetUsersItem
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
    return auth_user(auth)

# This route will delete a user from the database
@app.delete("/user/{id}", status_code=204)
async def delete_user_route(id: int, request: Request):
    verify_token(request.headers.get("Authorization"), id)
    return delete_user(id)

# This route will update a user in the database
@app.put("/user/{id}", status_code=200)
async def update_user_route(id: int, user: User, request: Request):
    verify_token(request.headers.get("Authorization"), id)
    return update_user(id, user)

# This route will get a user from the database
@app.get("/users", status_code=200)
async def get_users_route(body: GetUsersItem):
    return get_users(body.pseudo, body.page, body.perPage)

# This route will get a user from the database by id
@app.get("/user/{user_id}", status_code=200)
async def get_user_by_id_route(user_id: int, request: Request):
    verify_token(request.headers.get("Authorization"), user_id)
    return get_user_by_id(user_id)
