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
from flask_admin import BaseView, expose
from flask_admin.form import rules
from flask_admin.contrib.mongoengine import ModelView
from flask import session, Flask, redirect, url_for, request, flash,render_template
#
import forms
from flask.ext import wtf
from models import User, Event, Choices, EventType, Organization, Orgs, Forum
from datetime import datetime
# Customized admin views
import pymongo
from pymongo import MongoClient
from .helper import Helper
GET_POST = ['GET', 'POST']

class MessageView(ModelView):
    form_widget_args = {
        'message': {
            'rows': 10,
            'class': 'input-xlarge'
        }
    }

class UserView(ModelView):
  #  list_template='user_index.html'
    column_filters = ['first_name']
    def get_query(self):
       orgv = session['org']
#       print orgv
       if session['su']==True:
           return User.objects.all()
       else:
           return User.objects.filter(org=orgv)

    column_searchable_list = ('last_name','org')
    '''
    def on_model_change(self, form, User, is_created):

        # If the password field isn't blank...
        if len(form.pw_hash.data):
            User.generate_hash(form.pw_hash.data)
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            # model.pw_hash = utils.generate_hash(model.pw_hash)
     '''
class ForumView(ModelView):
    def get_query(self):
       orgv = session['org']
#       print orgv
       if session['su']==True:
           return Forum.objects.all()
       else:
           return Forum.objects.filter(org=orgv)
#
class EventView(ModelView):
    def get_query(self):
       orgv = session['org']
       print orgv
       if session['su']==True:
           return Event.objects.all()
       else:
           return Event.objects.filter(org=orgv)
#
def build_choice():
    event_types = EventType.objects.all()
    choices = Choices()
    choices.choices_clear()
    for event_type in event_types:
        dub = (event_type.abbr,event_type.label)
        choices.add_choices(dub)
#    print choices.choices
    return choices

def build_orgs():
    orgs = Organization.objects.all()
    org_choices = Orgs()
    org_choices.choices_clear()
    i=0
    for org in orgs:
        i += 1
        dub = (str(i),org.org_name)
        org_choices.add_choices(dub)
#    print org_choices.choices
    return org_choices

def build_users(org):
    users = User.objects.filter(org=org)
    user_choices = Choices()
    user_choices.choices_clear()
    i=0
    for user in users:
        i += 1
        dub = (str(i),user.email)
        user_choices.add_choices(dub)
#    print user_choices.choices
    return user_choices
