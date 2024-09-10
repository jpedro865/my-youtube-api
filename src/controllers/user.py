from src.db.connection import get_session, get_base
from src.models import User, MyException
from src.validators.user import validate_user
from datetime import datetime
from bcrypt import hashpw, gensalt

Session = get_session()
UserDb = get_base().classes.user

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
      "data": {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "pseudo": user.pseudo,
        "created_at": user.created_at,
      }
    }
  except Exception as e:
    Session.rollback()
    print("Error while adding user to db:")
    print(e)
    if "email_UNIQUE" in str(e):
      raise MyException("An account with this email already exists", 400)
    elif "username_UNIQUE" in str(e):
      raise MyException("An account with this username already exists", 400)
    raise MyException("{}".format(e), 400)
