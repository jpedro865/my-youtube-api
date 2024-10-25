from src.models import User
import re

# This function will validate the user data
def validate_user(user: User):
  # username validation
  if not user.username:
    raise ValueError("Username is required")
  if len(user.username) < 3:
    raise ValueError("Username must be at least 3 characters")
  if re.match(r"^[a-zA-Z0-9-_]*$", user.username) is None:
    raise ValueError("Username must only contain letters, numbers, _ and -")
  
  # pseudo validation
  if user.pseudo:
    if len(user.pseudo) < 3:
      raise ValueError("Pseudo must be at least 3 characters")
    if len(user.pseudo) > 20:
      raise ValueError("Pseudo must be at most 20 characters")
    
  # email validation
  if not user.email:
    raise ValueError("Email is required")
  if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user.email):
    raise ValueError("Invalid email")
  
  # password validation
  if not user.password:
    raise ValueError("Password is required")
  if len(user.password) < 8:
    raise ValueError("Password must be at least 8 characters")
  
  return True
