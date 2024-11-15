import mysql.connector

def connect():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="matcha",
        auth_plugin='mysql_native_password'
    )
    return connection

def get_user_tags(user_id):
    conn = connect()
    curs = conn.cursor()
    curs.execute("SELECT id, user_id, value FROM tags WHERE user_id = %s", [user_id])
    tags = []
    row = curs.fetchone()
    while row:
        tag = {}
        tag['id'] = row[0]
        tag['user_id'] = row[1]
        tag['value'] = row[2]
        tags.append(tag)
        row = curs.fetchone()
    return tags

def get_users(id):
    conn = connect()
    user_curs = conn.cursor(buffered=True)
    user_curs.execute("SELECT id, name, email, age, gender, bio, fame_rating, profile_pic, created_at FROM users WHERE id != %s", [id])
    users = []
    user_row = user_curs.fetchone()
    while user_row:
        # id is our liked
        user = {}
        user["id"] = user_row[0]
        user["name"] = user_row[1]
        user["email"] = user_row[2]
        user["age"] = user_row[3]
        user["gender"] = user_row[4]
        user["bio"] = user_row[5]
        user["fame"] = user_row[6]
        user["profile_pic"] = user_row[7]
        user["created_at"] = user_row[8]

        like_curs = conn.cursor(buffered=True)
        like_curs.execute("SELECT liked, was_liked FROM likes WHERE liked = %s AND was_liked = %s", [id, user["id"]])
        like_row = like_curs.fetchall()
        like_curs.close()

        if like_row:
            user["liked"] = True
        else:
            user["liked"] = False
        users.append(user)
        user_row = user_curs.fetchone()
    user_curs.close()
    conn.close()
    return users

def get_user_data(id):
    conn = connect()
    curs = conn.cursor()
    curs.execute("SELECT name, email, age, password, bio, gender, profile_pic, id FROM users WHERE id = %s", [id])
    row = curs.fetchone()
    user = {}
    user["name"] = row[0]
    user["email"] = row[1]
    user["age"] = row[2]
    user["password"] = row[3]
    user["bio"] = row[4]
    user["gender"] = row[5]
    user["profile_pic"] = row[6]
    user["id"] = row[7]
    return user



def get_friends(likes):
    friends = []
    for liked, was_liked in likes:
        friend = get_user_data(was_liked)
        friends.append(friend)
    return friends

def check_user_exists(fieldname, fielddata):
    conn = connect()
    curs = conn.cursor()
    curs.execute(f"SELECT {fieldname} from users where {fieldname} = %s", [fielddata])
    row = curs.fetchone()
    return not not row
