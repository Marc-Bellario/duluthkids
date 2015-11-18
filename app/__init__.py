#
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
import os
from flask import Flask, session
import flask_login as login
import flask_admin as admin
from flask_mongoengine import MongoEngine
from flask.ext.admin.contrib.mongoengine.view import ModelView
from models import *
from admin1 import *
import base64
# Create application
app = Flask(__name__)
#print str(os.environ['MONGOLAB_URI'])
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '\xc5\xcc\x8c\xa1\xe7\x05{\x16\xd2\x80r\xcc~\x85\xb6u2\xf2gL\xe9f\xee\x14'
#app.config['MONGODB_SETTINGS'] = {'DB': 'newforum6'}
if 'MONGOLAB_URI' in os.environ:
    connection_string = str(os.environ['MONGOLAB_URI'])
    print connection_string
if 'MONGOLAB_URI' in os.environ:
    dbname_string = str(os.environ['MONOGO_LAB_DBNAME'])
    print dbname_string
app.config['MONGODB_SETTINGS'] = {'DB': dbname_string, "host":connection_string}
# Create models
try:
    db = MongoEngine()
    db.init_app(app)
except Exception as e:
        print app
        print e.args      # arguments stored in .args
        print " - init exception value: ", e
#        return redirect(url_for('.home'))
# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.objects(id=user_id).first()

init_login()
import views
    # Create admin

# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

class MySUModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_superuser

# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
#    @expose('/')
    def is_accessible(self):
        return login.current_user.is_admin()




    # Add views
    # Create admin
#
admin = admin.Admin(app, 'DuluthKids: Admin', index_view=MyAdminIndexView(),template_mode='bootstrap3')
#
    # Add view
admin.add_view(ForumView(Forum))
admin.add_view(MessageView(Message))
admin.add_view(MySUModelView(Registration))
admin.add_view(MySUModelView(Organization))
admin.add_view(UserView(User,name='USERS'))
admin.add_view(SUUserView(User,name='SUUSERS',endpoint='duplicate_view'))
admin.add_view(MyModelView(EventType,name='Event Types'))
admin.add_view(EventView(Event))
