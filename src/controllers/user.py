from src.db.connection import get_session, get_base
from src.models import User, ApiException, Auth
from src.validators.user import validate_user, validate_auth, validate_user_update
from datetime import datetime
from bcrypt import hashpw, gensalt
from sqlalchemy import select, or_, func
from src.controllers.token import create_token, TOKEN_CREATION_ERROR_MSG, update_token

UserDb = get_base().classes.user

#error message
USER_NOT_FOUND_MSG = "User not found"
INVALID_PASSWORD_MSG = "Invalid password"
USERNAME_ALREADY_EXISTS_MSG = "An account with this username already exists"
EMAIL_ALREADY_EXISTS_MSG = "An account with this email already exists"
PAGE_NOT_FOUND_MSG = "Page not found"

# This function will add a user to the database
def add_user(user_data: User):
  session = get_session()
  validate_user(user_data)
  try:
    user_data.password = hashpw(user_data.password.encode("utf-8"), gensalt()).decode("utf-8")
    user = UserDb(
      username=user_data.username,
      email=user_data.email,
      pseudo=user_data.pseudo,
      password=user_data.password,
      created_at=datetime.now(),
    )
    session.add(user)
    session.commit()
    return {
      "message": "User added successfully",
      "data": user_to_json(user)
    }
  except Exception as e:
    session.rollback()
    print("Error while adding user to db:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    if "email_UNIQUE" in str(e):
      raise ApiException(400, 1101, [EMAIL_ALREADY_EXISTS_MSG])
    if "username_UNIQUE" in str(e):
      raise ApiException(400, 1101, [USERNAME_ALREADY_EXISTS_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will authenticate a user
def auth_user(auth: Auth):
  session = get_session()
  validate_auth(auth)
  try:
    login = auth.login
    password = auth.password
    # construct the query to get the user
    sql_rec = select(UserDb).where(or_(UserDb.username == login, UserDb.email == login))
    # execute the query and get the user
    user = session.scalars(sql_rec).one_or_none()

    # verify user and password
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    if hashpw(password.encode("utf-8"), user.password.encode("utf-8")) != user.password.encode("utf-8"):
      raise ValueError(INVALID_PASSWORD_MSG)
    
    # create a token
    token = create_token(user)
    if token is None:
      raise ValueError(TOKEN_CREATION_ERROR_MSG)
    
    return {
      "message": "OK",
      "data": token,
    }
  except Exception as e:
    session.rollback()
    print("Error while authenticating user:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    if INVALID_PASSWORD_MSG in str(e):
      raise ApiException(401, 1103, [INVALID_PASSWORD_MSG])
    if TOKEN_CREATION_ERROR_MSG in str(e):
      raise ApiException(500, 1455, [TOKEN_CREATION_ERROR_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will delete a user from the database
def delete_user(user_id: int):
  session = get_session()
  try:
    # construct the query to get the user
    sql_rec = select(UserDb).where(UserDb.id == user_id)
    # execute the query and get the user
    user = session.scalars(sql_rec).one_or_none()

    # verify if user exist
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    
    # delete the user
    session.delete(user)
    session.commit()
    return {
      "message": "User deleted successfully",
    }
  except Exception as e:
    session.rollback()
    print("Error while deleting user:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will update a user in the database
def update_user(user_id: int, user_data: User):
  session = get_session()
  validate_user_update(user_data)
  try:  
    # construct the query to get the user
    sql_rec = select(UserDb).where(UserDb.id == user_id)
    # execute the query and get the user
    user = session.scalars(sql_rec).one_or_none()

    # verify if user exist
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    
    # update the user
    user.username = user_data.username if user_data.username else user.username
    user.email = user_data.email if user_data.email else user.email
    user.pseudo = user_data.pseudo if user_data.pseudo else user.pseudo
    user.password = hashpw(user_data.password.encode("utf-8"), gensalt()).decode("utf-8") if user_data.password else user.password
    session.commit()
    return {
      "message": "User updated successfully",
      "data": user_to_json(user),
      "token": update_token(user)
    }
  except Exception as e:
    session.rollback()
    print("Error while updating user:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    if "email_UNIQUE" in str(e):
      raise ApiException(400, 1101, [EMAIL_ALREADY_EXISTS_MSG])
    if "username_UNIQUE" in str(e):
      raise ApiException(400, 1101, [USERNAME_ALREADY_EXISTS_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will get all users from the database with a pagination system
def get_users(pseudo: str, page: int, per_page: int):
  session = get_session()
  try:
    if page < 1:
      raise ValueError(PAGE_NOT_FOUND_MSG)

    # get the total number of users
    users_count = session.query(func.count(UserDb.id)).filter(UserDb.pseudo.like(f"%{pseudo}%")).scalar()

    # calculate the offset
    offset = ((page -1 ) * per_page)
    if offset < 0:
      offset = 0
    
    # construct the query to get the users
    sql_rec = select(UserDb).filter(UserDb.pseudo.like(f"%{pseudo}%")).limit(per_page).offset(offset)

    # execute the query and get the users
    users = session.scalars(sql_rec).all()

    # verify if pages exists (Page 1 always exists)
    if (len(users) == 0 and page != 1):
      raise ValueError(PAGE_NOT_FOUND_MSG)
    
    return {
      "message": "OK",
      "data": [user_to_json(user) for user in users],
      "pager": {
        "current": page,
        "total": users_count,
      },
    }
  
  except Exception as e:
    session = get_session()
    session.rollback()
    print("Error while getting users:")
    print(e)
    if PAGE_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [PAGE_NOT_FOUND_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will get a user by its id from the database
def get_user_by_id(user_id: int):
  session = get_session()
  try:
    # construct the query to get the user
    sql_rec = select(UserDb).where(UserDb.id == user_id)
    # execute the query and get the user
    user = session.scalars(sql_rec).first()

    # verify if user exist
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    
    return {
      "message": "OK",
      "data": user_to_json(user)
    }
  except Exception as e:
    session.rollback()
    print("Error while getting user by id:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will convert a User object to a JSON object
def user_to_json(user: User):
  return None if user is None else {
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "pseudo": user.pseudo,
    "created_at": user.created_at,
  }
