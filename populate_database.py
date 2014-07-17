from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import models.secomments

from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///FlaskPanel/se_comments.db', convert_unicode=True, echo=False)
session = sessionmaker()
session.configure(bind=engine)
models.secomments.create_all_tables(engine)


s = session()

s.add(models.secomments.CommentType(id=1, name="good comment", flagging_threshold=0.9999))
s.add(models.secomments.CommentType(id=2, name="rude or offensive", flagging_threshold=1))
s.add(models.secomments.CommentType(id=3, name="not constructive", flagging_threshold=1))
s.add(models.secomments.CommentType(id=4, name="obsolete", flagging_threshold=0.99))
s.add(models.secomments.CommentType(id=5, name="too chatty", flagging_threshold=0.9997))
s.add(models.secomments.CommentType(id=6, name="other...", flagging_threshold=1))
s.commit()

s.add(models.secomments.Setting(name="classifier_algorithm", value="naivebayesv2", user_manage=1))
s.add(models.secomments.Setting(name="current_status", value="", user_manage=0))
s.add(models.secomments.Setting(name="current_status_datetime", value=datetime.utcnow(), user_manage=0))
s.add(models.secomments.Setting(name="current_status_last_run_datetime", value="", user_manage=0))
s.add(models.secomments.Setting(name="flagging_max_comments_retrieve", value="1000", user_manage=1))
s.add(models.secomments.Setting(name="max_history_days", value="10000", user_manage=1))
s.add(models.secomments.Setting(name="min_sleep_between_comment_fetch", value="300", user_manage=1))
s.add(models.secomments.Setting(name="min_sleep_between_flags", value="5.5", user_manage=1))
s.add(models.secomments.Setting(name="se_api_comment_filter", value="!1zSsiTKfrmHAV3)D3sqap", user_manage=1))
s.add(models.secomments.Setting(name="se_api_key", value="", user_manage=1))
s.add(models.secomments.Setting(name="se_api_remaining_quota", value="", user_manage=0))
s.add(models.secomments.Setting(name="se_api_token", value="", user_manage=1))
s.commit()

s.add(models.secomments.TrainingAlgorithm(name="naivebayesv2", description="Naive Bayes version 2", creation_date=datetime.utcnow(), file_location="algorithms/NaiveBayesV2/naivebayesv2.pickle.bz2"))
s.commit()


