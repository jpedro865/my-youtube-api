from pydantic import BaseModel

# This is the User model that will be used to validate the request body
class User(BaseModel):
  username: str
  pseudo: str
  email: str
  password: str

# This is the Auth model that will be used to validate the request body
class Auth(BaseModel):
  login: str
  password: str

# custom exception
class MyException(Exception):
  def __init__(self, message, status_code):
    self.message = message
    self.status_code = status_code
