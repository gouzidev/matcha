from os import listdir, path, remove, makedirs
from werkzeug.utils import secure_filename
from flask import flash

def verify_ext(name):
    name_parts = name.split(".")
    allowed_exts = ["jpeg", "png", "jpg", "webp"]
    if name_parts[-1] not in allowed_exts:
        return False
    return True

def delete_files_in_directory(directory_path):
   try:
     files = listdir(directory_path)
     for file in files:
       file_path = path.join(directory_path, file)
       if path.isfile(file_path):
         remove(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")


def handle_img(app, user_id, profile_pic):
    if not profile_pic:
       return None
    pic_name = secure_filename(profile_pic.filename)
    if verify_ext(pic_name):
        imgs_dir = app.config["UPLOAD_FOLDER"]
        user_folder = path.join(imgs_dir, str(user_id))
        if not path.exists(user_folder):
            makedirs(user_folder, exist_ok=True)
        else:
            delete_files_in_directory(user_folder)

        full_profile_pic_path = path.join(user_folder, pic_name)
        profile_pic.save(full_profile_pic_path)
        return pic_name
    else:
       flash("allowed image extensions: ['.jpeg', '.jpg', '.png', '.webp']", "error")
       return None

def verify_form_data(name, email, passw, gender):
        if not name:
            flash("please enter a valid name", "error")
            return False
        if not email:
            flash("please enter a valid email", "error")
            return False
        if not passw:
            flash("please enter a valid password", "error")
            return False
        if len(passw) < 8:
            flash("password must be at least 8 characters", "error")
            return False
        if not gender:
            flash("please select your gender", "error")
            return False
        return True

def get_users_full_pic_path(imgs_dir, users):
    for user in users:
        pic = user["profile_pic"]
        id = user["id"]
        full_path = path.join(imgs_dir, str(id), pic)
        user["profile_pic"] = full_path
    return users

def get_user_full_pic_path(imgs_dir, user):
    pic = user["profile_pic"]
    id = user["id"]
    full_path = path.join(imgs_dir, str(id), pic)
    user["profile_pic"] = full_path
    return user

def filter_users_data(users):
    for user in users:
        user.pop("fame")
    return users

