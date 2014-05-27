import csv
import logging

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import models.base as base
from models.secomments import Comment, CommentType

from datetime import datetime


LOGLEVEL_FILE = logging.INFO
LOGLEVEL_CONSOLE = logging.INFO

logging.basicConfig(filename='logs/populate_database.log', level=LOGLEVEL_FILE,
                    format='%(asctime)s - %(levelname)-8s - %(name)-12s - %(message)s')
console_log = logging.StreamHandler()
console_log.setLevel(LOGLEVEL_CONSOLE)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console_log.setFormatter(formatter)
logging.getLogger('').addHandler(console_log)

Base = declarative_base()
engine = create_engine('sqlite:///FlaskPanel/se_comments.db', convert_unicode=True, echo=False)
session = sessionmaker()
session.configure(bind=engine)
logging.info('Creating Database')
#base.Base.metadata.create_all(engine)

s = session()
#logging.info('Populating Comment Types')
#s.add(CommentType(id=1, name="good comment"))
#s.add(CommentType(id=2, name="rude or offensive"))
#s.add(CommentType(id=3, name="not constructive"))
#s.add(CommentType(id=4, name="obsolete"))
#s.add(CommentType(id=5, name="too chatty"))
#s.add(CommentType(id=6, name="other..."))
#s.commit()

with open('clean_data/clean_mostly_good.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # Skip the headers line
    logging.info('Inserting comments')
    cnt = 0
    for row in reader:
        logging.debug(
            "Inserting: Link => {0:s}, Text => {1:s}, Id => {2:s}, Score => {3:s}, User ID => {4:s}, Rep => {5:s}, Post Type => {6:s}, " \
            "Date => {0:s}, Comment Type => {1:s}"
            .format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        s.add(Comment(link=row[0], text=row[1], id=row[2], score=row[3], user_id=row[4], reputation=row[5],
                      post_type=row[6], creation_date=datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S"), comment_type_id=row[8]))
        cnt += 1
        if cnt % 1000 == 0:
            s.commit()
    s.commit()