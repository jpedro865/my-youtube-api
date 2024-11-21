from sqlalchemy import select, func
from src.db.connection import get_session, get_base
from src.models import ApiException

UserDb = get_base().classes.user
VideoDb = get_base().classes.video
CommentDb = get_base().classes.comment

# error message
USER_NOT_FOUND_MSG = "User not found"
VIDEO_NOT_FOUND_MSG = "Video not found"
PAGE_NOT_FOUND_MSG = "Page not found"
COMMENT_NOT_FOUND_MSG = "Comment not found"
COMMENT_BODY_REQUIRED = "Comment body is required"

# this function will add a comment to a video
def add_comment_to_video(video_id: str, user_id: int, body: str):
  session = get_session()
  try:
    if body is None or body == "":
      raise ValueError(COMMENT_BODY_REQUIRED)
    # get video
    video = session.query(VideoDb).filter(VideoDb.id == video_id).first()
    if video is None:
      raise ValueError(VIDEO_NOT_FOUND_MSG)
    
    # get user
    user = session.query(UserDb).filter(UserDb.id == user_id).first()
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    
    comment = CommentDb(
      body=body,
      video_id=video_id,
      user_id=user_id
    )
    session.add(comment)
    session.commit()
    return {
      "message": "OK",
      "data": comment_to_json(comment)
    }
  except Exception as e:
    session.rollback()
    if VIDEO_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, VIDEO_NOT_FOUND_MSG)
    if COMMENT_BODY_REQUIRED in str(e):
      raise ApiException(400, 1001, COMMENT_BODY_REQUIRED)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1003, USER_NOT_FOUND_MSG)
    raise ApiException(500, 1999, "INTERNAL_ERROR")
  

def comment_to_json(comment):
  return {
    "id": comment.id,
    "body": comment.video_id,
    "user": {
      "id": comment.user.id,
      "username": comment.user.username,
      "pseudo": comment.user.pseudo,
    }
  }
