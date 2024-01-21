"""Python Flask WebApp Auth0 integration example
"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import certifi

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, session, url_for, request

from random import randint, choice

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import string
import time

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


uri = env.get("MONGODB_ATLAS_URI")

ca = certifi.where()
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=ca)

def randomStringCode(length):
    return ''.join([choice(string.ascii_letters+string.digits) for i in range(length)])


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["cya_db"]
dbcol_users = db["users"]
dbcol_courses = db["courses"]
dbcol_lessons = db["lessons"]

class Data:
    class Course:
        @staticmethod
        def create(name, subject, **kwargs):
            course_id = randomStringCode(5)
            while True:
                if Data.Course.get(course_id):
                    course_id = randomStringCode(6)
                else:
                    break
            return dbcol_courses.insert_one({
                "_id": course_id,
                "name": name,
                "subject": subject,
                "teacher": {
                    "name": session.get("user")["userinfo"]["name"],
                    "email": session.get("user")["userinfo"]["email"]
                },
                "students": [],
                "lessons": [],
                **kwargs})

        @staticmethod
        def get(id, check_user_access=False):
            c = dbcol_courses.find_one({"_id": id})
            if not check_user_access:
                return c
            e = session.get("user")["userinfo"]["email"]
            if e in c['students'] or e == c['teacher']['email']:
                return c
            else:
                return None

        @staticmethod
        def add_lesson(course_id, name, video, quiz_questions):
            e = session.get("user")["userinfo"]["email"]
            if not Data.Course.get(course_id)["teacher"]["email"] == e:
                return False
            lesson = {
                "name": name,
                "video_url": video,
                "quiz": quiz_questions
            }
            dbcol_courses.update({"_id": course_id}, {"$push": {"lessons": lesson}})

        @staticmethod
        def get_all_courses_of_user():
            e = session.get("user")["userinfo"]["email"]
            d = dbcol_courses.find({"$or": [
                {"teacher.email": e},
                {"students": e}
            ]})
            return list(d)

        @staticmethod
        def get_user_role_in_course(course_id):
            course = Data.Course.get(course_id, True)
            if not course:
                return 'none'
            if course['teacher']['email'] == session.get('user')['userinfo']['email']:
                return 'teacher'
            else:
                return 'student'

        @staticmethod
        def join(course_id):
            if not Data.Course.get(course_id):
                return False
            email = session.get('user')['userinfo']['email']
            dbcol_courses.update_one({"_id": course_id}, {"$push": {"students": email}})

    class Lesson:
        @staticmethod
        def get(lesson_id):
            return dbcol_lessons.find_one({"_id": lesson_id})

        @staticmethod
        def all_from_course(course_id):
            return list(dbcol_lessons.find({"course_id": course_id}))

        @staticmethod
        def all_with_status(status):
            search = {}
            search[session.get("user")["userinfo"]["email"]] = status
            return list(dbcol_lessons.find(search))

        @staticmethod
        def all_from_course_with_status(course_id, status, check_user_access):
            if check_user_access and not Data.Course.get(course_id, check_user_access):
                return []
            search = {}
            search[session.get("user")["userinfo"]["email"]] = status
            return list(dbcol_lessons.find({"course_id": course_id, **search}))

        @staticmethod
        def create(name, video_content, course_id):
            course = Data.Course.get(course_id)
            students = course['students']
            status = {}
            for s in students:
                status[s] = False
            dbcol_lessons.insert_one({
                "name": name,
                "course_id": course_id,
                "video": video_content,
                "student_status": status
                })

    class User:
        # note: i am using email as the identifier, in a real application i would use the user's public id
        @staticmethod
        def create(email, name, role="none", **kwargs):
            return dbcol_users.insert_one({"name": name, "email": email, "role": role, **kwargs})

        @staticmethod
        def get(email):
            return dbcol_users.find_one({"email": email})

        @staticmethod
        def create_if_new(email, name, role="none", **kwargs):
            if not Data.User.get(email):
                return Data.User.create(email, name, role, **kwargs)
            else:
                return None

        @staticmethod
        def update(email, **kwargs):
            return dbcol_users.update_one({"email": email}, {"$set": kwargs})


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

def get_role():
    r = session.get("role")
    if r:
        return r
    user = session.get("user")
    if not user:
        return "none"
    u = Data.User.get(user["userinfo"]["email"])
    return u["role"]

# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        user=session.get("user")
    )

@app.route("/testing")
def testing():
    return render_template(
        "testing.html",
        user=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4)
    )

@app.route("/roles")
def roles():
    r = session.get("user")

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    info = session["user"]["userinfo"]
    if Data.User.create_if_new(info["email"], info["name"]):
        return redirect("/setup")

    userdata = Data.User.get(info["email"])
    if not "role" in userdata.keys():
        return redirect("/setup")


    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/setup")
def setup():
    if not session.get("user"):
        return redirect("/")
    return "<a href='setup/setrole?role=teacher'>Teacher</a> <a href='setup/setrole?role=student'>Student</a>"

@app.route("/setup/setrole")
def setrole():
    if not session.get("user"):
        return redirect("/")
    try:
        e = session.get("user")["userinfo"]["email"]
        r = request.args.get("role")
        Data.User.update(e, role=r)
        session["role"] = r
        return redirect("/dashboard")
    except Exception as e:
        print(e)
        return redirect("/logout")


@app.route("/dashboard")
def dashboard():
    user = session.get("user")['userinfo']
    if not user:
        return redirect("/")
    role = get_role()
    if role == "teacher" or role == "student":
        courses = Data.Course.get_all_courses_of_user()
        print(json.dumps(courses, indent=4))
        return render_template("dashboard.html", user=user, role=role, courses=courses)
    else:
        return redirect("/setup")

@app.route("/course/create", methods=["POST"])
def create_course():
    print("CREATING A COURSE")
    data = request.json
    print(data)
    try:
        Data.Course.create(data['name'], data['subject'], students=data['students'])
        return jsonify({"status": "success"}, 200)
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}, 500)

@app.route("/course/join", methods=["POST"])
def join_course():
    print("JOINING A COURSE")
    data = request.json
    print(data)
    try:
        Data.Course.join(data['course_id'])
        return jsonify({"status": "success"}, 200)
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}, 500)

@app.route("/course/<course_id>")
def course_page(course_id):
    course = Data.Course.get(course_id, True)
    if not course:
        return redirect("/dashboard")
    user = session.get("user")["userinfo"]
    r = Data.Course.get_user_role_in_course(course_id)
    lessons = Data.Lesson.all_from_course(course_id)
    return render_template("course.html", course=course, user=user, role=r, lessons=lessons)

@app.route("/lesson/create", methods=["POST"])
def create_lesson():
    name = request.form.get("name")
    course_id = request.form.get("course_id")
    lessonvideo = request.files.get("lessonvideo")
    print(list(request.files))
    if not lessonvideo:
        return jsonify({"status": "failed"})
    content = lessonvideo.stream.read()
    Data.Lesson.create(name, content, course_id)
    return jsonify({"status": "success"})

@app.route("/course/<course_id>/lesson/<lesson_id>")
def lesson_page(course_id, lesson_id):
    lesson = Data.Lesson.get(lesson_id)
    course = Data.Course.get(course_id, True)
    if not lesson:
        return redirect("/course/" + course_id)
    user = session.get("user")["userinfo"]
    return render_template("lesson.html", course=course, user=user, lesson=lesson)

@app.route("/course/<course_id>/lesson/<lesson_id>/quiz")
def lesson_quiz(course_id, lesson_id):
    lesson = Data.Lesson.get(lesson_id)
    course = Data.Course.get(course_id, True)
    if not lesson:
        return redirect("/course/" + course_id)
    user = session.get("user")["userinfo"]
    return render_template("quiz.html", course=course, user=user, lesson=lesson)

@app.route("/course/<course_id>/lesson/create")
def create_lesson_page(course_id):
    course = Data.Course.get(course_id, True)
    if not course:
        return redirect("/dashboard")
    user = session.get("user")["userinfo"]
    r = Data.Course.get_user_role_in_course(course_id)
    if r != 'teacher':
        return redirect("/course/" + course_id)
    return render_template("lessonCreate.html", course=course, user=user)

@app.route("/course/<course_id>/lesson")
def slash_lesson(course_id):
    return redirect("/course/" + course_id)

# @app.route("lesson/submit", methods=["POST"])
# def submit_lesson():
    

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

# @app.errorhandler(Exception)
# def error(e):
#     print(e)
#     return render_template('error.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000), debug=True)
