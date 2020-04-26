from os.path import abspath, dirname, join
from os import getenv
from dotenv import load_dotenv

ROOT_DIR = abspath(dirname(__file__))
dotenv_path = join(ROOT_DIR, '.env')
load_dotenv(dotenv_path)
IG_USERNAME = getenv("IG_USERNAME", "")
IG_PASSWORD = getenv("IG_PASSWORD", "")