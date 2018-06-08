import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings:
    profile_location = os.path.join(BASE_DIR, 'profiles')
    profile_commentors_location = os.path.join(BASE_DIR, 'profiles')
    limit_amount = 12000
