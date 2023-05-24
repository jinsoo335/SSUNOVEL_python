import sys
sys.path.append("")

from sqlalchemy.orm import sessionmaker

from database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
