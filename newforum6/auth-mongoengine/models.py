#  18/Oct/2015 14:21
#   mlb
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
#  newforum6
import datetime
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import ListField
from mongoengine import ReferenceField
from mongoengine import StringField
from mongoengine import FileField
from mongoengine import ImageField
from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import IntField
#from flask_mongoengine import TextAreaField
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash

# from app import db
# Define mongoengine documents
class UserDT(EmbeddedDocument):
    email = StringField(required=True, max_length=100)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    org = StringField(max_length=255)

class Address_ETC(EmbeddedDocument):
    street_addr = StringField(max_length=50)
    city = StringField(max_length=50)
    state = StringField(max_length=50)
    zip = StringField(max_length=10)
    phone = StringField(max_length=13)
    contact = EmbeddedDocumentField(UserDT)

class Organization(Document):
    org_name = StringField(max_length=100)
    date_created =  DateTimeField(default=datetime.now,required=True)

    location = EmbeddedDocumentField(Address_ETC)


class User(Document):


    email = StringField(required=True, max_length=100)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

    pw_hash = StringField(required=True, max_length=100)
    is_active = BooleanField(required=True,default=True)
    is_superuser = BooleanField(default=False)
    roles = ListField(StringField(max_length=50))
    last_login = DateTimeField()
    org = StringField(required=True,max_length=255)
    date_created =  DateTimeField(default=datetime.now,required=True)
    pw_checked =  BooleanField()






    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        if "admin" in self.roles:
            return True
        else:
            return False

    def is_staff(self):
        if "staff" in self.roles:
            return True
        else:
            return False
    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

#    @staticmethod
    def generate_hash(self,password):
        #return generate_password_hash(password, method='pbkdf2:sha1', salt_length=8)
        self.pw_hash = generate_password_hash(password, method='pbkdf2:sha1', salt_length=8)
    # Required for administrative interface
    def __unicode__(self):
        return self.last_name

class Message(Document):
    __tablename__ = "messages"

    addr = StringField(max_length=150)
    subject = StringField(max_length=150)
    message =  StringField(max_length=10000)
    date_created =  DateTimeField(default=datetime.now,required=True)
        # the user who wrote the message
    user_from = EmbeddedDocumentField(UserDT)
        # the user who receives the message
    user = EmbeddedDocumentField(UserDT)

class Registration(Document):
    #__tablename__ = "registrations"

    reg_type = StringField(max_length=10)
    org = StringField(max_length=30)
    message =  StringField(max_length=10000)
    date_created =  DateTimeField(default=datetime.now,required=True)
        # the person registering
    user_from = EmbeddedDocumentField(UserDT)
        # the user who registers

class Post(EmbeddedDocument):
    title = StringField(max_length=60)
    created = DateTimeField(default=datetime.now,required=True)
    creator = EmbeddedDocumentField(UserDT)
    body = StringField(max_length=10000)



class PostArrayEl(EmbeddedDocument):
    key = StringField(max_length=60)
    post = EmbeddedDocumentField(Post)


class Thread(EmbeddedDocument):
    title = StringField(max_length=60)
    created = DateTimeField(default=datetime.now,required=True)
    creator = EmbeddedDocumentField(UserDT)
    posts = ListField(EmbeddedDocumentField(PostArrayEl))
    def num_posts(self):
	return self.post_set.count()
    def num_replies(self):
	return self.post_set.count() - 1
    def last_post(self):
	if self.post_set.count():
	    return self.post_set.order_by("created")[0]



class ThreadArrayEl(EmbeddedDocument):
    key = StringField(max_length=60)
    thread = EmbeddedDocumentField(Thread)


class Forum(Document):
    title = StringField(max_length=60)
    slug = StringField(max_length=60)
    threads =  ListField(EmbeddedDocumentField(ThreadArrayEl))
    org = StringField(max_length=255)
    created = DateTimeField(default=datetime.now)
    creator = EmbeddedDocumentField(UserDT)

    def num_posts(self):
	return sum([t.num_posts() for t in self.thread_set.all()])
    def last_post(self):
	if self.thread_set.count():
	    last = None
	    for t in self.thread_set.all():
		l = t.last_post()
		if l:
		    if not last: last = l
    def __unicode__(self):
	return self.title
    @property
    def post_type(self):
        return self.__class__.__name__

#===============================================================================
class Note(Document):
    '''
    A generic model for adding simple, arbitrary notes to other models such as
    ``Event`` or ``Occurrence``.
    '''
    note = StringField()
    created = DateTimeField(default=datetime.now)
# 1  below creates a backword link to event or occurance - should not need for mongo
    object_id = IntField(min_value=0)
#   like wise as per 1

    #===========================================================================

    #---------------------------------------------------------------------------
    def __str__(self):
        return self.note
#===============================================================================
class Contact(Document):
    '''
       contact for event details

    '''
    name = StringField()
    created = DateTimeField(default=datetime.now)
    phone = StringField()
    email = StringField()

#===============================================================================
class Orgs():
    choices = []
    def choices_clear(self):
        if len(self.choices) > 0:
            del self.choices[:]
    def add_choices(self,dub):
        self.choices.append(dub)
#===============================================================================
class Choices():
    choices = []
    def choices_clear(self):
        if len(self.choices) > 0:
            del self.choices[:]
    def add_choices(self,dub):
        self.choices.append(dub)
