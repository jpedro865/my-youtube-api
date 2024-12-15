from src.models import User, Auth
from src.models import ApiException
import re

# This function will validate the user data
def validate_user(user: User):
  # username validation
  if not user.username:
    raise ApiException(400, 1101, ["Username is required"])
  if len(user.username) < 3:
    raise ApiException(400, 1101, ["Username must be at least 3 characters"])
  if re.match(r"^[a-zA-Z0-9-_]*$", user.username) is None:
    raise ApiException(400, 1101, ["Username must only contain letters, numbers, _ and -"])
  
  # pseudo validation
  if user.pseudo:
    if len(user.pseudo) < 3:
      raise ApiException(400, 1101, ["Pseudo must be at least 3 characters"])
    if len(user.pseudo) > 20:
      raise ApiException(400, 1101, ["Pseudo must be at most 20 characters"])
    
  # email validation
  if not user.email:
    raise ApiException(400, 1101, ["Email is required"])
  if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user.email):
    raise ApiException(400, 1101, ["Invalid email"])
  
  # password validation
  if not user.password:
    raise ApiException(400, 1101, ["Password is required"])
  if len(user.password) < 8:
    raise ApiException(400, 1101, ["Password must be at least 8 characters"])
  
  return True

# This function will validate the user data for update
def validate_auth(auth: Auth):
  # login validation
  if not auth.login:
    raise ApiException(400, 1101, ["Login is required"])
  
  # password validation
  if not auth.password:
    raise ApiException(400, 1101, ["Password is required"])
  
  return True

# This function will validate the user data for update
def validate_user_update(user: User):
  # username validation
  if user.username:
    if len(user.username) < 3:
      raise ApiException(400, 1101, ["Username must be at least 3 characters"])
    if re.match(r"^[a-zA-Z0-9-_]*$", user.username) is None:
      raise ApiException(400, 1101, ["Username must only contain letters, numbers, _ and -"])
  
  # pseudo validation
  if user.pseudo:
    if len(user.pseudo) < 3:
      raise ApiException(400, 1101, ["Pseudo must be at least 3 characters"])
    if len(user.pseudo) > 20:
      raise ApiException(400, 1101, ["Pseudo must be at most 20 characters"])
    
  # email validation
  if user.email:
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user.email):
      raise ApiException(400, 1101, ["Invalid email"])
  
  # password validation
  if user.password:
    if len(user.password) < 8:
      raise ApiException(400, 1101, ["Password must be at least 8 characters"])
  
  return True
