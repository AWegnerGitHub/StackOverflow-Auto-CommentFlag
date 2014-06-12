import csv
from utils import utils

logging = utils.setup_logging("populate_database")
s = utils.connect_to_db("sqlite:///FlaskPanel/se_comments.db")

#base.Base.metadata.create_all(engine)

#s = session()
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