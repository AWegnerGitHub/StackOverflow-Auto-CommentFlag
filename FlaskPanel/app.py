from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from models.secomments import Comment, CommentType
from SEAPI.SEAPI import SEAPI, SEAPIError
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta


app = Flask(__name__)
app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

post_type_dict = {
    "question": 1,
    "answer": 2
}


@app.route('/')
def index():
    header_counts = populate_header_counts()

    print comments_flag_this_week
    return render_template('index.html',
                       comments=db.session.query(Comment).filter_by(id=0).order_by(Comment.creation_date.desc()).all(),
                       header_counts=header_counts,
                       pagetitle="Main")


@app.route('/training_data')
def training_data():
    header_counts = populate_header_counts()
    return render_template('index.html',
                           comments=db.session.query(Comment).filter_by(is_training=True).order_by(
                               Comment.creation_date.desc()).all(),
                           header_counts=header_counts,
                           pagetitle="Training Data")


@app.route('/disputed_comments')
def disputed_data():
    header_counts = populate_header_counts()
    return render_template('index.html',
                           comments=db.session.query(Comment).filter_by(disputed=True).order_by(
                               Comment.creation_date.desc()).all(),
                           header_counts=header_counts,
                           pagetitle="Disputed Comments")


@app.route('/automated_data')
def automated_data():
    header_counts = populate_header_counts()
    return render_template('index.html',
                           comments=db.session.query(Comment).filter_by(added_manually=False,
                                                                        is_training=False).order_by(
                               Comment.creation_date.desc()).all(),
                           header_counts=header_counts,
                           pagetitle="Automatically Added Comments")


@app.route('/manual_data')
def manual_data():
    header_counts = populate_header_counts()
    return render_template('index.html',
                           comments=db.session.query(Comment).filter_by(added_manually=True,
                                                                        is_training=False).order_by(
                               Comment.creation_date.desc()).all(),
                           header_counts=header_counts,
                           pagetitle="Manually Added Comments")


@app.route('/add_comments')
def add_comments():
    return render_template('add_comment.html', suppress_overview=True, pagetitle="Add Comments")


@app.route('/add_comment_data', methods=['POST'])
def add_comment_data():
    comment_list = request.form.getlist('comments[]')
    comment_types_list = request.form.getlist('commenttypes[]')
    comments = []
    response = {
        'success': False,
        'msg': 'Unknown Error'
    }

    if comment_list[0]:
        for c in comment_list:
            try:
                comments.append(c.split("#")[1].split("_")[0][7:])
            except IndexError:
                response['msg'] = "Invalid Input. Need full URL to comment."
                return jsonify(**response)

        comment_dict = dict(zip(comments, comment_types_list))
        # THIS IS WHERE WE PULL COMMENTS FROM API
        site = SEAPI("stackoverflow")
        comment_data = site.fetch('comments', ids=comments, filter='!1zSsiTKfrlw0eKYQiRXjG')
        for c in comment_data['items']:
            link = "http://stackoverflow.com/posts/comments/%s" % (c['comment_id'])
            text = BeautifulSoup(c['body']).get_text()
            id = c['comment_id']
            score = c['score']
            user_id = c['owner']['user_id']
            reputation = c['owner']['reputation']
            post_type = post_type_dict[c['post_type']]
            creation_date = datetime.fromtimestamp(c['creation_date'])  # .strftime("%Y-%m-%d %H:%M:%S")
            comment_type_id = comment_dict[unicode(c['comment_id'])]

            # print "-" * 15
            # print """
            # Link => %s
            # Text => %s
            # ID => %s
            # Score => %s
            # User => %s
            # Rep => %s
            # Post Type => %s
            # Creation Date => %s
            # Comment Type => %s
            # """ % (
            # link,
            # text,
            # id,
            # score,
            # user_id,
            # reputation,
            # post_type,
            # creation_date,
            # comment_type_id,
            # )
            db.session.add(Comment(link=link, text=text, id=id, score=score, user_id=user_id, reputation=reputation,
                                   post_type=post_type, creation_date=creation_date, comment_type_id=comment_type_id,
                                   added_manually=True))

        try:
            db.session.commit()
            response['success'] = True
            response['msg'] = "Comment(s) successfully added."
        except IntegrityError:
            response['msg'] = "Attempted to enter duplicate comment."
    else:
        response['msg'] = "No comments input."
    return jsonify(**response)


