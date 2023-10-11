from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models.db_models as db

engine = create_engine("postgresql+psycopg2://postgres:adminpostgres@postgresql:5432/RheemCSmessages")
# engine = create_engine("sqlite:///resume.db")
db.Base.metadata.create_all(bind=engine)  # Connection between Base class and the engine

# Take care with expire_on_commit=False!
SessionMaker = sessionmaker(bind=engine, expire_on_commit=False)  # Create SessionMaker with the engine
