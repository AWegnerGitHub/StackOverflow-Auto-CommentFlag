from utils import utils
from models.secomments import Setting, Comment
from SEAPI import SEAPI
from bs4 import BeautifulSoup
from datetime import datetime
from math import floor
from time import sleep
from sqlalchemy.exc import IntegrityError

logging = utils.setup_logging("retrieve_comments")
s = utils.connect_to_db("sqlite:///FlaskPanel/se_comments.db")

# Gather our settings
API_KEY = Setting.by_name(s, 'se_api_key')
API_TOKEN = Setting.by_name(s, 'se_api_token')
COMMENT_FILTER = Setting.by_name(s, 'se_api_comment_filter')
MAX_COMMENTS_RETRIEVE = int(Setting.by_name(s, 'flagging_max_comments_retrieve'))
SLEEP_BETWEEN_RETRIEVE = float(Setting.by_name(s, 'min_sleep_between_comment_fetch'))
EPOCH = datetime.utcfromtimestamp(0)


# Set up our SITE object
SITE = SEAPI.SEAPI('stackoverflow', key=API_KEY, access_token=API_TOKEN)


def main():
    logging.debug("Beginning main loop")
    logging.debug("Settings:")
    logging.debug("  API_TOKEN: %s" % (API_TOKEN))
    logging.debug("  API_KEY: %s" % (API_KEY))
    logging.debug("  COMMENT_FILTER: %s" % (COMMENT_FILTER))
    logging.debug("  MAX_COMMENTS_TO_RETRIEVE: %s" % (MAX_COMMENTS_RETRIEVE))
    logging.debug("  SLEEP_BETWEEN_RETRIEVE: %s" % (SLEEP_BETWEEN_RETRIEVE))

    SITE.max_pages = floor(MAX_COMMENTS_RETRIEVE / SITE.page_size)
    logging.debug("  MAX PAGES: %s" % (SITE.max_pages))
    loop = 0
    while loop < 5:
        comments = retrieve_comments()
        for c in comments['items']:
            s.add(Comment(
                link = "http://stackoverflow.com/posts/comments/%s" % (c['comment_id']),
                text = BeautifulSoup(c['body']).get_text(),
                id = c['comment_id'],
                score = c['score'],
                user_id = c['owner']['user_id'],
                reputation = c['owner']['reputation'],
                post_type = utils.post_type_dict[c['post_type']],
                creation_date = datetime.fromtimestamp(c['creation_date']),
                comment_type_id = 1,
                system_add_date = datetime.utcnow()
            ))
            try:
                s.commit()
            except IntegrityError:              # Overlaps in time frames do occur, this prevents it from breaking the commit
                                                # as the single record is skipped
                logging.warning("Duplicate comment skipped database insertion.  ID: %s" % (c['comment_id']))
                s.rollback()
            loop += 1
            logging.debug("Sleeping for %s seconds" % (SLEEP_BETWEEN_RETRIEVE))
            sleep(SLEEP_BETWEEN_RETRIEVE)


def get_timestamps():
    now_ts = int((datetime.utcnow() - EPOCH).total_seconds())
    previous_run_ts = int((datetime.strptime(Setting.by_name(s, 'current_status_last_run_datetime'), "%Y-%m-%d %H:%M:%S.%f") - EPOCH).total_seconds())
    return now_ts, previous_run_ts


def retrieve_comments():
    now, previous = get_timestamps()
    now_readable = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    previous_readable = datetime.fromtimestamp(previous).strftime('%Y-%m-%d %H:%M:%S')
    logging.info("Retrieving comments created between %s and %s" % (previous_readable, now_readable))
    Setting.update_value(s, 'current_status', 'RETRIEVING COMMENTS')
    Setting.update_value(s, 'current_status_datetime', datetime.utcnow())
    comments = SITE.fetch('comments', filter=COMMENT_FILTER, fromdate=previous, todate=now)
    logging.info("   %s comments retrieved" % (len(comments['items'])))


    logging.debug("Remaining Quota updated to: %s" % (comments['quota_remaining']))
    Setting.update_value(s, 'se_api_remaining_quota', comments['quota_remaining'])
    Setting.update_value(s, 'current_status', 'IDLE')
    Setting.update_value(s, 'current_status_datetime', datetime.utcnow())
    Setting.update_value(s, 'current_status_last_run_datetime', datetime.utcnow())

    return comments



if __name__ == "__main__":
    main()