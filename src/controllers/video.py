from sqlalchemy import select, func
from src.db.connection import get_session, get_base
from src.models import ApiException, VideoList
from fastapi import UploadFile
from src.controllers.token import verify_token
from src.controllers.user import user_to_json
from datetime import datetime
import ffmpeg
import os
from math import ceil

UserDb = get_base().classes.user
VideoDb = get_base().classes.video

# error message
USER_NOT_FOUND_MSG = "User not found"
VIDEO_NOT_FOUND_MSG = "Video not found"
PAGE_NOT_FOUND_MSG = "Page not found"
WRONG_VIDEO_FORMAT = "Video must be in mp4 format"
ERROR_SAVING_VIDEO = "Error while saving video"
VIDEO_NAME_REQUIRED ="Video name is required"
VIDEO_SOURCE_REQUIRED = "Video source is required"

# This function will return a list of videos
def get_videos(body: VideoList):
  session = get_session()
  try:
    if body.page < 1:
      raise ValueError(PAGE_NOT_FOUND_MSG)
    # get video of user
    user = None
    if body.user is not None and body.user != "":
      if isinstance(body.user, str):
        sql_rec = select(UserDb).where(UserDb.username == body.user)
        user = session.scalars(sql_rec).first()
        if user is None:
          raise ValueError(USER_NOT_FOUND_MSG)
      elif isinstance(body.user, int):
        user = session.query(UserDb).filter(UserDb.id == body.user).first()
        if user is None:
          raise ValueError(USER_NOT_FOUND_MSG)
    
    sql_rec = select(VideoDb)
    sql_rec_count = select(func.count(VideoDb.id))
    if user is not None:
      # search for videos of the user
      sql_rec = sql_rec.where(VideoDb.user_id == user.id)
      sql_rec_count = sql_rec_count.where(VideoDb.user_id == user.id)
    if body.duration is not None:
      # search for videos with duration between duration - 10 and duration + 10
      sql_rec = sql_rec.where(VideoDb.duration.between(body.duration - 10, body.duration + 10))
      sql_rec_count = sql_rec_count.where(VideoDb.duration.between(body.duration - 10, body.duration + 10))
    if body.name is not None:
      # search for videos with name containing the search string
      sql_rec = sql_rec.where(VideoDb.name.like("%{}%".format(body.name)))
      sql_rec_count = sql_rec_count.where(VideoDb.name.like("%{}%".format(body.name)))

    # get total number of videos
    try:
      total_videos = session.scalars(sql_rec_count).first()
    except Exception as e:
      raise ValueError("Error while getting total videos")

    # calculate pagination offset
    offset = ((body.page -1 ) * body.perPage)
    if offset < 0:
      offset = 0
    
    try :
      # limit the number of videos fetched and offset
      sql_rec = sql_rec.limit(body.perPage).offset(offset)
      # execute the query and get the videos
      videos = session.scalars(sql_rec).all()
    except Exception as e:
      raise ValueError("Error while fetching videos")
    
    # verify if pages exists (Page 1 always exists)
    if (len(videos) == 0 and body.page != 1):
      raise ValueError(PAGE_NOT_FOUND_MSG)
    
    total_pages = ceil(total_videos / body.perPage)

    data = []
    for video in videos:
      user = session.query(UserDb).filter(UserDb.id == video.user_id).first()
      data.append(video_to_json(video, user))
    
    return {
      "message": "OK",
      "data": data,
      "pager": {
        "current": body.page,
        "total": total_pages,
      }
    }
  except Exception as e:
    print("Error while getting videos from db:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    if PAGE_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [PAGE_NOT_FOUND_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will update a video
def update_video(video_id: int, name: str):
  session = get_session()
  try:
    if name is None:
      raise ValueError("Nothing to update")
    
    video = session.query(VideoDb).filter(VideoDb.id == video_id).first()
    if video is None:
      raise ValueError(VIDEO_NOT_FOUND_MSG)

    # update video name
    video.name = name
    session.commit()

    # get user info
    user = session.query(UserDb).filter(UserDb.id == video.user_id).first()
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)

    return {
      "message": "OK",
      "data": video_to_json(video, user)
    }
  except Exception as e:
    session.rollback()
    print("Error while updating video:")
    print(e)
    if VIDEO_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1005, [VIDEO_NOT_FOUND_MSG])
    if "Nothing to update" in str(e):
      raise ApiException(400, 1007, ["Nothing to update"])
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will add a video to the user
def add_video_to_user(user_id: int, name: str, video: UploadFile):
  session = get_session()
  if video is None:
    raise ValueError(VIDEO_SOURCE_REQUIRED)
  if name is None:
    raise ValueError(VIDEO_NAME_REQUIRED)
  if video.content_type != "video/mp4":
    raise ValueError(WRONG_VIDEO_FORMAT)
  try:
    # get user and check if it exists
    user = session.query(UserDb).filter(UserDb.id == user_id).first()
    if user is None:
      raise ValueError(USER_NOT_FOUND_MSG)
    
    # save video to public directory
    video_path = save_video_public(video)
    if video_path is None:
      raise ValueError(ERROR_SAVING_VIDEO)
    
    # get video info (width, height, duration)
    video_info = get_video_info(video_path)
    
    video = VideoDb(
      user_id=user_id,
      name=name,
      source=video_path,
      duration=video_info["duration"],
      views=0,
      created_at=datetime.now(),
      enabled=True
    )
    session.add(video)
    session.commit()
    return {
      "message": "OK",
      "data": video_to_json(video, user)
    }
  except Exception as e:
    session.rollback()
    print("Error while adding video to db:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    if WRONG_VIDEO_FORMAT in str(e):
      raise ApiException(400, 1003, [WRONG_VIDEO_FORMAT])
    if ERROR_SAVING_VIDEO in str(e):
      raise ApiException(500, 1999, [ERROR_SAVING_VIDEO])
    if VIDEO_NAME_REQUIRED in str(e):
      raise ApiException(400, 1002, [VIDEO_NAME_REQUIRED])
    if VIDEO_SOURCE_REQUIRED in str(e):
      raise ApiException(400, 1002, [VIDEO_SOURCE_REQUIRED])
    raise ApiException(500, 1999, ["{}".format(e)])

# This function will delete a video
def delete_video(video_id: int, user_id: int):
  session = get_session()
  try:
    video = session.query(VideoDb).filter(VideoDb.id == video_id).first()
    if video is None:
      raise ValueError(VIDEO_NOT_FOUND_MSG)
    if video.user.id != user_id:
      raise ValueError("Forbidden")
    
    # delete video
    session.delete(video)
    session.commit()
    return {
      "message": "OK",
    }
  except Exception as e:
    print("Error while deleting video:")
    print(e)
    if VIDEO_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1005, [VIDEO_NOT_FOUND_MSG])
    if "Forbidden" in str(e):
      raise ApiException(403, 1006, ["Forbidden"])
    raise ApiException(500, 1999, ["{}".format(e)])
  
