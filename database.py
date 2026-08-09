from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Thay đổi user, password và host phù hợp với CSDL MySQL của bạn
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
