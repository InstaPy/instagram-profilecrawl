import sys
import os
import wget
from util.download_image_post import DownloadImagePost
import json
from config import ROOT_DIR


def main(arguments):
    profiles_path = arguments[1] if len(arguments) > 1 else "profiles"

    profile_list = os.listdir(profiles_path)

    for profile in profile_list:
        file_path = os.path.join(ROOT_DIR, profiles_path, profile)
        file_name, file_extension = os.path.splitext(file_path)
        if file_extension == ".json":  # check file is json
            f = open(file_path, "r")
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
