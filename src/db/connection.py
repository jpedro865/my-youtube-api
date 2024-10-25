import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base


# Get environment variables
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", 3306)
user = os.getenv("DB_USER", "user")
password = os.getenv("DB_PASSWORD", "password")
db = os.getenv("DB_NAME", "mydb")

# Create the database URL
db_url = "mysql+pymysql://{}:{}@{}:{}/{}".format(
  user,
  password,
  host,
  port,
  db
)

# Function to get a connection to the database
def get_engine():
  try:
    engine = create_engine(db_url)
    print("Connection successful")
    return engine
  except Exception as e:
    print("Failed while creating db engine:")
    print(e)
    return None

# Function to get a session to the database using SQLAlchemy ORM
def get_session():
  print("Establishing session with db...")
  try:
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    print("Connection successful")
    return session_local()
  except Exception as e:
    print("Error loading db session:")
    print(e)
    print("Retrying...")
    return get_session()

# Function to get the base of the database
def get_base():
  print("Establishing base builder with db...")
  try:
    Base = automap_base()
    Base.prepare(get_engine(), reflect=True)
    print("Connection successful")
    return Base
  except Exception as e:
    print("Error loading db base:")
    print(e)
    print("Retrying...")
    return get_base()
