from sqlalchemy import select, func
from src.db.connection import get_session, get_base
from src.models import ApiException
from math import ceil

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

# this function will get list of comments of a video
def get_comments_of_video(video_id: str, page: int, perPage: int):
  session = get_session()
  try:
    if page < 1:
      raise ValueError(PAGE_NOT_FOUND_MSG)
    video = session.query(VideoDb).filter(VideoDb.id == video_id).first()
    if video is None:
      raise ValueError(VIDEO_NOT_FOUND_MSG)
    
    # get total number of comments
    try:
      total_comments = session.query(func.count(CommentDb.id)).filter(CommentDb.video_id == video_id).scalar()
    except Exception as e:
      raise ValueError("Error while getting total videos")
    
    # calculate pagination offset
    offset = ((page -1 ) * perPage)
    if offset < 0:
      offset = 0
    
    # get comments
    comments = session.query(CommentDb).filter(CommentDb.video_id == video_id).offset(offset).limit(perPage).all()
    
    # verify if pages exists (Page 1 always exists)
    if (len(comments) == 0 and page != 1):
      raise ValueError(PAGE_NOT_FOUND_MSG)

    return {
      "message": "OK",
      "data": [comment_to_json(comment) for comment in comments],
      "pager": {
        "current": page,
        "total": ceil(total_comments / perPage)
      }
    }
  except Exception as e:
    if VIDEO_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, VIDEO_NOT_FOUND_MSG)
    if PAGE_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1005, PAGE_NOT_FOUND_MSG)
    raise ApiException(500, 1999, "INTERNAL_ERROR")
  

def comment_to_json(comment):
  return {
    "id": comment.id,
    "body": comment.body,
    "user": {
      "id": comment.user.id,
      "username": comment.user.username,
      "pseudo": comment.user.pseudo,
    }
  }
