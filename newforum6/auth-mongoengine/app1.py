from flask import Flask, url_for, redirect, render_template, request
from flask_mongoengine import MongoEngine

from wtforms import form, fields, validators
from flask_admin import BaseView, expose
import flask_admin as admin

import flask_login as login
from flask_admin.contrib.mongoengine import ModelView
from flask_admin import helpers
from datetime import datetime
from models import  Event, Choices
import forms
# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# MongoDB settings
app.config['MONGODB_SETTINGS'] = {'DB': 'test'}
db = MongoEngine()
db.init_app(app)


# Create user model. For simplicity, it will store passwords in plain text.
# Obviously that's not right thing to do in real world application.
class User(db.Document):
    login = db.StringField(max_length=80, unique=True)
    email = db.StringField(max_length=120)
    password = db.StringField(max_length=64)
    confirmed_at = db.DateTimeField(default=datetime.now,required=True)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.login


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return User.objects(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if User.objects(login=self.login.data):
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        print user_id
        return User.objects(id=user_id).first()

# add an event to event collection
#-------------------------------------------------------------------------------
class AddEvent(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('.event'))

    @expose('/', methods=('GET', 'POST'))
    def add_event(self):
        dtstart=datetime.now()
        event_form = forms.EventForm(Choices=build_choice())
        recurrence_form = forms.MultipleOccurrenceForm()
        if event_form.validate_on_submit():
          #  data = form.data
          #  user.set(**data)
          #  event.save()

#==========================================

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

#==========================================

            flash("Your profile has been saved")
        else:
            flash("form did not validate on submit")
        recurrence_form.day = datetime.now()
        recurrence_form.until = datetime.now()
        return self.render('add_event.html',dtstart=dtstart,event_form=event_form, recurrence_form=recurrence_form)
#-------------------------------------------------------------------------------

# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated


# Flask views
@app.route('/')
def index():
    print "begin index"
    # print current_user
    #print login.current_user
    return render_template('index.html', user=login.current_user)


@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        login.login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()

        form.populate_obj(user)
        user.save()

        login.login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize flask-login
    init_login()

    # Create admin
    admin = admin.Admin(app, 'Example: Auth-Mongo', index_view=MyAdminIndexView(),template_mode='bootstrap3',)

    # Add view
    admin.add_view(MyModelView(User))
    admin.add_view(MyModelView(Event))

    #admin.add_view(AddEvent(name='Add Events', endpoint='add_event'))
    # Start app
    app.run(debug=True)
