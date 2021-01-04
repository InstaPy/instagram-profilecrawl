import sys
import os
from util.download_image_post import DownloadImagePost
import json
from util.instalogger import InstaLogger
from util.settings import BASE_DIR, Settings

logger = InstaLogger.logger()


def main(arguments):
    profiles_path = arguments[1] if len(arguments) > 1 else Settings.profile_location
    abs_profiles_path = os.path.join(BASE_DIR, profiles_path)
    if not os.path.exists(abs_profiles_path):
        logger.error(f"Directory ('{abs_profiles_path}') couldn't found!")
        return

    profile_list = os.listdir(abs_profiles_path)
    if not profile_list:
        logger.error(f"Directory ('{profile_list}') is empty!")
        return

    for profile in profile_list:
        file_path = os.path.join(abs_profiles_path, profile)
        file_name, file_extension = os.path.splitext(file_path)
        if file_extension == ".json":  # check file is json
            with open(file_path, "r") as f:
                data = json.loads(f.read())
            if data is not None or data is not []:
                username = data.get("username", "")
                if data.get("posts") is not None:

                    images = [val for post in data.get("posts", []) for (key, val) in post.items() if
                              key == "preview_img"]
                    image_downloader = DownloadImagePost('images/{}'.format(username))
                    for img in images:
                        # TODO: Implement download Image URL here
                        image_downloader.extract(img[4].get("src"))
                else:
                    print("This user doesn't have any post(s) yet.")

        else:
            print("Unsupported file type")


if __name__ == "__main__":
    args = sys.argv
    main(args)
