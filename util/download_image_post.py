from os.path import join, exists
from os import makedirs
from .settings import BASE_DIR
import wget


class DownloadImagePost(object):

    def __init__(self, downloaded_path='images/ig_username'):
        self.downloaded_path = join(BASE_DIR, downloaded_path)
        if not exists(self.downloaded_path):
            makedirs(self.downloaded_path)

    def extract(self, url):
        wget.download(url=url, out=self.downloaded_path)
