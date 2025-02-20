from src.db.connection import get_session, get_base
from src.models import ApiException
from datetime import datetime, timedelta
from sqlalchemy import select
from os import environ
import jwt


TokenDb = get_base().classes.token

#error message
TOKEN_CREATION_ERROR_MSG = "Error while creating token"
TOKEN_NOT_FOUND_MSG = "Token not found"
TOKEN_EXPIRED_MSG = "Token expired"
VERIFICATION_ERROR_MSG = "Error while verifying token"

# This function will create a token for a user and add it to the database
def create_token(user):
  try:
    session = get_session()
    unexpired_token = user_has_unexpired_token(user.id)
    if unexpired_token:
      return unexpired_token

    # CREATE JSON TOKEN
    expires = datetime.now() + timedelta(hours=3)
    new_token = jwt.encode({
      "user_id": user.id,
      "username": user.username,
      "pseudo": user.pseudo,
      "email": user.email,
      "exp": expires
    }, environ['SECRET_KEY'], algorithm="HS256")

    print(environ['SECRET_KEY'])

    # add the token to the database
    token = TokenDb(
      code=new_token,
      user_id=user.id,
      expired_at=expires,
    )
    session.add(token)
    session.commit()
    return new_token
  except Exception as e:
    session.rollback()
    print("Error while creating token:")
    print(e)
    return None

# This function will verify if user possess a token
def user_has_unexpired_token(user_id: int):
  try:
    session = get_session()
    # construct the query to get the token
    sql_rec = select(TokenDb).where(TokenDb.user_id == user_id)
    # execute the query and get the token
    token = session.scalars(sql_rec).one_or_none()

    # verify if token exist and is not expired
    if token is None:
      return False
    if token.expired_at < datetime.now():
      # delete the token if it is expired
      session.delete(token)
      session.commit()
      return False
    return token.code
  except Exception as e:
    print("Error while verifying if user has unexpired token:")
    print(e)
    return False

# updates the token of a user with the new information
def update_token(user):
  try:
    # delete the old token
    delete_user_tokens(user.id)

    session = get_session()
    # CREATE JSON TOKEN
    expires = datetime.now() + timedelta(hours=3)
    new_token = jwt.encode({
      "user_id": user.id,
      "username": user.username,
      "pseudo": user.pseudo,
      "email": user.email,
      "exp": expires
    }, environ['SECRET_KEY'], algorithm="HS256")

    # add the token to the database
    token = TokenDb(
      code=new_token,
      user_id=user.id,
      expired_at=expires,
    )
    session.add(token)
    session.commit()
    return new_token
  except Exception as e:
    session.rollback()
    print("Error while updating token:")
    print(e)
    return None

  
def verify_token(token: str, user_id: int = None):
  try:
    session = get_session()
    if token is None:
      raise ValueError(TOKEN_NOT_FOUND_MSG)
    # construct the query to get the token
    sql_rec = select(TokenDb).where(TokenDb.code == token)
    if user_id is not None:
      sql_rec = sql_rec.where(TokenDb.user_id == user_id)
    # execute the query and get the token
    token = session.scalars(sql_rec).one_or_none()

    # verify if token exist and is not expired
    if token is None:
      raise ValueError(VERIFICATION_ERROR_MSG)
    if token.expired_at < datetime.now():
      raise ValueError(TOKEN_EXPIRED_MSG)
    return token.user_id
  except Exception as e:
    print("Error while verifying token:")
    print(e)
    if TOKEN_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1402, [TOKEN_NOT_FOUND_MSG])
    elif TOKEN_EXPIRED_MSG in str(e):
      raise ApiException(401, 1401, [TOKEN_EXPIRED_MSG])
    raise ApiException(401, 1444, [VERIFICATION_ERROR_MSG])

def delete_user_tokens(user_id: int):
  try:
    session = get_session()
    # construct the query to get the token
    sql_rec = select(TokenDb).where(TokenDb.user_id == user_id)
    # execute the query and get the token
    tokens = session.scalars(sql_rec).all()

    # verify if token exist and is not expired
    if tokens.__len__() == 0:
      return True

    for token in tokens:
      session.delete(token)
    session.commit()
    return True
  except Exception as e:
    print("Error while deleting user tokens:")
    print(e)
    return False
