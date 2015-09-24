#!/usr/bin/env python

"""
    flask-forum
    Copyright (C) 2011 Tom Dryer <tomdryer.com@gmail.com>
    License: 3-clause BSD
"""

#TODO: format reply text before writing it to the database
#TODO: add CSRF token to logout
#TODO: come up with a better SQL query for topics()

#import sqlite3

from pymongo import MongoClient
from pymongo import DESCENDING
from bson.son import SON
from bson.objectid import ObjectId
# import gridfs
client = MongoClient()
db = client.flask_forumD
# set_db_open()
# fs = gridfs.GridFS(db)
# thumbs = gridfs.GridFS(db, collection='thumb')




from bcrypt import hashpw, gensalt
from string import ascii_uppercase, ascii_lowercase, digits
from datetime import datetime
from time import time
from flask import Flask, render_template, request, g, redirect, session, \
    abort, url_for, flash
#from flaskext.wtf import Form, TextField, PasswordField, Required, EqualTo, \
#    Length, ValidationError, TextAreaField
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField,  \
    validators, ValidationError, TextAreaField

app = Flask(__name__)

DATABASE = "flask-forum.db"
app.secret_key = "development key"
MAX_USERNAME_LENGTH = 20

class RegistrationForm(Form):
    username = TextField("Username", validators=[validators.Required(), \
            validators.Length(max=MAX_USERNAME_LENGTH)])
    password1 = PasswordField("Password", validators=[validators.Required()])
    password2 = PasswordField("Password (verify)", validators=[validators.Required(), \
            validators.EqualTo("password1", message="Passwords must match.")])

    def validate_username(form, field):
        # check if username is in use
        username = field.data
        existing = db.users.find({"username":[username]})
  #      existing = query_db("SELECT * FROM users WHERE username = ?", \
  #              [username], one=True)
        if len(list(existing)) != 0:
            raise ValidationError("Sorry, this username is already taken.")

class LoginForm(Form):
    username = TextField("Username", validators=[validators.Required(), \
            validators.Length(max=MAX_USERNAME_LENGTH)])
    password = PasswordField("Password", validators=[validators.Required()])

class ReplyForm(Form):
    content = TextAreaField("Reply", validators=[validators.Required()])

class NewTopicForm(Form):
    subject = TextField("Subject", validators=[validators.Required()])
    content = TextAreaField("Reply", validators=[validators.Required()])

def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d @ %I:%M %p')

def format_elapsed_datetime(time):
    print "time:"
    print time
    seconds = int(timestamp()) - int(time)
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    if days > 1:
        return "%i days ago" % days
    elif days == 1:
        return "1 day ago"
    elif hours > 1:
        return "%i hours ago" % hours
    elif hours == 1:
        return "1 hour ago"
    elif minutes > 1:
        return "%i minutes ago" % minutes
    elif minutes == 1:
        return "1 minute ago"
    elif seconds > 1:
        return "%i seconds ago" % seconds
    else:
        return "1 second ago"

def timestamp():
    return str(int(time()))

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def db_closed():
    return db_closed

def set_db_closed():
    db_closed = 1

def set_db_open():
    db_closed = 0

@app.before_request
def before_request():
    # connect database
    # db = sqlite3.connect(DATABASE)
    # if db_closed():
    db = client.flask_forumD
    db_closed = 0
    # look up the current user
    g.username = None
    if "username" in session:
        user = [session["username"]][0] 
        print user
        print "****"
        doc = db.user.find({"username":user})
        if len(list(doc)) > 0:
            g.username = list(db.user.find({"username":user}))[0]["username"]
        else:
            print "user not found"
            g.username = [session["username"]][0]  

@app.after_request
def after_request(response):
   # db.close()
    db_closed = 1
    return response

@app.route('/')
def topics():
    # get a list of topics sorted by the date of their last reply
    # requires aggregation unwind

    pipeline = [
        {"$unwind": "$reply"},
        {"$group": {"_id": "$_id", "subject":{"$first":"$subject"}, "count": {"$sum": 1},"max_date": {"$max": "$reply.ts"}}},
        {"$sort": SON([("max_date", -1), ("count", -1)])}
    ]
    topics = db.subject.aggregate(pipeline)['result']

    for topic in topics:
        # get number of replies to topic
        reply_count = topic['count']
        topic["replies"] = reply_count 
        # get date of most recent reply
        last_reply = topic['max_date']
        topic["last_reply_date"] = last_reply
    return render_template("topics.html", topics=topics)