############################################################## HELPER FUNCTIONS ##############################################################

def video_to_json(video, user):
  return {} if video is None else {
    "id": video.id,
    "name": video.name,
    "source": video.source,
    "created_at": video.created_at,
    "views": video.views,
    "enabled": video.enabled,
    "user": {
      "id": user.id,
      "username": user.username,
      "pseudo": user.pseudo,
      "created_at": user.created_at
    },
    "format": {
      "1080": video.source,
      "720": video.source,
      "480": video.source,
      "360": video.source,
      "240": video.source,
      "144": video.source
    }
  }

# Saves video received from the user to the public directory
# Returns the path to the saved video
def save_video_public(video: UploadFile) -> str:
  public_video_path = "{}/public/videos/".format(os.getcwd())

  # create video directory
  try:
    if not os.path.exists(public_video_path):
      os.makedirs(public_video_path)
  except Exception:
    raise ApiException(500, 1999, ["Error while creating video directory"])
  
  # check if video already exists
  try:
    if os.path.exists("{}{}".format(public_video_path, video.filename)):
      video.filename = "{}_{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), video.filename)
  except Exception:
    raise ApiException(500, 1999, ["Error while checking video existence"])
  
  try:
    with open("{}{}".format(public_video_path, video.filename), "wb") as buffer:
      buffer.write(video.file.read())
  except Exception:
    raise ApiException(500, 1999, ["Error while saving video"])

  return "{}{}".format(public_video_path, video.filename)

# This function meta data of a video
def get_video_info(path):
  try:
    probe = ffmpeg.probe(path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
      return None
    return {
      "width": video_stream['width'],
      "height": video_stream['height'],
      "duration": video_stream['duration']
    }
  except Exception as e:
    print("Error while getting video info:")
    print(e)
    return None
