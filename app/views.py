#
'''
Copyright [2015] [Marc Bellario]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
#
from flask import Flask, url_for, redirect, render_template, request, session, flash
from app import app
import flask_login as login
from forms import LoginForm,RegistrationForm,EventForm,CreatePostForm,CreateThreadForm,MessageForm,SelectOrgForm
from models import User, Event,Forum,Message,UserDT,Registration
from admin1 import build_choice,build_orgs,build_users
from datetime import datetime
import datetime as datetime1
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import login_user, logout_user, login_required
from .helper import Helper
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_admin import BaseView
from werkzeug.security import check_password_hash,generate_password_hash
GET_POST = ['GET', 'POST']
#BaseView views
class MyBase(BaseView):
    pass
    """docstring for MyBase_BaseView_(self, arg):
        super MyBase_init__()
        self.arg = arg """

@app.route('/')
def index():
    print " begin index "
    if session.get('roles') is not None:
        swt_admin = 'admin' in session['roles']
    else:
        swt_admin = False
    return render_template('index.html', user=login.current_user, swt_admin=swt_admin)

@app.route('/list')
@login_required
def list():
    boards = Forum.objects.all()
    swt_admin = 'admin' in session['roles']
    return render_template('forum/index1.html', boards=boards, swt_admin=swt_admin)

#=========================================================================

#@app.route('/detail/<slug>/<dt>')
@app.route('/detail/<dt>/<id>')
@login_required
def detail(id,dt):
    board = Forum.objects.filter(id = id)
    print board[0].title
    #dt=datetime.now()
    #print " date: %s " % dt
    print dt
    threads = board[0].threads
    if threads:
        print " # threads: %s" % len(threads)
    else:
        print " no threads "
    t_ret,cnt = Helper().find_thread(threads,dt)
    rec_cnt = 0;
    swt_admin = 'admin' in session['roles']
    return render_template('forum/detail1.html', board=board[0], thread=t_ret, key=dt, swt_admin=swt_admin)

@app.route('/board')
def board():
    try:
        board = Forum.objects.filter(org = session['org'])
#        threads = Thread.query.filter(Thread.board_id == board.id)
#                        .order_by(Thread.updated.desc()).all()
        threads = board[0].threads
    except Exception as e:
        print e.args      # arguments stored in .args
        print " id: ", id
        print " - BOARD exception value: ", e
        return redirect(url_for('.home'))

    print "_____\/______"
    if 'username' in session:
        print 'Logged in as %s' % session['username']
    else:
        print ' No username in session '
    swt_admin = 'admin' in session['roles']
    return render_template('forum/board1.html', board=board[0],
                           threads=threads, swt_admin=swt_admin)

@app.route('/<id>/create/', methods=GET_POST)
@login_required
def create_thread(id):
    try:
        board = Forum.objects.filter(id = id)
    except Exception as e:
        print " exception value: ", e
        return redirect(url_for('.index'))
    form = CreateThreadForm()
    if form.validate_on_submit():
        t=Helper().build_thread(form,session['username'])
        te=ThreadArrayEl()
        te.key = str(len(board[0].threads)+1)
        te.thread=t
        try:
            Forum.objects(slug=slug).update_one(push__threads=te)
        except Exception as e:
            print " exception update value: ", e
            return redirect(url_for('.index'))



        return redirect(url_for('.board', slug=slug))

    swt_admin = 'admin' in session['roles']
    return render_template('forum/create_thread1.html', board=board[0],
                           form=form, swt_admin=swt_admin)

@app.route('/<id>/<dt>/create/', methods=GET_POST)
@login_required
def create_post(id,dt):
    try:
        board = Forum.objects.filter(id = id)
    except Exception as e:
        print " exception value: ", e
        return redirect(url_for('.index'))
    threads = board[0].threads

    t_ret, sve_cnt = Helper().find_thread(threads,dt)
    form = CreatePostForm()
    if form.validate_on_submit():
        p=Helper().build_post(form,session['username'])
        pe = PostArrayEl()
        pe.key = str(len(t_ret.posts) + 1)
        pe.post = p
        t_ret.posts.append(pe)
        threads[sve_cnt - 1].thread=t_ret
        try:
            Forum.objects(slug=slug).update_one(set__threads=threads)
        except Exception as e:
            print " exception update value: ", e
            return redirect(url_for('.index'))


        return redirect(url_for('.board', slug=slug))


    swt_admin = 'admin' in session['roles']
    return render_template('forum/create_post1.html', thread=t_ret,
                           form=form, swt_admin=swt_admin)



#==========================================================================
@app.route('/write', methods=['GET', 'POST'])
#@login_required
def write():
    if session.get('roles') is not None:
        swt_admin = 'admin' in session['roles']
    else:
        swt_admin = False

    return render_template('write.html',swt_admin=swt_admin)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/home')
def home():
    s1=datetime.today() + datetime1.timedelta(days=1)
    s2=datetime.today() + datetime1.timedelta(days=2)
    s3=datetime.today() + datetime1.timedelta(days=32)

    print s1
    time_start=s1.strftime("%Y-%m-%d 00:00:00")
    time_end=s2.strftime("%Y-%m-%d 00:00:00")
    time_plus=s3.strftime("%Y-%m-%d 00:00:00")
    start=datetime.strptime(str(time_start),"%Y-%m-%d %H:%M:%S")
    end=datetime.strptime(str(time_end),"%Y-%m-%d %H:%M:%S")
    plus=datetime.strptime(str(time_plus),"%Y-%m-%d %H:%M:%S")

    collection = Event._get_collection()
    events=collection.aggregate(
     # Start with a $match pipeline which can take advantage of an index and limit documents processed
       [{ "$unwind" : "$occurrences" },
       { "$match" : {
         'occurrences.occurrence.start_time':{"$gte": start, "$lt": end}
       }}]
     )
    events_post=collection.aggregate(
     # Start with a $match pipeline which can take advantage of an index and limit documents processed
       [{ "$unwind" : "$occurrences" },
       { "$match" : {
         'occurrences.occurrence.start_time':{"$gte": end, "$lt":plus }
       }},
         { "$sort" : { 'occurrences.occurrence.start_time' : 1 } }
       ]
     )
    print type(events)
    print dir(events)
    print events
    doclist1 = []
    doclist2 = []
    for doc in events:
        doclist1.append(doc)
    for doc in events_post:
        doclist2.append(doc)
    count = len(doclist1)
    flash("This is a demo !!", category='success')
    if session.get('roles') is not None:
        swt_admin = 'admin' in session['roles']
    else:
        swt_admin = False

    return render_template('home1.html',events=doclist1,events_post=doclist2,count=count,ctr=0,swt_admin=swt_admin)

@app.route('/check_passwords/')
def check_passwords():
    users = User.objects.all()
    for user in users:
        if not user.pw_checked:
            user.pw_hash = generate_password_hash(user.pw_hash, method='pbkdf2:sha1', salt_length=8)
            user.pw_checked = True
            user.save()
    return '<li> checked </li>'

@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        login.login_user(user)
        session['org']=user.org
        session['su']=user.is_superuser
        session['email'] = user.email
        session['roles'] = user.roles
#        print session['su']
#===============================================================
        collection = User._get_collection()
        collection.update({"user.first_name":form.username.data}, { '$set': { 'last_login': datetime.now() }})
#===============================================================
#        print session['org']
        flash("Logged in successfully!", category='success')
        return redirect(url_for('index'))
    if session.get('roles') is not None:
        swt_admin = 'admin' in session['roles']
    else:
        swt_admin = False
    return render_template('login.html', title='login', form=form, swt_admin=swt_admin)


@app.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user_from = UserDT()
        user_from.first_name = form.first_name.data
        user_from.last_name = form.last_name.data
        user_from.email = form.email.data
        registration = Registration()
        registration.org = form.org.data
        registration.message = form.message.data
        registration.reg_type = form.reg_type.data
        registration.user_from = user_from

        registration.save()
        flash("Your registration will be reviewed", category='success')
        return redirect(url_for('home'))
    if session.get('roles') is not None:
        swt_admin = 'admin' in session['roles']
    else:
        swt_admin = False

    return render_template('registration.html', form=form, swt_admin=swt_admin)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('index'))
#-------------------------------------------------------------------------------
@app.route('/message_detail/<id>')
def message_detail(id):
#    login.logout_user()
    try:
        message = Message.objects.filter(id = id)
    except Exception as e:
        print " exception value: ", e
        return redirect(url_for('.index'))
    form = MessageForm()
    form.content = message[0].message
    form.name_to = message[0].user.first_name
    form.name_from = message[0].user_from.first_name
    form.subject = message[0].subject
    swt_admin = 'admin' in session['roles']
    return render_template('forum/message_detail.html',form=form, swt_admin=swt_admin)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
@app.route('/message_out/', methods=('GET', 'POST'))
def message_out():
#    login.logout_user()
    org_form = SelectOrgForm(Orgs=build_orgs())
    print build_orgs().choices[0]
    message_form = MessageForm(Choices=build_users(build_orgs().choices[0][1]))
    save_org = build_orgs().choices[0][1]
    if request.method == 'POST':
        if request.form['btn']=="select":
            print "select"
            d_choices = dict(build_orgs().choices)
            print d_choices[org_form.org.data]
            save_org = d_choices[org_form.org.data]
            message_form = MessageForm(Choices=build_users(d_choices[org_form.org.data]))
        else:
            print "send"
            print save_org
            if save_org is None:
                print "None"
            else:
                d2_choices = dict(build_users(save_org).choices)
                print d2_choices[message_form.name_to.data]
            message = Message()
            message.addr = d2_choices[message_form.name_to.data]
            message.subject = str(message_form.subject.data)
            message.message = str(message_form.content.data)
            message.save()
            flash("Message Sent", category='success')
#    message_form = MessageForm()
    swt_admin = 'admin' in session['roles']
    return render_template('forum/org_list.html' ,form=org_form, message_form=message_form,swt_admin=swt_admin)

#-------------------------------------------------------------------------------
@app.route('/message_in/')
def message_in():
#    login.logout_user()
    try:
        messages = Message.objects.filter(addr = session["email"])
    except Exception as e:
        print " exception value: ", e
        return redirect(url_for('.index'))
    swt_admin = 'admin' in session['roles']
    return render_template('forum/message_list.html' ,messages=messages,swt_admin=swt_admin)
#    return redirect(url_for('index'))

#-------------------------------------------------------------------------------

@app.route('/events_add', methods=GET_POST)
def events_add():
#
#    events = Event.objects.all()
    dtstart=datetime.now()
    event_form = forms.EventForm(Choices=build_choice())
    recurrence_form = forms.MultipleOccurrenceForm()
    if request.method == 'POST':
        params=recurrence_form.print_all()
        print "params:"
        print params
        print "title:"
        print event_form.title.data
        print "label:"
        print event_form.label.data
        print "day:"
        s=re.search("value=",str(recurrence_form.day))
        n1=s.end()+1
        time_start =  str(recurrence_form.day)[n1:n1+19]
        print time_start
        print " until:"
        s=re.search("value=",str(recurrence_form.until))
        n2=s.end()+1
        time_end = str(recurrence_form.until)[n2:n2+19]

        print time_end
        evt_choice = build_choice()
        d_choices = dict(evt_choice.choices)
        print d_choices
        evt = create_event(
            event_form.title.data,
            d_choices[event_form.label.data],
            event_form.label.data,
            description=event_form.description.data,
            start_time = datetime.strptime(str(time_start),"%Y-%m-%d %H:%M:%S"),
            end_time = datetime.strptime(str(time_end),"%Y-%m-%d %H:%M:%S"),
            note=event_form.note.data,
            **params
        )

        events = Event.objects.all()
        return render_template('admin/event_list.html' ,events=events)
    recurrence_form.day = datetime.now()
    recurrence_form.until = datetime.now()
    return render_template('admin/add_event.html',dtstart=dtstart,event_form=event_form, recurrence_form=recurrence_form)

#-------------------------------------------------------------------------------
