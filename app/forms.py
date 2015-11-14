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

from flask.ext.wtf import Form
from wtforms import  form, fields, validators, BooleanField, IntegerField, TextField, PasswordField, TextAreaField, SubmitField,RadioField, SelectField, SelectMultipleField
from wtforms.validators import Required
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms import widgets
from dateutil import rrule
from datetime import datetime
from datetime import time
import datetime as datetime1
from .helper import Helper
from .models import Choices,Orgs
from models import User
import flask_login as login
from werkzeug.security import check_password_hash,generate_password_hash
WEEKDAY_SHORT = [
    (7, '__Sun'),
    (1, '__Mon'),
    (2, '__Tue'),
    (3, '__Wed'),
    (4, '__Thu'),
    (5, '__Fri'),
    (6, '__Sat')
]

WEEKDAY_LONG = [
    (7, 'Sunday'),
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday')
]

MONTH_LONG = [
    (1,  'January'),
    (2,  'February'),
    (3,  'March'),
    (4,  'April'),
    (5,  'May'),
    (6,  'June'),
    (7,  'July'),
    (8,  'August'),
    (9,  'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
]

MONTH_SHORT = [
    (1,  '__Jan'),
    (2,  '__Feb'),
    (3,  '__Mar'),
    (4,  '__Apr'),
    (5,  '__May'),
    (6,  '__Jun'),
    (7,  '__Jul'),
    (8,  '__Aug'),
    (9,  '__Sep'),
    (10, '__Oct'),
    (11, '__Nov'),
    (12, '__Dec'),
]


ORDINAL = [
    (1,  'first'),
    (2,  'second'),
    (3,  'third'),
    (4,  'fourth'),
    (-1, 'last')
]

REGISTRATION_TYPE = [
    ('info',  'send information'),
    ('reg org',  'register organization')
]

FREQUENCY_CHOICES = [
    (rrule.DAILY,   'Day(s)'),
    (rrule.WEEKLY,  'Week(s)'),
    (rrule.MONTHLY, 'Month(s)'),
    (rrule.YEARLY,  'Year(s)'),
]

REPEAT_CHOICES = [
    ('count', 'By count'),
    ('until', 'Until date'),
]

ROLES = [
    ('1', 'su'),
    ('2', '___admin____'),
    ('3', '___staff____'),
    ('4', '___parent____'),
    ('5', '___user____'),
]

ISO_WEEKDAYS_MAP = (
    None,
    rrule.MO,
    rrule.TU,
    rrule.WE,
    rrule.TH,
    rrule.FR,
    rrule.SA,
    rrule.SU
)

TIMESLOT_INTERVAL = datetime1.timedelta(minutes=15)
DEFAULT_OCCURRENCE_DURATION = datetime1.timedelta(hours=+1)
MINUTES_INTERVAL = TIMESLOT_INTERVAL.seconds // 60
SECONDS_INTERVAL = Helper().time_delta_total_seconds(DEFAULT_OCCURRENCE_DURATION)
#-------------------------------------------------------------------------------
class SelectOrgForm(Form,Orgs):
    org =  SelectField(choices=Orgs.choices)
#-------------------------------------------------------------------------------
class MessageForm(Form,Choices):
#
    name_to = SelectField(choices=Choices.choices)
    name_from = TextAreaField(validators=[Required()])
    subject = TextAreaField(validators=[Required()])
    content = TextAreaField(validators=[Required()])
    send_message = SubmitField()
#
#-------------------------------------------------------------------------------
class CreateThreadForm(Form):
    name = TextAreaField(validators=[Required()])
    content = TextAreaField(validators=[Required()])
    submit = SubmitField()
#-------------------------------------------------------------------------------
class CreatePostForm(Form):
    title = TextAreaField(validators=[Required()])
    content = TextAreaField(validators=[Required()])
    submit = SubmitField()
#===============================================================================
# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    username = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')
        if user.pw_checked:
            if check_password_hash(pw_hash, self.password.data):
                raise validators.ValidationError('Invalid password')
        else:
            if user.pw_hash != self.password.data:
                raise validators.ValidationError('Invalid password')

    def get_user(self):
        return User.objects(last_name=self.username.data).first()


class RegistrationForm(form.Form):
    org = fields.TextField()
    reg_type = fields.SelectField(choices=REGISTRATION_TYPE)
    message = fields.TextAreaField()
    first_name = fields.TextField()
    last_name = fields.TextField()
    email = fields.TextField(validators=[validators.required()])

#===============================================================================
class EventForm(Form,Choices):
    '''
    A simple form for adding and updating Event attributes

    '''
    title = TextAreaField(validators=[Required()])
    description = TextAreaField(validators=[Required()])
 #
    note = TextAreaField()

    label =  SelectField(choices=Choices.choices)
#===========================================================================
class OccurenceForm(Form):
#
    start_time = DateTimeField(validators=[Required()])
    end_time = DateTimeField(validators=[Required()])
#===============================================================================
class MultipleOccurrenceForm(Form):
    day = DateTimeField(default=datetime.now())
    '''
        label=_('Date'),
        initial=date.today,
        widget=SelectDateWidget()
    )

    start_time_delta = forms.IntegerField(
        label=_('Start time'),
        widget=forms.Select(choices=default_timeslot_offset_options)
    )

    end_time_delta = forms.IntegerField(
        label=_('End time'),
        widget=forms.Select(choices=default_timeslot_offset_options)
    )
    # recurrence options
    repeats = forms.ChoiceField(
        choices=REPEAT_CHOICES,
        initial='count',
        label=_('Occurrences'),
        widget=forms.RadioSelect()
    )
    '''
    # recurrence options

    repeats = RadioField(
        'Occurrences',
        [validators.Required()],
        choices=REPEAT_CHOICES, default='count'
    )
    count = IntegerField('Total Occurrences',default=1)

    until = DateTimeField(default=datetime.now())

    freq = RadioField(
        'Frequency',
        default=rrule.WEEKLY,
        choices=FREQUENCY_CHOICES
    )

    interval = IntegerField(default=1)

    # weekly options
    week_days = SelectMultipleField(
        'Weekly options',
        choices=WEEKDAY_SHORT,
        widget=widgets.ListWidget(prefix_label=True),
        option_widget=widgets.CheckboxInput()
    )

    # monthly  options

    month_option = RadioField(
        'Monthly options',
        default='each',
        choices=[('on','On the'), ('each','Each:')]
    )

#

#
    month_ordinal_day =  SelectField(choices=WEEKDAY_LONG)
    each_month_day = SelectMultipleField(
        choices=[(i,"__"+str(i)) for i in range(1,32)],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )

    # yearly options
    year_months = SelectMultipleField(
        'Yearly options',
        choices=MONTH_SHORT,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )

    is_year_month_ordinal = BooleanField()

    year_month_ordinal =  SelectField(choices=ORDINAL)
    year_month_ordinal_day =  SelectField(choices=WEEKDAY_LONG)
    #---------------------------------------------------------------------------
    def __init__(self, *args, **kws):
        super(MultipleOccurrenceForm, self).__init__(*args, **kws)
        dtstart=datetime.now()
        if dtstart:
            dtstart = dtstart.replace(
                minute=((dtstart.minute // MINUTES_INTERVAL) * MINUTES_INTERVAL),
                second=0,
                microsecond=0
            )

            weekday = dtstart.isoweekday()
            ordinal = dtstart.day // 7
            ordinal = '%d' % (-1 if ordinal > 3 else ordinal + 1,)
            offset = (dtstart - datetime.combine(dtstart.date(), time(0))).seconds
            '''
            self.initial.setdefault('day', dtstart)
            self.initial.setdefault('week_days', '%d' % weekday)
            self.initial.setdefault('month_ordinal', ordinal)
            self.initial.setdefault('month_ordinal_day', '%d' % weekday)
            self.initial.setdefault('each_month_day', ['%d' % dtstart.day])
            self.initial.setdefault('year_months', ['%d' % dtstart.month])
            self.initial.setdefault('year_month_ordinal', ordinal)
            self.initial.setdefault('year_month_ordinal_day', '%d' % weekday)
            self.initial.setdefault('start_time_delta', '%d' % offset)
            self.initial.setdefault('end_time_delta', '%d' % (offset + SECONDS_INTERVAL,))
            '''
    #---------------------------------------------------------------------------

    def print_all(self):
        if self.day:
            print "day"
            print self.day
            print self.day.data
        else:
            print "None"

        if self.repeats:
            print "repeats"
            print self.repeats.data
        else:
            print "None"

        if self.count:
            print "count"
            print self.count.data
        else:
            print "None"

        if self.until:
            print "until"
            print self.until
            print self.until.data
        else:
            print "None"

        if self.freq:
            print "freq"
            print self.freq.data
        else:
            print "None"

        if self.interval:
            print "interval"
            print self.interval.data
        else:
            print "None"

        if self.week_days:
            print "week_days"
            print self.week_days.data
        else:
            print "None"

        if self.month_option:
            print "month_option"
            print self.month_option.data
        else:
            print "None"

        if self.month_ordinal:
            print "month_ordinal"
            print self.month_ordinal.data
        else:
            print "None"

        if self.month_ordinal_day:
            print "month_ordinal_day"
            print self.month_ordinal_day.data
        else:
            print "None"

        if self.each_month_day:
            print "each_month_day"
            print self.each_month_day.data
        else:
            print "None"

        if self.year_months:
            print "year_months"
            print self.year_months.data
        else:
            print "None"

        if self.is_year_month_ordinal:
            print "is_year_month_ordinal"
            print self.is_year_month_ordinal.data
        else:
            print "None"

        if self.year_month_ordinal:
            print "year_month_ordinal"
            print self.year_month_ordinal.data
        else:
            print "None"

        if self.year_month_ordinal_day:
            print "year_month_ordinal_day"
            print self.year_month_ordinal_day.data
        else:
            print "None"


        params = self.build_rrule_params()
        print params
        return params

    #---------------------------------------------------------------------------
    def clean(self):
        day = datetime.combine(self.cleaned_data['day'], time(0))
        self.cleaned_data['start_time'] = day + timedelta(
            seconds=self.cleaned_data['start_time_delta']
        )

        self.cleaned_data['end_time'] = day + timedelta(
            seconds=self.cleaned_data['end_time_delta']
        )

        return self.cleaned_data

    #---------------------------------------------------------------------------
    def save(self, event):
        if self.cleaned_data['repeats'] == 'count' and self.cleaned_data['count'] == 1:
            params = {}
        else:
            params = self._build_rrule_params()

        event.add_occurrences(
            self.cleaned_data['start_time'],
            self.cleaned_data['end_time'],
            **params
        )

        return event

    #---------------------------------------------------------------------------
    def build_rrule_params(self):
        iso = ISO_WEEKDAYS_MAP
   #     data = self.cleaned_data
        params = dict(
            freq=int(self.freq.data),
            interval=int(self.interval.data) or 1
        )

        if self.repeats.data == 'until':
            params['until'] = self.until.data
        else:
            params['count'] = self.count.data

        if params['freq'] == rrule.WEEKLY:
            v=[]
            for x in self.week_days.data:
                y=int(x)
                v.append(y)
            params['byweekday'] = [iso[n] for n in v]

        elif params['freq'] == rrule.MONTHLY:
            if 'on' == self.month_option.data:
                ordinal = self.month_ordinal.data
                day = iso[self.month_ordinal_day.data]
                params.update(byweekday=day, bysetpos=ordinal)
            else:
                params['bymonthday'] = self.each_month_day.data

        elif params['freq'] == rrule.YEARLY:
            params['bymonth'] = self.year_months.data
            if self.is_year_month_ordinal.data:
                ordinal = self.year_month_ordinal.data
                day = iso[self.year_month_ordinal_day.data]
                params['byweekday'] = day(ordinal)

        elif params['freq'] != rrule.DAILY:
            raise NotImplementedError(('Unknown interval rule ' + params['freq']))

        return params
