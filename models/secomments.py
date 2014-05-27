from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Enum, Boolean, DateTime
from sqlalchemy.types import TypeDecorator, Unicode
from sqlalchemy.orm import relationship, backref

from models.base import Base

import datetime

class CoerceUTF8(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value

class Comment(Base):
    """This class defines what the comments information looks like and what is used for training and testing"""
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, unique=True)
    text = Column(CoerceUTF8(500, convert_unicode=True), nullable=False)
    link = Column(CoerceUTF8(500, convert_unicode=True), nullable=False)
    score = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False, index=True)
    reputation = Column(BigInteger, nullable=False)
    post_type = Column(Enum('1', '2'), nullable=False, index=True)
    comment_type_id = Column(Integer, ForeignKey('commenttypes.id'), nullable=False, index=True)
    comment_type = relationship('CommentType', backref='comments')
    creation_date = Column(DateTime, nullable=False)
    disputed = Column(Boolean, nullable=False, default=False, index=True)
    system_add_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
#    is_training = Column(Boolean, nullable=False, default=False)
#    added_manually = Column(Boolean, nullable=False, default=False)


class CommentType(Base):
    """This class defines our available comment types"""
    __tablename__ = 'commenttypes'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(CoerceUTF8(50, convert_unicode=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)


