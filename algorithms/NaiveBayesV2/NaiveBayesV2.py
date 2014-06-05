import re, os
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from text.classifiers import NaiveBayesClassifier
from text.blob import TextBlob
import random
import math

import models.base as base
from models.secomments import Comment, CommentType

LOGLEVEL_FILE = logging.INFO
LOGLEVEL_CONSOLE = logging.INFO

TRAINING_RATIO = 0.75

logging.basicConfig(filename='../../logs/naive_bayes_v2.log', level=LOGLEVEL_FILE,
                    format='%(asctime)s - %(levelname)-8s - %(name)-12s - %(message)s')
console_log = logging.StreamHandler()
console_log.setLevel(LOGLEVEL_CONSOLE)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console_log.setFormatter(formatter)
logging.getLogger('').addHandler(console_log)

Base = declarative_base()
engine = create_engine('sqlite:///../../FlaskPanel/se_comments.db', convert_unicode=True, echo=False)
session = sessionmaker()
session.configure(bind=engine)
s = session()
logging.debug('Connected to Database')


def get_training_data(threshold=1000):
        """ Learn the various types of comments available in the database
        Learn only comments that have more than `threshold` classified against it """

        res = (s.query(CommentType.id, CommentType.name,
                func.count(CommentType.id).label('count'))
            .select_from(CommentType).join(Comment)
            .group_by(CommentType.id, CommentType.name)
            )

        comment_types = []
        for r in res:
            if r.count > threshold:
                comment_types.append((r.id, r.name))
                logging.info('Pulling comments for %s (%s) => Count: %s' % (r.id, r.name, r.count))

        training_data = {}
        if comment_types:
            for ct in comment_types:
                comments = s.query(Comment).filter_by(comment_type_id=ct[0]).order_by(func.random()).limit(threshold)
                training_data[ct[1]] = comments
        else:
            raise ValueError('No comments found with the learning threshold of %s' % (threshold))

        # Create our tuple list for further training
        training_list = []
        for data in training_data:
            for d in training_data[data]:
                training_list.append((d.text, data))      # Text, classification

        return training_list



data = get_training_data(threshold=1000)
random.shuffle(data)
train, test = data[:int(math.floor(len(data)*TRAINING_RATIO))], data[int(math.ceil(len(data)*TRAINING_RATIO)):]

logging.info("Data Set Size => {0}".format(len(data)))
logging.info("Training Set Size => {0}".format(len(train)))
logging.info("Test Set Size => {0}".format(len(test)))
entire_set = len(data) == len(train) + len(test)
logging.log(logging.WARNING if not entire_set else logging.INFO, "Entire data set allocated => {0}".format(entire_set))

logging.info("Training NaiveBayes Classifier")
cl = NaiveBayesClassifier(train)


# Compute accuracy
print("Accuracy: {0}".format(cl.accuracy(test)))

logging.info("Listing Informative Features")
# Show 5 most informative features
cl.show_informative_features(30)



