from src.db.connection import get_session, get_base
from src.models import MyException
from datetime import datetime, timedelta
from sqlalchemy import select
import secrets

Session = get_session()
TokenDb = get_base().classes.token

#error message
TOKEN_CREATION_ERROR_MSG = "Error while creating token"
TOKEN_NOT_FOUND_MSG = "Token not found"
TOKEN_EXPIRED_MSG = "Token expired"

# This function will create a token for a user and add it to the database
def create_token(user_id: int):
  try:
    unexpired_token = user_has_unexpired_token(user_id)
    if unexpired_token:
      return unexpired_token

    # create a new token
    new_token = secrets.token_urlsafe(32)

    # add the token to the database
    token = TokenDb(
      code=new_token,
      user_id=user_id,
      expired_at=datetime.now() + timedelta(hours=3),
    )
    Session.add(token)
    Session.commit()
    return new_token
  except Exception as e:
    Session.rollback()
    print("Error while creating token:")
    print(e)
    return None

# This function will verify if user possess a token
def user_has_unexpired_token(user_id: int):
  try:
    # construct the query to get the token
    sql_rec = select(TokenDb).where(TokenDb.user_id == user_id)
    # execute the query and get the token
    token = Session.scalars(sql_rec).one_or_none()

    # verify if token exist and is not expired
    if token is None:
      return False
    if token.expired_at < datetime.now():
      # delete the token if it is expired
      Session.delete(token)
      Session.commit()
      return False
    return token.code
  except Exception as e:
    print("Error while verifying if user has unexpired token:")
    print(e)
    return False