@app.route('/update_comment', methods=['POST'])
def update_comment():
    pk = request.form.get('pk', -1, type=int)
    val = request.form.get('value', -1, type=int)

    response = {
        'success': False,
        'msg': 'Unknown Error'
    }

    if pk < 0 or val < 0:
        response['msg'] = "Invalid values passed. Attempted to update Comment ID: %s to Comment Type: %s" % (pk, val)
    else:
        #        db.session.query(Comment).update({"id": pk, "comment_type_id": val})
        db.session.query(Comment).filter_by(id=pk).update(dict(comment_type_id=val))
        db.session.commit()
        response['success'] = True
        response['msg'] = "Updated Comment ID: %s to Comment Type: %s" % (pk, val)

    return jsonify(**response)


# -- Support Functions
def populate_header_counts():
    resp_dict = {}
    resp_dict['comment_cnts'] = (db.session.query(CommentType.id, CommentType.name,
                                     func.count(CommentType.id).label('count'))
                    .select_from(CommentType).join(Comment)
                    .group_by(CommentType.id, CommentType.name)
    )
    resp_dict['comments_manual_add_today'] = db.session.query(Comment).filter(
        Comment.system_add_date >= date.today() - timedelta(days=0),
        Comment.added_manually == 1
        ).count()
    resp_dict['comments_manual_add_yesterday'] = db.session.query(Comment).filter(
        Comment.system_add_date == date.today() - timedelta(days=1),
        Comment.added_manually == 1
        ).count()
    resp_dict['comments_manual_add_this_week'] = db.session.query(Comment).filter(
        Comment.system_add_date >= date.today() - timedelta(days=7),
        Comment.added_manually == 1
        ).count()

    resp_dict['comments_auto_add_today'] = db.session.query(Comment).filter(
        Comment.system_add_date >= date.today() - timedelta(days=0),
        Comment.added_manually == 0
        ).count()
    resp_dict['comments_auto_add_yesterday'] = db.session.query(Comment).filter(
        Comment.system_add_date == date.today() - timedelta(days=1),
        Comment.added_manually == 0
        ).count()
    resp_dict['comments_auto_add_this_week'] = db.session.query(Comment).filter(
        Comment.system_add_date >= date.today() - timedelta(days=7),
        Comment.added_manually == 0
        ).count()

    resp_dict['comments_flag_today'] = db.session.query(Comment).filter(
        Comment.system_add_date >= date.today() - timedelta(days=0),
        Comment.comment_type_id,
        Comment.is_training == 0,
        Comment.added_manually == 0
        ).count()
    resp_dict['comments_flag_yesterday'] = db.session.query(Comment).filter(
        Comment.system_add_date == date.today() - timedelta(days=1),
        Comment.comment_type_id != 1,
        Comment.is_training == 0,
        Comment.added_manually == 0
        ).count()
    resp_dict['comments_flag_this_week'] = db.session.query(Comment).filter(
        Comment.system_add_date >= date.today() - timedelta(days=7),
        Comment.comment_type_id,
        Comment.is_training == 0,
        Comment.added_manually == 0
        ).count()

    return resp_dict




# -- Additional Template Filters
@app.template_filter()
def friendly_time(dt, past_="ago", future_="from now", default="just now"):
    """
    Returns string representing "time since" or "time until" e.g. 3 days ago, 5 hours from now etc.
    """

    now = datetime.now()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period:
            return "%d %s %s" % (period,
                                 singular if period == 1 else plural,
                                 past_ if dt_is_past else future_)

    return default



if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("80"),
        debug=True
    )