from src.db.connection import get_session, get_base
from src.models import User, MyException
from src.validators.user import validate_user
from datetime import datetime
from bcrypt import hashpw, gensalt
from sqlalchemy import select, or_
from src.controllers.token import create_token, TOKEN_CREATION_ERROR_MSG

Session = get_session()
UserDb = get_base().classes.user

#error message
USER_NOT_FOUND_MSG = "User not found"
INVALID_PASSWORD_MSG = "Invalid password"
USERNAME_ALREADY_EXISTS_MSG = "An account with this username already exists"
EMAIL_ALREADY_EXISTS_MSG = "An account with this email already exists"

# This function will add a user to the database
def add_user(user_data: User):
  try:
    print(user_data)
    validate_user(user_data)
    user_data.password = hashpw(user_data.password.encode("utf-8"), gensalt()).decode("utf-8")
    user = UserDb(
      username=user_data.username,
      email=user_data.email,
      pseudo=user_data.pseudo,
      password=user_data.password,
      created_at=datetime.now(),
    )
    Session.add(user)
    Session.commit()
    return {
      "message": "User added successfully",
      "data": user_to_json(user)
    }
  except Exception as e:
    Session.rollback()
    print("Error while adding user to db:")
    print(e)
    if "email_UNIQUE" in str(e):
      raise MyException(USERNAME_ALREADY_EXISTS_MSG, 400)
    elif "username_UNIQUE" in str(e):
      raise MyException(EMAIL_ALREADY_EXISTS_MSG, 400)
    raise MyException("{}".format(e), 400)

# This function will authenticate a user
def auth_user(login: str, password: str):
  try:
    # construct the query to get the user
    sql_rec = select(UserDb).where(or_(UserDb.username == login, UserDb.email == login))
    # execute the query and get the user
    user = Session.scalars(sql_rec).one_or_none()

    # verify user and password
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    if hashpw(password.encode("utf-8"), user.password.encode("utf-8")) != user.password.encode("utf-8"):
      raise ValueError(INVALID_PASSWORD_MSG)
    
    # create a token
    token = create_token(user.id)
    if token is None:
      raise ValueError(TOKEN_CREATION_ERROR_MSG)
    
    return {
      "message": "OK",
      "data": token,
    }
  except Exception as e:
    Session.rollback()
    print("Error while authenticating user:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise MyException(USER_NOT_FOUND_MSG, 404)
    elif INVALID_PASSWORD_MSG in str(e):
      raise MyException(INVALID_PASSWORD_MSG, 401)
    elif TOKEN_CREATION_ERROR_MSG in str(e):
      raise MyException(TOKEN_CREATION_ERROR_MSG, 500)
    raise MyException("{}".format(e), 400)

def delete_user(user_id: int):
  try:
    # construct the query to get the user
    sql_rec = select(UserDb).where(UserDb.id == user_id)
    # execute the query and get the user
    user = Session.scalars(sql_rec).one_or_none()

    # verify if user exist
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    
    # delete the user
    Session.delete(user)
    Session.commit()
    return {
      "message": "User deleted successfully",
    }
  except Exception as e:
    Session.rollback()
    print("Error while deleting user:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise MyException(USER_NOT_FOUND_MSG, 404)
    raise MyException("{}".format(e), 400)

# This function will convert a User object to a JSON object
def user_to_json(user: User):
  return None if user is None else {
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "pseudo": user.pseudo,
    "created_at": user.created_at,
  }
