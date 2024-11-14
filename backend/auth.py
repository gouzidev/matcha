from flask import flash,  session
from flask import render_template, request, redirect
import db, utils
from flask_bcrypt import Bcrypt

def init_auth(app):

    bcrypt = Bcrypt(app)

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
            return redirect("/user")
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