'''
def topics():
    # get a list of topics sorted by the date of their last reply
    # requires aggregation unwind
    topics = query_db("SELECT * FROM topic ORDER BY (SELECT MAX(time) FROM \
            reply WHERE reply.topic_id = topic.topic_id) DESC")
    for topic in topics:
        # get number of replies to topic
        reply_count = query_db("SELECT count(*) FROM reply WHERE topic_id = ?", 
                [topic["topic_id"]], one=True)["count(*)"]
        topic["replies"] = reply_count - 1
        # get date of most recent reply
        last_reply = query_db("SELECT time FROM reply WHERE topic_id = ? ORDER \
                BY time DESC LIMIT 1", [topic["topic_id"]], one=True)["time"]
        topic["last_reply_date"] = last_reply
    return render_template("topics.html", topics=topics)
'''
@app.route('/topic/new', methods=['GET', 'POST'])
def new_topic():
    form = NewTopicForm()
    if form.validate_on_submit():
        new_topic_id = post_topic(form.subject.data, form.content.data)
        flash("New topic posted.")
        return redirect('/topic/' + new_topic_id)
    return render_template("newtopic.html", form=form)

@app.route('/topic/<topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    # view or post to a topic
    t_id = ObjectId(topic_id)
    subject = list(db.subject.find({"_id":t_id}))[0]['subject']
  #  subject = query_db("SELECT subject FROM topic WHERE topic_id = ?", 
  #          [topic_id], one=True)
    if subject is None:
        abort(404)
    subject = subject[0]
    
    form = ReplyForm()
    if form.validate_on_submit():
        # need to be logged in
        if not g.username:
            abort(403)
        post_reply(t_id, form.content.data)
        flash("Reply posted.")
    doc = db.subject.find({"_id":t_id})
    replies = list(doc)[0]['reply']
  #  replies = query_db("SELECT * FROM reply WHERE topic_id = ? ORDER BY time",
  #          [topic_id])
    return render_template("topic.html", subject=subject, replies=replies, t_id=t_id,
                           form=form)

def post_topic(subject, content):
    _id = db.subject.insert({"subject":[subject]})
 #   g.db.execute("INSERT INTO topic (subject) values (?);", [subject])
 #   g.db.commit()
 #   topic_id = query_db("select last_insert_rowid()")[0]["last_insert_rowid()"]
    topic_id = str(_id)
    post_reply(_id, content)
    return topic_id

def post_reply(topic_id, content):
    db.subject.update({"_id":topic_id},{"$push":{"reply":{"content":content,"author":g.username,"ts":timestamp()}}})
 #   g.db.execute("INSERT INTO reply (topic_id, time, content, author) values \
 #           (?, ?, ?, ?);", [topic_id, timestamp(), content, g.username])
 #   g.db.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # check if username/password is correct
        username = form.username.data
        password = form.password.data
        user_rec = list(db.user.find({"username":username}))[0]
        password_hash  = user_rec['password_hash']
#        user = query_db("SELECT password_hash FROM users WHERE username = ?", \
#                [username], one=True)
        if user_rec != None:
            pw_hash = hashpw(password.encode('utf-8'), user_rec["password_hash"].encode('utf-8'))
            if (pw_hash == user_rec["password_hash"]):
                # login and redirect to topics
                session["username"] = username
                flash("Login successful.")
                return redirect("/")
        # flash an error
        flash("Invalid username or password.")
    return render_template("login.html", form=form)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop("username", None)
    g.username = None
    return render_template("template.html", page_name="Logout", 
            page_body="You have been logged out.")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # create account
        username = form.username.data
        password = form.password1.data
        pw_hash = hashpw(password.encode('utf-8'), gensalt())
        db.user.insert({"username":username,"password_hash":pw_hash})
   #     g.db.execute("INSERT INTO users (username, password_hash) \
   #             values (?, ?)", [username, pw_hash])
   #     g.db.commit()
        # redirect to login
        flash("Account created. Login to continue.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['datetimeelapsedformat'] = format_elapsed_datetime

if __name__ == '__main__':
    db_closed = 1
    print app
    app.run(debug=True, host="0.0.0.0")

