# -*- coding: utf-8 -*-

from utils import utils
from models.secomments import Setting, Comment, CommentType, TrainingAlgorithm
from text.blob import TextBlob
from SEAPI import SEAPI
from bs4 import BeautifulSoup
from datetime import datetime
from math import floor
from time import sleep
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import logging

logging = utils.setup_logging("retrieve_comments", file_level=logging.DEBUG, console_level=logging.INFO,
                                requests_level=logging.CRITICAL)
s = utils.connect_to_db("sqlite:///FlaskPanel/se_comments.db")

# These our the global variables we'll be using
SETTINGS = None
SITE = None
CLASSIFIER_DICT = None
COMMENT_TYPES_DICT = None
CLASSIFIER = None


def main(skip_comments=False):
    global SETTINGS, SITE, CLASSIFIER_DICT, COMMENT_TYPES_DICT, CLASSIFIER
    SETTINGS = gather_settings()
    SITE = SEAPI.SEAPI('stackoverflow', key=SETTINGS['API_KEY'], access_token=SETTINGS['API_TOKEN'])
    SITE.page_size = SETTINGS['MAX_COMMENTS_RETRIEVE'] if SETTINGS['MAX_COMMENTS_RETRIEVE'] <= 100 else 100
    SITE.max_pages = 1 if floor(SETTINGS['MAX_COMMENTS_RETRIEVE'] / SITE.page_size) == 0 else floor(
        SETTINGS['MAX_COMMENTS_RETRIEVE'] / SITE.page_size)
    CLASSIFIER_DICT = TrainingAlgorithm.all_training_algorithms(s)
    COMMENT_TYPES_DICT = CommentType.all_comment_types(s)
    logging.info("Processing Classifier information: '%s' at %s" % (CLASSIFIER_DICT[SETTINGS['CLASSIFIER_ALGORITHM']]['name'],
                                                                CLASSIFIER_DICT[SETTINGS['CLASSIFIER_ALGORITHM']]['file_location']))
    CLASSIFIER = utils.get_naive_bayes_classifier(CLASSIFIER_DICT[SETTINGS['CLASSIFIER_ALGORITHM']]['file_location'])

    show_settings()

    if skip_comments:
        logging.debug("skip_comments set to True. Not retrieving comments.")
    else:
        flagging_loop()


