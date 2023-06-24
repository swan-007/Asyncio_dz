import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

load_dotenv()

PG_DSN = f"postgresql+asyncpg://{os.getenv('db_user')}:{os.getenv('db_password')}@" \
         f"{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_name')}"
engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class SwapiPeople(Base):
    __tablename__ = "swapi_people"

    id = Column(Integer, primary_key=True)
    birth_year = Column(String(10))
    eye_color = Column(String(20))
    films = Column(Text)
    gender = Column(String(30))
    hair_color = Column(String(30))
    height = Column(String(30))
    homeworld = Column(String(200))
    mass = Column(String(30))
    name = Column(String(30))
    skin_color = Column(String(30))
    species = Column(Text)
    starships = Column(Text)
    vehicles = Column(Text)
