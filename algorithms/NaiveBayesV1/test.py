from NaiveBayes import  Pool
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

import models.base as base
from models.secomments import Comment, CommentType

Base = declarative_base()
engine = create_engine('sqlite:///FlaskPanel/se_comments.db', convert_unicode=True, echo=False)
session = sessionmaker()
session.configure(bind=engine)
s = session()

threshold = 20

p = Pool()
p.learn(threshold=threshold)


res = s.query(Comment.comment_type_id, 
        CommentType.name,
        func.count(Comment.comment_type_id).label('count')
    ).join(CommentType).group_by(Comment.comment_type_id).all()    

comment_types_ids = []
comment_types = []
for r in res:
    if r.count > threshold:
        comment_types_ids.append(r.comment_type_id)
        comment_types.append(r.name)
		
if comment_types_ids:
    for ct in comment_types_ids:
#         comments = s.query(Comment).filter(Comment.comment_type_id. = ct).all()
        comments = s.query(Comment).filter_by(comment_type_id = ct).order_by(func.random()).limit(4)

        if comments:
			for c in comments:
				res = p.Probability(c, dclass = "too chatty")
				print """
				-----	
				Comment => %s
				Real => %s	
				Result => %s
				""" % (c.text, c.comment_type.name, str(res))
#				print(c.comment_type.name + ": " + file + ": " + str(res))

