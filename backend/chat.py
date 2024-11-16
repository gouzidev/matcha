
from flask import flash, session, jsonify
from flask import render_template, redirect, request
import db, utils
from flask_bcrypt import Bcrypt


def init_chat(app):

    @app.route("/chat", methods=["GET"])
    def chat_page():
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
        return render_template("chat.html", user=user, name=user.get("name"), friends=friends)


    @app.route("/chat/<target_id>", methods=["GET"])
    def chat_with(target_id):
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            flash("please log in first to chat!", "error")
            return redirect("/login")
        target = db.get_user_data(target_id)
        target = utils.get_user_full_pic_path("img", target)
        if not target:
            flash("this user doesn't exist !!", "error")
            return redirect("/chat")

        if not db.check_users_friends(user_id, target_id):
            flash("you must be friends to chat!", "error")
            return redirect("/chat")

        conn = db.connect()
        curs = conn.cursor()

        user = db.get_user_data(user_id)
        user = utils.get_user_full_pic_path("img", user)

        curs.execute("SELECT distinct l1.liked, l1.was_liked FROM likes l1, likes l2 WHERE l1.was_liked = l2.liked and l1.liked=%s", [user_id])
        likes = curs.fetchall()

        messages = db.get_discussion(user_id, target_id)
        friends = db.get_friends(likes)
        friends = utils.get_users_full_pic_path("img", friends)
        return render_template("chat.html", target=target, messages=messages, user=user, name=user.get("name"), friends=friends)


    @app.route("/chat/<target_id>", methods=["POST"])
    def send_msg(target_id):
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            flash("please log in first to send a message!", "error")
            return redirect("/login")
        target = db.get_user_data(target_id)
        if not target:
            flash("this user doesn't exist !!", "error")
            return redirect("/chat")

        if not db.check_users_friends(user_id, target_id):
            flash("you must be friends to chat!", "error")
            return redirect("/chat")

        msg = request.form.get("message")
        print(msg)
        if not msg:
            flash("please send a valid message", "error")
            return redirect(f"/chat/{target_id}")

        conn = db.connect()
        curs = conn.cursor()
        curs.execute("insert into messages (content, sender, receiver) values (%s, %s, %s)", [msg, user_id, target_id])
        conn.commit()
        return redirect(f"/chat/{target_id}")


    @app.route("/chat/<int:msg_id>", methods=["DELETE"])
    def delete_msg(msg_id):
        user_id = session.get("user_id")
        logged = session.get("logged")
        if not user_id or not logged:
            return jsonify({"status": 405, "msg": "unothorized, please log in first"})
        conn = db.connect()
        curs = conn.cursor()
        curs.execute("select * from messages where id=%s and sender = %s", [msg_id, user_id])
        row = curs.fetchone()
        if not row:
            flash("msg doesnt exist!", "error")
            return jsonify({"status": 404, "msg": "message not found"})
        curs.execute("delete from messages where id=%s and sender = %s", [msg_id, user_id])
        conn.commit()
        return jsonify({"status": 200, "msg": "message deleted successfully"})


