import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import bz2
import pickle


post_type_dict = {
    "question": 1,
    "answer": 2
}


def setup_logging(file_name, file_level=logging.INFO, console_level=logging.INFO, requests_level=logging.CRITICAL):
    logging.basicConfig(filename='logs/%s.log' % (file_name), level=file_level,
                        format='%(asctime)s - %(levelname)-8s - %(name)-12s - %(message)s')
    console_log = logging.StreamHandler()
    console_log.setLevel(console_level)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console_log.setFormatter(formatter)
    logging.getLogger('').addHandler(console_log)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.CRITICAL)
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


def get_naive_bayes_classifier(classifier_name):
    logging.info("Opening classifier from {0}".format(classifier_name))
    f = bz2.BZ2File(classifier_name, 'rb')
    cl = pickle.load(f)
    f.close()
    return cl