def flagging_loop():
    global SETTINGS
    while True:
        daily_flag_limit_exceeded = False
        # Recheck settings, to ensure something important didn't change while we slept
        SETTINGS = gather_settings()
        comments = retrieve_comments()
        if comments:
            for c in comments['items']:
                comment_body = BeautifulSoup(c['body']).get_text()
                prob_dist = CLASSIFIER.prob_classify(comment_body)
                try:
                    classified_as = prob_dist.max()
                    if prob_dist.prob(classified_as) >= COMMENT_TYPES_DICT[classified_as]['flagging_threshold']:
                        logging.debug("Classified: %s => As: %s => Certainty: %s => Flagged: [True]" % (
                            comment_body, classified_as, prob_dist.prob(classified_as)))
                        s.add(Comment(
                            link="http://stackoverflow.com/posts/comments/%s" % (c['comment_id']),
                            text=comment_body,
                            id=c['comment_id'],
                            score=c['score'],
                            user_id=c['owner']['user_id'],
                            reputation=c['owner']['reputation'],
                            post_type=utils.post_type_dict[c['post_type']],
                            creation_date=datetime.fromtimestamp(c['creation_date']),
                            comment_type_id=COMMENT_TYPES_DICT[classified_as]['id'],
                            system_add_date=datetime.utcnow(),
                            post_id=c['post_id']
                        ))
                        try:
                            s.commit()
                        except IntegrityError:  # Overlaps in time frames do occur, this prevents it from breaking the commit
                            # as the single record is skipped
                            logging.info("Duplicate comment skipped database insertion.  ID: %s" % (c['comment_id']))
                            s.rollback()

                        if bool(COMMENT_TYPES_DICT[classified_as]['is_flagging_enabled']):
                            daily_flag_limit_exceeded = flag_comment(c['comment_id'], classified_as)
                            if not daily_flag_limit_exceeded:
                                logging.debug("Sleeping for %s seconds" % (SETTINGS['SLEEP_BETWEEN_FLAGS']))
                                sleep(SETTINGS['SLEEP_BETWEEN_FLAGS'])
                            else:
                                break
                    else:
                        logging.debug(
                            "Classified: %s =>  As: %s => ChattyProb: %s  ObsolProb: %s  GoodProb: %s => Flagged: [False]" %
                            (comment_body, prob_dist.max(), prob_dist.prob('too chatty'),
                             prob_dist.prob('obsolete'), prob_dist.prob('good comment')
                            ))

                except UnicodeDecodeError:
                    logging.debug("Couldn't print this one.")

        if not daily_flag_limit_exceeded:
            logging.debug("Sleeping for %s seconds" % (SETTINGS['SLEEP_BETWEEN_RETRIEVE']))
            sleep(SETTINGS['SLEEP_BETWEEN_RETRIEVE'])
        else:
            sleep_time = (datetime.replace(datetime.utcnow() + timedelta(days=1), hour=0, minute=10, second=0) - datetime.utcnow()).total_seconds()
            logging.info("Daily Flagging limit has been reached. Sleeping until tomorrow (UTC) (%s seconds from now)" % (sleep_time))
            Setting.update_value(s, 'current_status', 'FLAGS EXCEEDED; SLEEPING')
            sleep(sleep_time)


def flag_comment(comment_id, classified_as):
    logging.debug("Getting flag options for comment id %s" % (comment_id))
    daily_flag_limit_exceeded = False
    try:
        flag_options = SITE.fetch('comments/%s/flags/options' % (comment_id))
    except SEAPI.SEAPIError as e:
        logging.critical("API Error occurred.")
        logging.critical("   Error URL: %s" % (e.url))
        logging.critical("   Error Number: %s" % (e.error))
        logging.critical("   Error Code: %s" % (e.code))
        logging.critical("   Error Message: %s" % (e.message))
        return

    flag_option_id = None
    for f in flag_options['items']:
        if f['description'] == classified_as:
            flag_option_id = f['option_id']
            logging.debug("Comment id %s has a flag option id of %s for being classified as %s" % (comment_id, flag_option_id, classified_as))
            break

    if flag_option_id:
        logging.info("Issuing %s flag for comment id %s" % (classified_as, comment_id))
        try:
            flag = SITE.send_data('comments/%s/flags/add' % (comment_id), option_id=flag_option_id)
            Setting.update_value(s, 'se_api_remaining_quota', flag['quota_remaining'])
        except SEAPI.SEAPIError as e:
            if e.error == 407:
                logging.info(e.message)
                daily_flag_limit_exceeded = True
            else:
                logging.critical("API Error occurred.")
                logging.critical("   Error URL: %s" % (e.url))
                logging.critical("   Error Number: %s" % (e.error))
                logging.critical("   Error Code: %s" % (e.code))
                logging.critical("   Error Message: %s" % (e.message))

    return daily_flag_limit_exceeded



def gather_settings():
    global SITE
    settings = {'API_KEY': Setting.by_name(s, 'se_api_key'),
                'API_TOKEN': Setting.by_name(s, 'se_api_token'),
                'COMMENT_FILTER': Setting.by_name(s, 'se_api_comment_filter'),
                'MAX_COMMENTS_RETRIEVE': int(Setting.by_name(s, 'flagging_max_comments_retrieve')),
                'SLEEP_BETWEEN_RETRIEVE': float(Setting.by_name(s, 'min_sleep_between_comment_fetch')),
                'SLEEP_BETWEEN_FLAGS': float(Setting.by_name(s,'min_sleep_between_flags')),
                'EPOCH': datetime.utcfromtimestamp(0),
                'CLASSIFIER_ALGORITHM': Setting.by_name(s, 'classifier_algorithm')}

    if SITE:
        SITE.page_size = settings['MAX_COMMENTS_RETRIEVE'] if settings['MAX_COMMENTS_RETRIEVE'] <= 100 else 100
        SITE.max_pages = 1 if floor(settings['MAX_COMMENTS_RETRIEVE'] / SITE.page_size) == 0 else floor(
            settings['MAX_COMMENTS_RETRIEVE'] / SITE.page_size)

    return settings


