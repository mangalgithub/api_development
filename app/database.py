import os
from sqlmodel import create_engine,Session,SQLModel
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# print("DB_HOST =", os.getenv("DB_HOST"))
# print("DATABASE_URL =", os.getenv("DATABASE_URL"))

# if not DATABASE_URL:
    # Local development fallback
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

    # missing = [k for k, v in {
    #     "DB_USER": DB_USER,
    #     "DB_PASSWORD": DB_PASSWORD,
    #     "DB_NAME": DB_NAME,
    # }.items() if not v]

    # if missing:
    #     raise RuntimeError(f"Missing env vars: {missing}")

DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"{DB_HOST}@:{DB_PORT}/{DB_NAME}"
    )

# Optional: Render sometimes provides postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)


# ---------- Session Dependency ----------
def get_session():
    with Session(engine) as session:
        yield session

# ---------- DB Init ----------
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
