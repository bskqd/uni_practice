from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
DATABASE_URL = 'postgresql://bohdan:bohdan1234@localhost/uni'
engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(engine, autoflush=False, expire_on_commit=False)
