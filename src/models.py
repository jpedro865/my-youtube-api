from pydantic import BaseModel, Field
from typing import Union

# This is the User model that will be used to validate the request body
class User(BaseModel):
  username: str = None
  pseudo: str = None
  email: str = None
  password: str = None

# This is the Auth model that will be used to validate the request body
class Auth(BaseModel):
  login: str = None
  password: str = None

# classe used to validate request body of get_users_route
class GetUsersItem(BaseModel):
  pseudo: str = ''
  page: int = 1 # default value
  perPage: int  = 5 # default value

# custom exception
class ApiException(Exception):
  def __init__(self, status_code: int, error_code: int=None, errors: list=None):
    switcher = {
      400: "Bad Request",
      401: "Unauthorized",
      403: "Forbidden",
      404: "Not Found",
      500: "Internal Server Error"
    }
    self.message = switcher.get(status_code, "Internal Server Error")
    self.status_code = status_code
    self.error_code = error_code
    self.errors = errors

# BaseModel VideoList to validate request body of get_videos_route
class VideoList(BaseModel):
  name: str = None
  user: Union[int, str] = None
  duration: int = None
  page: int = 1
  perPage: int = 5

class BodyVideoListByUser(BaseModel):
  page: int = 1
  perPage: int = 5

class BodyVideoUpdate(BaseModel):
  name: str = None
  user: int = None

class BodyAddComment(BaseModel):
  body: str = None

class BodyListComments(BaseModel):
  page: int = 1
  perPage: int = 5

class BodyAddFormat(BaseModel):
  format: str = None
  file: str = None
