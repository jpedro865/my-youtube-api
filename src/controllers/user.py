from src.db.connection import get_session, get_base
from datetime import date

Session = get_session()
User = get_base().classes.user

def add_user():
  try:
    user = User(
      username="Johnvbvb",
      email="email@emailvvbdd.com",
      pseudo="johnny",
      password="password",
      created_at=date.today(),
    )
    Session.add(user)
    Session.commit()
    print("User added")
  except Exception as e:
    print("Error in test:")
    print(e)