#===============================================================================
#===============================================================================
#@python_2_unicode_compatible
class EventType(Document):
    '''
    Simple ``Event`` classifcation.
    '''
    org = StringField(max_length=40)
    abbr = StringField(max_length=4, unique=False)
    label = StringField(max_length=50)

    #===========================================================================
    #class Meta:
    #    verbose_name = _('event type')
    #    verbose_name_plural = _('event types')

    #---------------------------------------------------------------------------
    def __str__(self):
        return self.label
#===============================================================================
class OccurrenceManager(Document):

    use_for_related_fields = True

    #---------------------------------------------------------------------------
    def daily_occurrences(self, dt=None, event=None):
        '''
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        '''
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )
        )

        return qs.filter(event=event) if event else qs
#===============================================================================
#@python_2_unicode_compatible
class Occurrence(EmbeddedDocument):
    '''
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    '''
    start_time = DateTimeField()
    end_time = DateTimeField()
 
    #===========================================================================
 
    #---------------------------------------------------------------------------
 
    #---------------------------------------------------------------------------
    # @models.permalink
 
    #---------------------------------------------------------------------------
    def __lt__(self, other):
        return self.start_time < other.start_time

    #---------------------------------------------------------------------------
    #@property
 
    #---------------------------------------------------------------------------
    #@property
 #-------------------------------------------------------------------------------

#===============================================================================

class Occurrences(EmbeddedDocument):
    key = StringField(max_length=60)
    occurrence = EmbeddedDocumentField(Occurrence)

#===============================================================================

#@python_2_unicode_compatible
class Event(Document):
    '''
    Container model for general metadata and associated ``Occurrence`` entries.
    '''
    title = StringField(max_length=32)
    description = StringField(max_length=100)
    event_type = EmbeddedDocumentField('EventType')
    notes = EmbeddedDocumentField('Note')
    occurrences = ListField(EmbeddedDocumentField('Occurrences'))
    org = StringField(max_length=255)
    location = StringField(max_length=255)
    contact = EmbeddedDocumentField('Contact')
    #===========================================================================
  
    #---------------------------------------------------------------------------
    def __str__(self):
        return self.title

    #---------------------------------------------------------------------------
    # @models.permalink
    def get_absolute_url(self):
        return ('swingtime-event', [str(self.id)])

    #---------------------------------------------------------------------------
    def add_occurrences(self, start_time, end_time, **rrule_params):
        '''
        Add one or more occurences to the event using a comparable API to
        ``dateutil.rrule``.

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        '''
        occurrences = []

        cnt = 0
        count = rrule_params.get('count')
        until = rrule_params.get('until')
        if not (count or until):
            occurEL = Occurrences()
            print "single occurence"
            occur1 = Occurrence(start_time=start_time, end_time=end_time)
            occurEL.key = "1"
            occurEL.occurrence = occur1
            occurrences.append(occurEL)
        else:
            print "multiple occurrence"
            rrule_params.setdefault('freq', rrule.DAILY)
            delta = end_time - start_time
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                cnt += 1
                occurEL = Occurrences()
                occurEL.key = str(cnt)
                occurEL.occurrence =   Occurrence(start_time=ev, end_time=ev + delta)
                occurrences.append(occurEL)
        return occurrences


    #---------------------------------------------------------------------------
    def upcoming_occurrences(self):
        '''
        Return all occurrences that are set to start on or after the current
        time.
        '''
        return self.occurrence_set.filter(start_time__gte=datetime.now())

    #---------------------------------------------------------------------------
    def next_occurrence(self):
        '''
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        '''
        upcoming = self.upcoming_occurrences()
        return upcoming[0] if upcoming else None

    #---------------------------------------------------------------------------
    def daily_occurrences(self, dt=None):
        '''
        Convenience method wrapping ``Occurrence.objects.daily_occurrences``.
        '''
        return Occurrence.objects.daily_occurrences(dt=dt, event=self)
#===============================================================================

#-------------------------------------------------------------------------------
def create_event(
    title,
    event_type,
    abbr,
    description='',
    start_time=None,
    end_time=None,
    note=None,
    **rrule_params
):
    '''
    Convenience function to create an ``Event``, optionally create an
    ``EventType``, and associated ``Occurrence``s. ``Occurrence`` creation
    rules match those for ``Event.add_occurrences``.

    Returns the newly created ``Event`` instance.

    Parameters

    ``event_type``
        can be either an ``EventType`` object or 2-tuple of ``(abbreviation,label)``,
        from which an ``EventType`` is either created or retrieved.

    ``start_time``
        will default to the current hour if ``None``

    ``end_time``
        will default to ``start_time`` plus swingtime_settings.DEFAULT_OCCURRENCE_DURATION
        hour if ``None``

    ``freq``, ``count``, ``rrule_params``
        follow the ``dateutils`` API (see http://labix.org/python-dateutil)



#    if isinstance(event_type, tuple):
    event_type, created = EventType.objects.get_or_create(
            abbr=event_type[0],
            label=event_type[1]
        )
    '''
    start_time = start_time or datetime.now().replace(
        minute=0,
        second=0,
        microsecond=0
    )

    ev = Event()
    end_time = end_time or (start_time + datetime1.timedelta(hours=+1))
    my_occurrences = ev.add_occurrences(start_time, end_time, **rrule_params)



    event = Event(
        title=title,
        description=description,
        event_type=EventType(abbr,event_type),
        notes = Note(note=note),
        occurrences = my_occurrences
    )
    event.save()
    return event
