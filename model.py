import sys
sys.path.append("")

from sqlalchemy import Column, BIGINT, TIMESTAMP, INT, VARCHAR, FLOAT, TEXT, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Novel(Base):
    __tablename__ = 'novel'

    novel_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(100), nullable=False)
    summary = Column(TEXT)
    cover_image = Column(TEXT, nullable=True)
    episode = Column(INT)
    price = Column(INT, nullable=True)
    download_cnt = Column(INT)
    author_idx = Column(BIGINT, ForeignKey('author.author_idx'))
    rating = Column(FLOAT)
    review_cnt = Column(INT)
    category = Column(VARCHAR(45))
    is_finished = Column(VARCHAR(10))
    is_naver = Column(VARCHAR(200))
    is_kakao = Column(VARCHAR(200))
    is_munpia = Column(VARCHAR(200))
    is_ridi = Column(VARCHAR(200))



class RecommendNovel(Base):
    __tablename__ = 'recommend_novel'
    recommend_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    origin_novel_idx = Column(BIGINT, nullable=False)
    recommend_novel_idx = Column(BIGINT, nullable=False)


class Author(Base):
    __tablename__ = 'author'

    author_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    name = Column(VARCHAR(100))


class FavoriteAuthor(Base):
    __tablename__ = 'favorite_author'

    favorite_author_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    author_idx = Column(BIGINT, ForeignKey('author.author_idx'))
    member_idx = Column(BIGINT, ForeignKey('member.member_idx'))


class Alert(Base):
    __tablename__ = 'alert'

    alert_idx = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(100))
    read_check = Column(INT)
    url = Column(TEXT)
    member_idx = Column(BIGINT, ForeignKey('member.member_idx'))
    alert_type = Column(Enum('AUTHOR', 'COMMUNITY'))


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

    email = Column(VARCHAR(100))
    password = Column(VARCHAR(200))
    nickname = Column(VARCHAR(45))
    age = Column(INT)
    gender = Column(Enum('MALE', 'FEMALE'))
    login_type = Column(Enum('USER', 'ADMIN'))

