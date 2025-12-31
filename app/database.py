from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv
load_dotenv()

# ---------- PostgreSQL Config ----------
DB_USER = os.getenv("DB_USER");
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ---------- Engine ----------
engine = create_engine(
    DATABASE_URL,
    echo=True,          
    pool_size=10,
    max_overflow=20
)

# ---------- Session Dependency ----------
def get_session():
    with Session(engine) as session:
        yield session

# ---------- DB Init ----------
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
