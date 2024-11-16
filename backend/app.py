
from flask import Flask, flash
from flask import session
from flask import render_template, redirect
import db, utils
from flask_bcrypt import Bcrypt
import auth
import chat
import user

app = Flask(__name__, static_folder="../frontend/static",
             template_folder="../frontend/html", 
             static_url_path="/")

app.secret_key = "secret"

app.config["UPLOAD_FOLDER"] = "../frontend/static/img"

bcrypt = Bcrypt(app)

auth.init_auth(app)

user.init_user(app)

chat.init_chat(app)

@app.template_filter("first_4_words")
def first_4_words(s):
    words = s.split()
    first_4 = ' '.join(words[:4])
    if len(words) > 4:
        return first_4 + "..."
    else:
        return first_4

@app.route("/", methods=["GET"])
def index():
    name = session.get("name")
    email = session.get("email")
    if name and email:
        return render_template("index.html", email=email, name=name)
    return render_template("index.html")




@app.route("/explore", methods=["GET"])
def explore():
    user_id = session.get("user_id") or -1

    users = db.get_users(user_id)
    users = utils.get_users_full_pic_path("img", users)
    users.sort(key=lambda user: user['fame'], reverse=True)
    name = session.get("name")
    email = session.get("email")
    if name and email:
        return render_template("explore.html", users=users, email=email, name=name)
    return render_template("explore.html", users=users)


# app.run(host="127.0.0.1", port=5000, debug=True)
app.run(host="0.0.0.0", port=5000, debug=True)