#!flask/bin/python
from flask import Flask, jsonify, request
import random

import google_auth
import mysql.connector

import json
import string
from flask_oauth import OAuth


app = Flask(__name__)

app.secret_key = "12322222222222"

app.register_blueprint(google_auth.app)
SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '914338622258418'
FACEBOOK_APP_SECRET = 'e0f1ed736e6afc38c1f2d20cdee917ad'


@app.route('/')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()

        email = user_info['email']
        return checkExist(email)

        # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info,
        #                                                                                                     indent=4) + "</pre>"

    return 'You are not currently logged in.'


@app.route('/blog/api/v1.0/add', methods=['POST'])
def create_data():
    if not request.json:
        return jsonify({'result': 'Invalid payload'})
    if not 'token' in request.json:
        return jsonify({'result': 'Token is invalid'})
    else:
        result = check_token(request.json['token'])
        if result != "success":
            return jsonify({'result': result})

    if not 'name' in request.json or request.json['name'] is None:
        return jsonify({'result': 'name is invalid'})
    if not 'content' in request.json or request.json['content'] is None:
        return jsonify({'result': 'content is invalid'})
    if not 'writer' in request.json or request.json['writer'] is None:
        return jsonify({'result': 'writer is invalid'})
    sql_insert_query = """ INSERT INTO article(article_name, article_content, writer) VALUES (%s,%s, %s)"""
    insert_tuple = (request.json['name'], request.json['content'], request.json['writer'])
    return insert_data(sql_insert_query, insert_tuple)


@app.route('/blog/api/v1.0/info', methods=['POST'])
def create_info():
    if not request.json:
        return jsonify({'result': 'Invalid payload'})
    if not 'token' in request.json:
        return jsonify({'result': 'Token is invalid'})
    # else:
    #     #     result = check_token(request.json['token'])
    #     #     if result != "success":
    #     #         return jsonify({'result': result})

    if not 'email' in request.json or request.json['email'] is None:
        return jsonify({'result': 'email is invalid'})
    if not 'name' in request.json or request.json['name'] is None:
        return jsonify({'result': 'name is invalid'})
    if not 'phone_number' in request.json or request.json['phone_number'] is None:
        return jsonify({'result': 'phone_number is invalid'})
    if not 'job' in request.json or request.json['job'] is None:
        return jsonify({'result': 'job is invalid'})
    is_exist = check_email_exist(request.json['email'])
    print("Exists: " + is_exist)
    if check_email_exist(request.json['email']) == "exist":
        sql_insert_query = """ UPDATE users set name = %s, phone_number = %s, job = %s where email = %s"""
        insert_tuple = (request.json['name'], request.json['phone_number'], request.json['job'], request.json['email'])
    else:
        sql_insert_query = """ INSERT INTO users(email, name, phone_number, job) VALUES (%s, %s, %s, %s)"""
        insert_tuple = (request.json['email'], request.json['name'], request.json['phone_number'], request.json['job'])
    return insert_data(sql_insert_query, insert_tuple)


@app.route('/blog/api/v1.0/emotion', methods=['POST'])
def create_emotion():
    if not request.json:
        return jsonify({'result': 'Invalid payload'})
    if not 'token' in request.json:
        return jsonify({'result': 'Token is invalid'})
    else:
        result = check_token(request.json['token'])
        if result != "success":
            return jsonify({'result': result})

    if not 'emotion' in request.json or request.json['emotion'] is None:
        return jsonify({'result': 'Emotion is invalid'})
    if not 'article' in request.json or request.json['article'] is None:
        return jsonify({'result': 'Article is invalid'})
    if not 'name' in request.json or request.json['name'] is None:
        return jsonify({'result': 'Name is invalid'})
    if request.json['emotion'] == 'like':
        sql_insert_query = """ INSERT INTO emotion(article, name) VALUES (%s, %s)"""
    else:
        sql_insert_query = """ DELETE FROM emotion where article = %s and name = %s"""
    insert_tuple = (request.json['article'], request.json['name'])
    return insert_data(sql_insert_query, insert_tuple)


@app.route('/blog/api/v1.0/getBlog', methods=['GET'])
def get_blog():
    if request.args.get('token') is None:
        return jsonify({'result': 'Token is invalid'})
    else:
        result = check_token(request.args.get('token'))
        if result != "success":
            return jsonify({'result': result})

    name = request.args.get('name')
    article = request.args.get('article')
    # print("name: " + name)
    # print("article: " + article)
    return get_data(article, name)


def insert_data(sql_query, data):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='mydb',
                                             user='root',
                                             password='123456789')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, data)
        connection.commit()
        print("command executed successfully into python_users table")
        return jsonify({'result': 'success'})
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed command executed record into python_users table {}".format(error))
    finally:
        # closing database connection.
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return jsonify({'result': 'fail'})


