import logging
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import models.base as base
from models.secomments import Comment, CommentType
from datetime import datetime


def setup_logging(file_name, file_level=logging.INFO, console_level=logging.INFO):
	LOGLEVEL_FILE = file_level
	LOGLEVEL_CONSOLE = console_level

	logging.basicConfig(filename='logs/%s.log' % (file_name), level=LOGLEVEL_FILE,
						format='%(asctime)s - %(levelname)-8s - %(name)-12s - %(message)s')
	console_log = logging.StreamHandler()
	console_log.setLevel(LOGLEVEL_CONSOLE)
	formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
	console_log.setFormatter(formatter)
	logging.getLogger('').addHandler(console_log)
	logging.debug("Logging initialized")
	return logging
	
def connect_to_db(db_name):
	logging.debug("Connecting to %s" % (db_name))
	Base = declarative_base()
	engine = create_engine(db_name, convert_unicode=True, echo=False)
	session = sessionmaker()
	session.configure(bind=engine)
	logging.debug('Connection to database intialized; returning session.')
	return session()
