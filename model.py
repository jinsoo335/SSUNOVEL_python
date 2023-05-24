import sys
sys.path.append("")

from sqlalchemy import Column, BIGINT, TIMESTAMP, INT, VARCHAR, FLOAT, TEXT, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Novel(Base):
    __tablename__ = 'novel'

    novel_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(100), nullable=False)


class Author(Base):
    __tablename__ = 'author'

    author_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    name = Column(VARCHAR(100))


class Like(Base):
    __tablename__ = 'like'

    like_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    review_idx = Column(BIGINT, nullable=True)


class Review(Base):
    __tablename__ = 'review'

    review_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    rating = Column(FLOAT)


class Member(Base):
    __tablename__ = 'member'

    member_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    age = Column(INT)
    gender = Column()

