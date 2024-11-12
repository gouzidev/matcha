
from flask import Flask, flash
from flask import session
from flask import render_template, request, make_response, redirect
import db
from flask_bcrypt import Bcrypt

app = Flask(__name__, static_folder="../frontend/static",
             template_folder="../frontend/html", 
             static_url_path="/")

app.secret_key = "secret"

# app["UPLOAD_FOLDER"] = "./public/images"

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
    if not name:
        flash("please enter a valid name", "error")
        return redirect("/signup")
    email = request.form.get("email")
    if not email:
        flash("please enter a valid email", "error")
        return redirect("/signup")
    passw = request.form.get("passw")
    if not passw:
        flash("please enter a valid password", "error")
        return redirect("/signup")
    if len(passw) < 8:
        flash("password must be at least 8 characters", "error")
        return redirect("/signup")
    gender = request.form.get("gender")
    if not gender:
        flash("please select your gender", "error")
        return redirect("/signup")
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

def verify_ext(name):
    name_parts = name.split(".")
    allowed_exts = ["jpeg", "png"]
    if name_parts[-1] not in allowed_exts:
        return False
    return True

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
    profile_pic_path = None
    # profile_pic.name
    pic_name = profile_pic.filename
    if verify_ext(pic_name):
        profile_pic_path = f"/home/gouzi/Desktop/code 💻/web/matcha/frontend/static/img/"
        profile_pic.save(profile_pic_path + str(user_id))

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

    if oldpassw:
        user = db.get_user_data(user_id)
        if bcrypt.check_password_hash(user["password"], oldpassw):
            if oldpassw == newpassw:
                flash("new password can't be the same as the old", "error")
            elif len(newpassw) < 8:
                flash("new password must be 8 characters at least", "error")
                return redirect("/profile")
            hashed = bcrypt.generate_password_hash(newpassw).decode('utf-8')
            curs.execute("UPDATE users SET name = %s, age = %s, email = %s, password = %s, bio = %s, gender = %s, profile_pic = %s WHERE id=%s", [name, age, email, hashed, bio, gender, profile_pic_path ,user_id])
            conn.commit()
            flash("password updated successfully", "success")
            return redirect("/profile")
        else:
            flash("wrong password", "error")
            return redirect("/profile")
    
    curs.execute("UPDATE users SET name = %s, age = %s, email = %s, bio = %s, gender = %s , profile_pic = %s WHERE id=%s", [name, age, email, bio, gender, profile_pic_path, user_id])
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
        return render_template("profile_pic.html", img_path=profile_pic_path)
    else:
        return render_template("profile_pic.html", img_path="http://192.168.1.110:5000/img/default.webp")


# app.run(host="127.0.0.1", port=5000, debug=True)
app.run(host="0.0.0.0", port=5000, debug=True)