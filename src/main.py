from fastapi import FastAPI, Request, Form, File, UploadFile, Path, Header
from fastapi.responses import JSONResponse
from src.controllers.user import add_user, auth_user, delete_user, update_user, get_users, get_user_by_id
from src.controllers.token import verify_token
from src.controllers.video import add_video_to_user, get_videos, update_video, delete_video
from src.models import User, Auth, ApiException, GetUsersItem, VideoList, BodyVideoListByUser, BodyVideoUpdate

app = FastAPI()

# Exception handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: ApiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "code": exc.error_code,
            "data": exc.errors,
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
    print(request.headers.get("Authorization"))
    verify_token(request.headers.get("Authorization"), user_id)
    return get_user_by_id(user_id)

# This route will add a video to the user
@app.post("/user/{user_id}/video", status_code=201)
async def add_video_to_user_route(user_id: int = Path(...), Authorization: str = Header(...), name: str = Form(...), source: UploadFile = File(...)):
    verify_token(Authorization, user_id)
    return add_video_to_user(user_id, name, source)

# This route will get a list of videos
@app.get("/videos", status_code=200)
async def get_videos_route(body: VideoList):
    return get_videos(body)

# This route will get a list of videos of the specified user
@app.get("/user/{user_id}/videos", status_code=200)
async def get_user_videos_route(user_id: int, body: BodyVideoListByUser, request: Request):
    verify_token(request.headers.get("Authorization"))
    return get_videos(VideoList(user=user_id, page=body.page, perPage=body.perPage))

# This route will update a video
@app.put("/video/{video_id}", status_code=200)
async def update_video_route(video_id: int, body: BodyVideoUpdate, request: Request):
    verify_token(request.headers.get("Authorization"), body.user)
    return update_video(video_id, body.name)

# This route will delete a video
@app.delete("/video/{video_id}", status_code=204)
async def delete_video_route(video_id: int, request: Request):
    user_id = verify_token(request.headers.get("Authorization"))
    return delete_video(video_id, user_id)
