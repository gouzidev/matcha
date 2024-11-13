
from flask import Flask, flash
from flask import session, send_from_directory
from flask import render_template, request, make_response, redirect
import db, utils
from os import path, unlink, rmdir
from flask_bcrypt import Bcrypt


app = Flask(__name__, static_folder="../frontend/static",
             template_folder="../frontend/html", 
             static_url_path="/")

app.secret_key = "secret"

app.config["UPLOAD_FOLDER"] = "../frontend/static/img"

bcrypt = Bcrypt(app)

@app.route("/", methods=["GET"])
def index():
    name = session.get("name")
    email = session.get("email")
    if name and email:
        return render_template("index.html", email=email, name=name)
    return render_template("index.html")

@app.route("/explore", methods=["GET"])
def explore():
    users = db.get_users(-1)
    users.sort(key=lambda user: user['fame'], reverse=True)
    name = session.get("name")
    email = session.get("email")
    if name and email:
        return render_template("explore.html", users=users, email=email, name=name)
    return render_template("explore.html")

@app.route("/signup", methods=["GET"])
def show_signup_page():
    if session.get("logged") == True:
        return redirect("/")
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    passw = request.form.get("passw")
    gender = request.form.get("gender")

    verified = utils.verify_form_data(name, email, passw, gender)
    if not verified:
        return redirect("/profile")
    conn = db.connect()
    curs = conn.cursor()

    exists = db.check_user_exists("email", email)
    if exists:
        flash("this email already exists", "error")
        return redirect("/signup")

    hashed_password = bcrypt.generate_password_hash(passw).decode('utf-8')
    curs.execute("insert into users (name, email, password, gender) values (%s, %s, %s, %s)", [name, email, hashed_password, gender])
    conn.commit()
    flash("please login with your new account", "success")
    return redirect("/login")

@app.route("/login", methods=["GET"])
def show_login_page():
    if session.get("logged") == True:
        flash("you're already logged in", "error")
        return redirect("/")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    passw = request.form.get("passw")

    if not email or not passw:
        flash("please enter the requested credentials", "error")
        return redirect("/login")
    conn = db.connect()
    curs = conn.cursor()
    curs.execute("SELECT * FROM users WHERE email = %s", [email])
    user = curs.fetchone()
    if user:
        if bcrypt.check_password_hash(user[3], passw):
            session["logged"] = True
            session["name"] = user[1]
            session["email"] = user[2]
            session["user_id"] = user[0]
            return render_template("index.html", email=user[2], name=user[1])
    flash("wrong credentails", "error")
    return redirect("/login")

@app.route("/logout", methods=["POST"])
def logout():
    session["logged"] = False
    session.clear()
    return redirect("/")


@app.route("/chat", methods=["GET"])
def show_chat_page():
    if not session.get("logged"):
        flash("please loggin to see your chat", "error")
        return redirect("/login")
    email = session.get("email")
    name = session.get("name")
    user_id = session.get("user_id")
    users = db.get_users(user_id)
    
    if email and name:
        return render_template("chat.html", users=users, email=email, name=name)
    else:
        return render_template("login.html")


@app.route("/profile", methods=["GET"])
def show_profile_page():
    user_id = session.get("user_id")
    user_data = db.get_user_data(user_id)
    user = {}
    user["id"] = user_data["id"]
    user["name"] = user_data["name"]
    user["email"] = user_data["email"]
    user["age"] = user_data["age"]
    user["bio"] = user_data["bio"]
    user["gender"] = user_data["gender"]
    user["profile_pic"] = user_data["profile_pic"]
    if not user_id or not user:
        return redirect("/login")
    session["name"] = user["name"]
    session["email"] = user["email"]
    name = session.get("name")
    email = session.get("email")
    return render_template("profile.html", user=user, name=name, email=email)

@app.route("/profile", methods=["POST"])
def profile():
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
    # profile_pic.name
    if profile_pic:
        pic_name = utils.handle_img(app, user_id, profile_pic)
        if pic_name == None:
            return redirect("/profile")
    else:
        pic_name = None
    if not age:
        age = 0
    else:
        if not age.isdigit():
            flash("age should be a numeric value", "error")
            return redirect("/profile")
        else:
            age = int(age)
    if age > 100 or (age != 0 and age < 18):
        flash("looking at this age, this website isnt for you buddy", "error")
        return redirect("/profile")

    if not name or len(name) < 3:
        flash("please enter your valid name", "error")
        return redirect("/profile")
    if not gender or not gender.isdigit() or int(gender) < 0 or int(gender) > 1:
        flash("please select a valid gender", "error")
        print(f"gender[{gender}]")
        return redirect("/profile")
    conn = db.connect()
    curs = conn.cursor()
    user = db.get_user_data(user_id)

    if oldpassw:
        if bcrypt.check_password_hash(user["password"], oldpassw):
            if oldpassw == newpassw:
                flash("new password can't be the same as the old", "error")
            elif len(newpassw) < 8:
                flash("new password must be 8 characters at least", "error")
                return redirect("/profile")
            hashed = bcrypt.generate_password_hash(newpassw).decode('utf-8')
            if profile_pic:
                curs.execute("UPDATE users SET name = %s, age = %s, email = %s, password = %s, bio = %s, gender = %s, profile_pic = %s WHERE id=%s", [name, age, email, hashed, bio, gender, pic_name ,user_id])
            else:
                curs.execute("UPDATE users SET name = %s, age = %s, email = %s, password = %s, bio = %s, gender = %s WHERE id=%s", [name, age, email, hashed, bio, gender ,user_id])
            conn.commit()
            flash("password updated successfully", "success")
            return redirect("/profile")
        else:
            flash("wrong password", "error")
            return redirect("/profile")
    
    if profile_pic:
        curs.execute("UPDATE users SET name = %s, age = %s, email = %s, bio = %s, gender = %s , profile_pic = %s WHERE id=%s", [name, age, email, bio, gender, pic_name, user_id])
    else:
        curs.execute("UPDATE users SET name = %s, age = %s, email = %s, bio = %s, gender = %s WHERE id=%s", [name, age, email, bio, gender, user_id])
    conn.commit()
    flash("profile updated successfully", "success")

    # if not all([name, email, gender, bio, age]):
    #     return redirect("/explore")
    return redirect("/profile")


@app.route("/profile/picture/<user_id>", methods=["GET"])
def show_profile_pic(user_id):
    # user_id = session.get("user_id")
    user_data = db.get_user_data(user_id)
    print(user_data)
    profile_pic_path = user_data["profile_pic"]
    if profile_pic_path:
        return send_from_directory(path.join(app.config["UPLOAD_FOLDER"], str(user_id)), profile_pic_path)
    else:
        return render_template("profile_pic.html", img_path="http://192.168.1.110:5000/img/default.webp")


@app.route("/profile/picture/<int:user_id>", methods=["DELETE"])
def delete_profile_pic(user_id):
    id = session.get("user_id")
    if id != user_id:
        flash("error deleting your image", "error")
        return redirect("/profile")
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
            return redirect("/profile")
        if path.exists(path.join(app.config["UPLOAD_FOLDER"], str(user_id))):
            rmdir(path.join(app.config["UPLOAD_FOLDER"], str(user_id)))
        else:
            flash("error deleting your image", "error")
            return redirect("/profile")
        flash("deleted image successfully", "success")
    else:
        flash("error deleting your image (add one first)", "error")
    return redirect("/profile")


# app.run(host="127.0.0.1", port=5000, debug=True)
app.run(host="0.0.0.0", port=5000, debug=True)