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
    is_training = Column(Boolean, nullable=False, default=False)
    added_manually = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return "<Comment(id='%s', text='%s', comment_type='%s', link='%s')>" % (self.id, self.text, self.comment_type, self.link)


class CommentType(Base):
    """This class defines our available comment types"""
    __tablename__ = 'commenttypes'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(CoerceUTF8(50, convert_unicode=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return "<CommentType(id='%s', name='%s', is_active='%s')>" % (self.id, self.name, self.is_active)

    @classmethod
    def all_comment_types(cls, session):
        types_dict = {}
        for r in session.query(cls).filter_by(is_active=True).all():
            types_dict[r.name] = r.__dict__
        return types_dict


class TrainingAlgorithm(Base):
    """This class defines our available algorithms"""
    __tablename__ = 'trainingalgorithms'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(CoerceUTF8(50, convert_unicode=True), nullable=False)
    description = Column(CoerceUTF8(2000, convert_unicode=True), nullable=False)
    creation_date = Column(DateTime, nullable=False)
    file_location = Column(CoerceUTF8(250, convert_unicode=True), nullable=True)

    def __repr__(self):
        return "<TrainingAlgorithm(id='%s', name='%s', file_location='%s')>" % (self.id, self.name, self.file_location)

    @classmethod
    def all_training_algorithms(cls, session):
        training_dict = {}
        for r in session.query(cls).all():
            training_dict[r.name] = r.__dict__
        return training_dict


class TrainingResult(Base):
    """This class defines the results of our algorithms"""
    __tablename__ = 'trainingresults'
    comment_id = Column(Integer, ForeignKey('comments.id'), primary_key=True, unique=True)
    comment = relationship('Comment', backref='trainingresults')
    comment_type_id = Column(Integer, ForeignKey('commenttypes.id'), primary_key=True, unique=True)
    comment_type = relationship('CommentType', backref='trainingresults')
    algorithm_id = Column(Integer, ForeignKey('trainingalgorithms.id'), primary_key=True, unique=True)
    algorithm = relationship('TrainingAlgorithm', backref='trainingresults')
    classification_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    is_correct_classification = Column(Boolean)


class Setting(Base):
    """This class defines settings that our application uses"""
    __tablename__ = 'settings'
    name = Column(CoerceUTF8(125, convert_unicode=True), primary_key=True, unique=True)
    value = Column(CoerceUTF8(500, convert_unicode=True), nullable=False)
    user_manage = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return "<Setting(name='%s', value='%s')>" % (self.name, self.value)

    @classmethod
    def by_name(cls, session, name):
        return session.query(cls.value).filter(cls.name == name).scalar()

    @classmethod
    def update_value(cls, session, name, value):
        session.query(cls).filter_by(name=name).update({"value":value})
        session.commit()
