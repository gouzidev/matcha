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

def get_users(id):
    conn = connect()
    curs = conn.cursor()
    curs.execute("SELECT id, name, email, age, gender, bio, fame_rating, profile_pic, created_at FROM users WHERE id != %s", [id])
    users = []
    row = curs.fetchone()
    while row:
        user = {}
        user["id"] = row[0]
        user["name"] = row[1]
        user["email"] = row[2]
        user["age"] = row[3]
        user["gender"] = row[4]
        user["bio"] = row[5]
        user["fame"] = row[6]
        user["profile_pic"] = row[7]
        user["created_at"] = row[8]
        users.append(user)
        row = curs.fetchone()
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

def check_user_exists(fieldname, fielddata):
    conn = connect()
    curs = conn.cursor()
    curs.execute(f"SELECT {fieldname} from users where {fieldname} = %s", [fielddata])
    row = curs.fetchone()
    return not not row
