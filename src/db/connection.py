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
  print("Connecting to database...")
  try:
    engine = create_engine(db_url)
    print("Connection successful")
    return engine
  except Exception as e:
    print("Connection failed, error:")
    print(e)
    return None

# Function to get a session to the database using SQLAlchemy ORM
def get_session():
  try:
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return session_local()
  except Exception as e:
    print("Error loading db session:")
    print(e)
    return None

def get_base():
  try:
    Base = automap_base()
    Base.prepare(get_engine(), reflect=True)
    return Base
  except Exception as e:
    print("Error loading db base:")
    print(e)
    return None
