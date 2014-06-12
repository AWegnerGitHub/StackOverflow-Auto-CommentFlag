from utils import utils
from models.secomments import Comment, CommentType, Setting

logging = utils.setup_logging("utils_funcs")
logging.info("test")

s = utils.connect_to_db("sqlite:///FlaskPanel/se_comments.db")
print s.query(Setting).filter_by(name='se_api_key').one()