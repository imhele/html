import os
import oss2
from base64 import b64encode
from functools import partial
from hashlib import md5
from requests.structures import CaseInsensitiveDict


class Uploader:
    __output_path: str

    bucket: oss2.Bucket
    put_object_headers: CaseInsensitiveDict = CaseInsensitiveDict({
        'x-oss-object-acl': oss2.OBJECT_ACL_PUBLIC_READ
    })

    def __init__(self, bucket: oss2.Bucket, output_path: str):
        self.bucket = bucket
        self.__output_path = os.path.abspath(output_path)

    def start(self) -> None:
        for dirname, dirnames, filenames in os.walk(self.__output_path):
            ossdir = os.path.relpath(dirname, self.__output_path)
            ossdir = ossdir if ossdir != '.' else ''
            for filename in filenames:
                osskey = os.path.join(ossdir, filename)
                filepath = os.path.join(dirname, filename)
                if self.__should_skip_upload(filepath, osskey):
                    print('Skip upload %s' % osskey)
                    continue
                print('Uploading %s...' % osskey)
                self.bucket.put_object_from_file(
                    osskey, filepath, headers=self.put_object_headers)

    def __calc_local_md5(self, filepath: str) -> str:
        md5_hash = md5()
        with open(filepath, mode='rb') as f:
            for buffer in iter(partial(f.read, 128), b''):
                md5_hash.update(buffer)
        return b64encode(md5_hash.digest()).decode()

    def __fetch_remote_md5(self, osskey: str) -> str:
        try:
            return self.bucket.head_object(osskey).headers['content-md5']
        except:
            return ''

    def __should_skip_upload(self, filepath: str, osskey: str) -> bool:
        remote_md5 = self.__fetch_remote_md5(osskey)
        return bool(remote_md5 and remote_md5 == self.__calc_local_md5(filepath))


if __name__ == '__main__':
    EndPoint = os.environ.get('EndPoint')
    BucketName = os.environ.get('BucketName')
    AccessKeyId = os.environ.get('AccessKeyId')
    AccessKeySecret = os.environ.get('AccessKeySecret')

    auth = oss2.AuthV2(AccessKeyId, AccessKeySecret)
    bucket = oss2.Bucket(auth, EndPoint, BucketName)

    Uploader(bucket, 'output').start()
