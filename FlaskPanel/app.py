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
    comment_cnts = (db.session.query(CommentType.id, CommentType.name,
                func.count(CommentType.id).label('count'))
            .select_from(CommentType).join(Comment)
            .group_by(CommentType.id, CommentType.name)
            )
	comments_add_yesterday = comments=db.session.query(Comment).filter(Comment.system_add_date = date.today()-timedelta(days=1)).count()
	comments_add_today = comments=db.session.query(Comment).filter(Comment.system_add_date >= date.today()-timedelta(days=0)).count()
    comments_add_this_week = comments=db.session.query(Comment).filter(Comment.system_add_date >= date.today()-timedelta(days=7)).count()
    
    return render_template('index.html',
                            comments=db.session.query(Comment).filter_by(id=0).order_by(Comment.creation_date.desc()).all(),
                            comment_cnt = comment_cnts,
                            comments_add_this_week = comments_add_this_week,
                            pagetitle="Main")


@app.route('/training_data')
def training_data():
    return render_template('index.html',
        comments=db.session.query(Comment).filter_by(is_training=True).order_by(Comment.creation_date.desc()).all(),
        pagetitle="Training Data")


@app.route('/disputed_comments')
def disputed_data():
    return render_template('index.html',
                            comments=db.session.query(Comment).filter_by(disputed=True).order_by(Comment.creation_date.desc()).all(),
                            pagetitle="Disputed Comments")


@app.route('/automated_data')
def automated_data():
    return render_template('index.html',
                            comments=db.session.query(Comment).filter_by(added_manually=False, is_training=False).order_by(Comment.creation_date.desc()).all(),
                            pagetitle="Automatically Added Comments")


@app.route('/manual_data')
def manual_data():
    return render_template('index.html',
                            comments=db.session.query(Comment).filter_by(added_manually=True, is_training=False).order_by(Comment.creation_date.desc()).all(),
                            pagetitle="Manually Added Comments")


@app.route('/add_comments')
def add_comments():
    return render_template('add_comment.html', pagetitle="Add Comments")

    
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
        comment_data = site.fetch('comments',ids=comments, filter='!1zSsiTKfrlw0eKYQiRXjG')
        for c in comment_data['items']:
            link = "http://stackoverflow.com/posts/comments/%s" % (c['comment_id'])
            text = BeautifulSoup(c['body']).get_text()
            id = c['comment_id']
            score = c['score']
            user_id = c['owner']['user_id']
            reputation = c['owner']['reputation']
            post_type = post_type_dict[c['post_type']]
            creation_date = datetime.fromtimestamp(c['creation_date'])#.strftime("%Y-%m-%d %H:%M:%S")
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
            db.session.add(Comment(link=link,text=text, id=id, score=score, user_id=user_id, reputation=reputation,
                          post_type=post_type, creation_date=creation_date, comment_type_id=comment_type_id,added_manually=True))

        try:
            db.session.commit()
            response['success'] = True
            response['msg'] = "Comment(s) successfully added."
        except IntegrityError:
            response['msg'] = "Attempted to enter duplicate comment."
    else:
        response['msg'] = "No comments input."
    return jsonify(**response)
    
#    return render_template('index.html',
#                            comments=db.session.query(Comment).order_by(Comment.creation_date.desc()).all())
#                            # This is not correct. Needs to be filter(added_manually=False) when added_manually is added to schema

                            
@app.route('/update_comment', methods=['POST'])
def update_comment():
    pk = request.form.get('pk', -1, type=int)
    val = request.form.get('value', -1, type=int)
    
    print pk, val
    
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

    
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("80"),
        debug=True
    )