
from flask import flash, session, send_from_directory
from flask import render_template, request, redirect, jsonify
import db, utils
from os import path, unlink, rmdir
from requests import get as get_request
from requests import post as post_request
from flask_bcrypt import Bcrypt

def tag_exists(tags, tag_value):
    for tag in tags:
        if tag.get("value") == tag_value:
            return True
    return False
    
def init_user(app):

    bcrypt = Bcrypt(app)

    @app.route("/user", methods=["GET"])
    def show_profile_page():
        user_id = session.get("user_id")
        if not user_id:
            return redirect("/login")
        user_data = db.get_user_data(user_id)
        tags = db.get_user_tags(user_id)
        user = {}
        user["id"] = user_data["id"]
        user["name"] = user_data["name"]
        user["email"] = user_data["email"]
        user["age"] = user_data["age"]
        user["bio"] = user_data["bio"]
        user["gender"] = user_data["gender"]
        user["profile_pic"] = user_data["profile_pic"]
        user["tags"] = tags
        session["name"] = user["name"]
        session["email"] = user["email"]
        name = session.get("name")
        email = session.get("email")
        return render_template("user.html", user=user, name=name, email=email)

    @app.route("/user", methods=["POST"])
    def user():
        user_id = session.get("user_id")
        if not user_id:
            return redirect("/login")

        name = request.form.get("name")
        email = request.form.get("email")
        gender = request.form.get("gender")
        bio = request.form.get("bio")
        age = request.form.get("age")
        newpassw = request.form.get("newpassw")
        oldpassw = request.form.get("oldpassw")
        profile_pic = request.files.get("profile_pic")
        tag = request.form.get("tag")
        
        if profile_pic:
            pic_name = utils.handle_img(app, user_id, profile_pic)
            if pic_name == None:
                return redirect("/user")
        else:
            pic_name = None
        if not age:
            age = 0
        else:
            if not age.isdigit():
                flash("age should be a numeric value", "error")
                return redirect("/user")
            else:
                age = int(age)
        if age > 100 or (age != 0 and age < 18):
            flash("looking at this age, this website isnt for you buddy", "error")
            return redirect("/user")

        if not name or len(name) < 3:
            flash("please enter your valid name", "error")
            return redirect("/user")
        if not gender or not gender.isdigit() or int(gender) < 0 or int(gender) > 1:
            flash("please SELECT a valid gender", "error")
            return redirect("/user")
        if tag:
            tags = db.get_user_tags(user_id)
            if tag_exists(tags, tag):
                flash("this tag already exists", "error")
                print("error")
                return redirect("/user")
            else:
                if not user_id:
                    flash("please log in to post a tag", "error")
                    return redirect("/login")


        conn = db.connect()
        curs = conn.cursor()
        user = db.get_user_data(user_id)

        if oldpassw:
            if bcrypt.check_password_hash(user["password"], oldpassw):
                if oldpassw == newpassw:
                    flash("new password can't be the same as the old", "error")
                elif len(newpassw) < 8:
                    flash("new password must be 8 characters at least", "error")
                    return redirect("/user")
                hashed = bcrypt.generate_password_hash(newpassw).decode('utf-8')
                if profile_pic:
                    curs.execute("UPDATE users SET name = %s, age = %s, email = %s, password = %s, bio = %s, gender = %s, profile_pic = %s WHERE id=%s", [name, age, email, hashed, bio, gender, pic_name ,user_id])
                else:
                    curs.execute("UPDATE users SET name = %s, age = %s, email = %s, password = %s, bio = %s, gender = %s WHERE id=%s", [name, age, email, hashed, bio, gender ,user_id])
                conn.commit()
                flash("password updated successfully", "success")
                return redirect("/user")
            else:
                flash("wrong password", "error")
                return redirect("/user")
        
        if profile_pic:
            curs.execute("UPDATE users SET name = %s, age = %s, email = %s, bio = %s, gender = %s , profile_pic = %s WHERE id=%s", [name, age, email, bio, gender, pic_name, user_id])
        else:
            curs.execute("UPDATE users SET name = %s, age = %s, email = %s, bio = %s, gender = %s WHERE id=%s", [name, age, email, bio, gender, user_id])
        if tag:
            curs.execute("INSERT INTO tags (user_id, value) VALUES (%s, %s)", [user_id, tag])
        conn.commit()
        flash("profile updated successfully", "success")

        # if not all([name, email, gender, bio, age]):
        #     return redirect("/explore")
        return redirect("/user")


    @app.route("/user/<int:user_id>", methods=["GET"])
    def show_user_page(user_id):
        user_data = db.get_user_data(user_id)
        tags = db.get_user_tags(user_id)
        user = {}
        user["id"] = user_data["id"]
        user["name"] = user_data["name"]
        user["email"] = user_data["email"]
        user["age"] = user_data["age"]
        user["bio"] = user_data["bio"]
        user["gender"] = user_data["gender"]
        user["profile_pic"] = user_data["profile_pic"]
        user["tags"] = tags

        user = utils.get_user_full_pic_path("img", user)

        name = session.get("name")
        email = session.get("email")
        return render_template("user_page.html", user=user, name=name, email=email)


    @app.route("/user/picture/<user_id>", methods=["GET"])
    def show_profile_pic(user_id):
        # user_id = session.get("user_id")
        user_data = db.get_user_data(user_id)
        profile_pic_path = user_data["profile_pic"]
        if profile_pic_path:
            return send_from_directory(path.join(app.config["UPLOAD_FOLDER"], str(user_id)), profile_pic_path)
        else:
            return render_template("profile_pic.html", img_path="http:///127.0.0.1:5000/img/default.webp")


    @app.route("/user/picture/<int:user_id>", methods=["DELETE"])
    def delete_profile_pic(user_id):
        id = session.get("user_id")
        if id != user_id:
            flash("error deleting your image", "error")
            return redirect("/user")
        user_data = db.get_user_data(user_id)
        profile_pic_name = user_data["profile_pic"]
        
        if profile_pic_name:
            conn = db.connect()
            curs = conn.cursor()
            curs.execute("UPDATE users SET profile_pic = %s WHERE id=%s", [None, user_id])
            conn.commit()
            if path.exists((path.join(app.config["UPLOAD_FOLDER"], str(user_id), profile_pic_name))):
                unlink(path.join(app.config["UPLOAD_FOLDER"], str(user_id), profile_pic_name))
            else:
                flash("error deleting your image", "error")
                return redirect("/user")
            if path.exists(path.join(app.config["UPLOAD_FOLDER"], str(user_id))):
                rmdir(path.join(app.config["UPLOAD_FOLDER"], str(user_id)))
            else:
                flash("error deleting your image", "error")
                return redirect("/user")
            flash("deleted image successfully", "success")
        else:
            flash("error deleting your image (add one first)", "error")
        return redirect("/user")

    @app.route("/tag/<int:user_id>/<int:tag_id>", methods=["DELETE"])
    def delete_tag(user_id, tag_id):
        id = session.get("user_id")
        logged = session.get("logged")
        if not id or user_id != id or not logged:
            return jsonify({"success": False, "message": "please loggin first"}), 401
        conn = db.connect()
        curs = conn.cursor()
        curs.execute("SELECT id, user_id, value from tags where user_id=%s and id=%s", [user_id, tag_id])
        row = curs.fetchone()
        if not row:
            flash("tag isn't found", "error")
            return jsonify({"success": False, "message": "tag isn't found."}), 404
        
        curs.execute("delete from tags where id=%s", [tag_id])
        conn.commit()
        flash("tag is deleted successfully", "success")
        return jsonify({"success": True, "message": "Tag deleted successfully."}), 200

    @app.route("/like/<int:target_id>", methods=["POST"])
    def post_like(target_id):
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            flash("please log in to like someone!", "error")
            return redirect("/login")
        conn = db.connect()
        curs = conn.cursor()

        curs.execute("SELECT liked, was_liked FROM likes WHERE liked = %s AND was_liked = %s", [user_id, target_id])
        row = curs.fetchall()
        if row:
            curs.execute("DELETE FROM likes WHERE liked = %s AND was_liked = %s", [user_id, target_id])
            flash("unliked successfully!", "success")
        else:
            curs.execute("INSERT INTO likes (liked, was_liked) VALUES (%s, %s)", [user_id, target_id])
            flash("liked successfully!", "success")
        conn.commit()
        return redirect("/explore")

    @app.route("/chat/<int:target_id>", methods=["POST"])
    def chat(target_id):
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            flash("please log in to chat with someone!", "error")
            return redirect("/login")
        conn = db.connect()
        curs = conn.cursor()

        curs.execute("SELECT liked, was_liked FROM likes WHERE liked = %s AND was_liked = %s", [user_id, target_id])
        row1 = curs.fetchall()
        if not row1:
            flash("you must like the person first to chat with them!", "error")
            return redirect("/explore")
        curs.execute("SELECT liked, was_liked FROM likes WHERE liked = %s AND was_liked = %s", [target_id, user_id])
        row2 = curs.fetchall()
        if not row2:
            flash("you must be liked by the person first to chat with them!", "error")
        flash("now you can talk your 'Person'!", "success")

        return redirect("/explore")

    @app.route("/chat", methods=["GET"])
    def chat_page():
        # print("here ")
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            flash("please log in to chat with someone!", "error")
            return redirect("/login")
        conn = db.connect()
        curs = conn.cursor()

        user = db.get_user_data(user_id)
        user = utils.get_user_full_pic_path("img", user)

        curs.execute("SELECT distinct l1.liked, l1.was_liked FROM likes l1, likes l2 WHERE l1.was_liked = l2.liked and l1.liked=%s", [user_id])
        likes = curs.fetchall()

        friends = db.get_friends(likes)
        friends = utils.get_users_full_pic_path("img", friends)
        # print(friends)
        return render_template("chat.html", user=user, name=user.get("name"), friends=friends)


    @app.route("/chat/<user_id>", methods=["GET"])
    def chat_with(user_id):
        # print("here ")
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            flash("please log in to chat with someone!", "error")
            return redirect("/login")
        conn = db.connect()
        curs = conn.cursor()

        user = db.get_user_data(user_id)
        user = utils.get_user_full_pic_path("img", user)

        curs.execute("SELECT distinct l1.liked, l1.was_liked FROM likes l1, likes l2 WHERE l1.was_liked = l2.liked and l1.liked=%s", [user_id])
        likes = curs.fetchall()

        friends = db.get_friends(likes)
        friends = utils.get_users_full_pic_path("img", friends)
        # print(friends)
        return render_template("chat.html", user=user, name=user.get("name"), friends=friends)
