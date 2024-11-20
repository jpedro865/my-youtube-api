from sqlalchemy import select, or_, func
from src.db.connection import get_session, get_base
from src.models import ApiException
from fastapi import UploadFile
from src.controllers.token import verify_token
from src.controllers.user import user_to_json
from datetime import datetime
import ffmpeg
import os

Session = get_session()
UserDb = get_base().classes.user
VideoDb = get_base().classes.video

# error message
USER_NOT_FOUND_MSG = "User not found"
VIDEO_NOT_FOUND_MSG = "Video not found"


# This function will add a video to the user
def add_video_to_user(user_id: int, name: str, video: UploadFile):
  if video is None:
    raise ApiException(400, 1001, ["Video source is required"])
  if name is None:
    raise ApiException(400, 1002, ["Video name is required"])
  if video.content_type != "video/mp4":
    raise ApiException(400, 1003, ["Video must be in mp4 format"])
  try:
    # get user and check if it exists
    user = Session.query(UserDb).filter(UserDb.id == user_id).first()
    if user is None:
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    
    # save video to public directory
    video_path = save_video_public(video)
    if video_path is None:
      raise ApiException(500, 1999, ["Error while saving video"])
    
    # get video info (width, height, duration)
    video_info = getVideoInfo(video_path)
    
    video = VideoDb(
      user_id=user_id,
      name=name,
      source=video_path,
      duration=video_info["duration"],
      views=0,
      created_at=datetime.now(),
      enabled=True
    )
    Session.add(video)
    Session.commit()
    return {
      "message": "Video added successfully",
      "data": video_to_json(video, user)
    }
  except Exception as e:
    Session.rollback()
    print("Error while adding video to db:")
    print(e)
    if USER_NOT_FOUND_MSG in str(e):
      raise ApiException(404, 1004, [USER_NOT_FOUND_MSG])
    raise ApiException(500, 1999, ["{}".format(e)])

def video_to_json(video, user):
  return {
    "id": video.id,
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
  publicVideoPath = "{}/public/videos/".format(os.getcwd())

  # create video directory
  try:
    if not os.path.exists(publicVideoPath):
      os.makedirs(publicVideoPath)
  except:
    raise ApiException(500, 1999, ["Error while creating video directory"])
  
  # check if video already exists
  try:
    if os.path.exists("{}{}".format(publicVideoPath, video.filename)):
      video.filename = "{}_{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), video.filename)
  except:
    raise ApiException(500, 1999, ["Error while checking video existence"])
  
  try:
    with open("{}{}".format(publicVideoPath, video.filename), "wb") as buffer:
      buffer.write(video.file.read())
  except:
    raise ApiException(500, 1999, ["Error while saving video"])

  return "{}{}".format(publicVideoPath, video.filename)


def getVideoInfo(path):
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
