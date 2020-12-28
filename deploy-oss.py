import os
import oss2

AUTH = oss2.Auth(os.environ.get('AccessKeyId'), os.environ.get('AccessKeySecret'))
BUCKET = oss2.Bucket(AUTH, os.environ.get('EndPoint'), os.environ.get('BucketName'))

ROOT_DIR = os.path.join(os.getcwd(), 'output')
PATH_LIST = [ROOT_DIR]

while len(PATH_LIST):
  p = PATH_LIST.pop()
  if os.path.isdir(p):
    PATH_LIST += map(lambda i: os.path.join(p, i), os.listdir(p))
  elif os.path.isfile(p):
    BUCKET.put_object_from_file(os.path.relpath(p, ROOT_DIR), p)