def get_timestamps():
    now_ts = int((datetime.utcnow() - SETTINGS['EPOCH']).total_seconds())
    try:
        previous_run_ts = int((datetime.strptime(Setting.by_name(s, 'current_status_last_run_datetime'),
                                             "%Y-%m-%d %H:%M:%S.%f") - SETTINGS['EPOCH']).total_seconds())
    except ValueError:
        previous_run_ts = int((datetime.strptime(Setting.by_name(s, 'current_status_last_run_datetime'),
                                             "%Y-%m-%d %H:%M:%S") - SETTINGS['EPOCH']).total_seconds())

    return now_ts, previous_run_ts


def retrieve_comments():
    now, previous = get_timestamps()
    now_readable = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    previous_readable = datetime.fromtimestamp(previous).strftime('%Y-%m-%d %H:%M:%S')
    logging.info("Retrieving comments created between %s and %s" % (previous_readable, now_readable))
    Setting.update_value(s, 'current_status', 'RETRIEVING COMMENTS')
    Setting.update_value(s, 'current_status_datetime', datetime.utcnow())
    try:
        comments = SITE.fetch('comments', filter=SETTINGS['COMMENT_FILTER'], fromdate=previous, todate=now)
    except SEAPI.SEAPIError as e:
        logging.critical("API Error occurred.")
        logging.critical("   Error URL: %s" % (e.url))
        logging.critical("   Error Number: %s" % (e.error))
        logging.critical("   Error Code: %s" % (e.code))
        logging.critical("   Error Message: %s" % (e.message))
        return

    logging.info("   %s comments retrieved" % (len(comments['items'])))

    logging.debug("Remaining Quota updated to: %s" % (comments['quota_remaining']))
    Setting.update_value(s, 'se_api_remaining_quota', comments['quota_remaining'])
    Setting.update_value(s, 'current_status', 'IDLE')
    Setting.update_value(s, 'current_status_datetime', datetime.utcnow())
    Setting.update_value(s, 'current_status_last_run_datetime', datetime.utcnow())
    return comments


def show_settings():
    logging.debug("Settings (upon entering main loop):")
    logging.debug("  API_TOKEN: %s" % (SETTINGS['API_TOKEN']))
    logging.debug("  API_KEY: %s" % (SETTINGS['API_KEY']))
    logging.debug("  COMMENT_FILTER: %s" % (SETTINGS['COMMENT_FILTER']))
    logging.debug("  MAX_COMMENTS_TO_RETRIEVE: %s" % (SETTINGS['MAX_COMMENTS_RETRIEVE']))
    logging.debug("  SLEEP_BETWEEN_RETRIEVE: %s" % (SETTINGS['SLEEP_BETWEEN_RETRIEVE']))
    logging.debug("  MAX PAGES: %s" % (SITE.max_pages))
    logging.debug("  PAGE SIZE: %s" % (SITE.page_size))
    logging.debug("  CLASSIFIER: %s" % (CLASSIFIER_DICT[SETTINGS['CLASSIFIER_ALGORITHM']]['name']))
    logging.debug("  CLASSIFIER FILE: %s" % (CLASSIFIER_DICT[SETTINGS['CLASSIFIER_ALGORITHM']]['file_location']))

if __name__ == "__main__":
    main(skip_comments=False)