def get_data(article, name):
    try:
        mySQLConnection = mysql.connector.connect(host='localhost',
                                                  database='mydb',
                                                  user='root',
                                                  password='123456789')
        cursor = mySQLConnection.cursor()

        if not article and not name:
            sql_select_query = """select article_name, substring(article_content, 1, 10), writer from article"""
            cursor.execute(sql_select_query)
        elif not article and name:
            sql_select_query = """select article_name, substring(article_content, 1, 10), writer from article where writer = %s"""
            data = (name,)
            cursor.execute(sql_select_query, data)
        elif article and name:
            sql_select_query = """select article_name, article_content, writer from article where writer = %s and article_name = %s"""
            data = (name, article,)
            cursor.execute(sql_select_query, data)
        sql_select_like_query = """ select name from emotion where article  = %s"""
        record = cursor.fetchall()
        result = []

        for row in record:
            data = (row[0],)
            print("Row: " + row[0])
            cursor.execute(sql_select_like_query, data)
            list_name = cursor.fetchall()
            result.append(Result(row[0], row[1], row[2], list_name).to_dict())
        return json.dumps(result, ensure_ascii=False)
    except mysql.connector.Error as error:
        print("Failed to get record from database: {}".format(error))
    finally:
        # closing database connection.
        if mySQLConnection.is_connected():
            cursor.close()
            mySQLConnection.close()
            print("connection is closed")
    return jsonify({'result': 'fail'})


def check_email_exist(email):
    mySQLConnection = mysql.connector.connect(host='localhost',
                                              database='mydb',
                                              user='root',
                                              password='123456789')
    cursor = mySQLConnection.cursor()
    sql_select_like_query = """ select email from users where email  = %s"""
    print("email: " + email)
    cursor.execute(sql_select_like_query, (email,))
    record = cursor.fetchall()
    if record is None:
        return "not exist"
    else:
        return "exist"


def checkExist(email):
    try:
        mySQLConnection = mysql.connector.connect(host='localhost',
                                                  database='mydb',
                                                  user='root',
                                                  password='123456789')
        cursor = mySQLConnection.cursor()
        sql_select_query = """ select email, name, phone_number, job, user_type from users where email = %s"""
        cursor.execute(sql_select_query, (email,))
        row = cursor.fetchall()
        if row is None or cursor.rowcount == 0:
            sql_insert_query = """ insert into users(email, token, user_type) values(%s,%s, %s)"""
            token = randomString(20)
            data = (email, token, 'google')
            cursor.execute(sql_insert_query, data)
            mySQLConnection.commit()
            return jsonify({'result': 'success', 'token': token})
        else:
            for record in row:
                if record[4] == 'facebook':
                    if not record[1] or record[1] is None or not record[2] or record[2] is None:
                        return jsonify({'result': 'need more information: name and phone_number'})
                    else:
                        return jsonify({'result': 'system is saving you as facebook user'})
                elif record[4] == 'google':
                    if not record[1] or record[1] is None or not record[3] or record[3] is None:
                        return jsonify({'result': 'need more information: name and job'})
                    else:
                        return jsonify({'result': 'login success'})
    except mysql.connector.Error as error:
        print("Failed to get record from database: {}".format(error))
        mySQLConnection.rollback()
    finally:
        # closing database connection.
        if mySQLConnection.is_connected():
            cursor.close()
            mySQLConnection.close()
            print("connection is closed")
    return jsonify({'result': 'fail'})


def check_token(token):
    try:
        mySQLConnection = mysql.connector.connect(host='localhost',
                                                  database='mydb',
                                                  user='root',
                                                  password='123456789')
        cursor = mySQLConnection.cursor()
        sql_check_token = """select name, phone_number, job, user_type, token from users where token = %s """
        cursor.execute(sql_check_token, (token,))
        record = cursor.fetchone()
        if record is None or not record:
            return "Token is invalid"
        if record[3] == 'facebook':
            if record[0] is None or not record[0] or record[1] is None or not record[1]:
                return "need more information: name and phone_number"
        elif record[3] == 'google':
            if record[0] is None or not record[0] or record[2] is None or not record[2]:
                return "need more information: name and job"
        return "success"
    except mysql.connector.Error as error:
        print("Failed to get record from database: {}".format(error))
    finally:
        # closing database connection.
        if mySQLConnection.is_connected():
            cursor.close()
            mySQLConnection.close()
            print("connection is closed")
    return "success"


def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=id,name,email')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['email'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


class Result:
    def __init__(self, article_name, article_content, writer, list_name):
        self.article_name = article_name
        self.article_content = article_content
        self.writer = writer
        self.list_name = list_name

    def to_dict(self):
        return {"article_name": self.article_name, "article_content": self.article_content, "writer": self.writer,
                "people_like": self.list_name}


if __name__ == '__main__':
    app.run(debug=True)
