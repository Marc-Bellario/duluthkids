#helper.py
from .models import Post,Thread,UserDT
class Helper(object):
    def find_thread(self,threads,key):
        rec_cnt = 0
        t_ret = Thread()
        for t in threads:
            rec_cnt += 1
            if t.key == key:
                t_ret = t.thread
                break
        return t_ret,rec_cnt
#
    def find_post(self,posts,key):
        rec_cnt = 0
        p_ret = Post     
        for p in posts:
            rec_cnt += 1
            if p.key == key:
                p_ret = p.post
                break
        return p_ret
#
    def build_thread(self,form,user):
        print 'after validate'
        print 'Logged in as %s' % user
        u = UserDT()
        u.first_name = user
        u.last_name = "b"
        u.email =  user + "@here.com"
     #   p = Post(body=form.content.data, creator=session['username'])
        p = Post()
        p.title = "thread description"
        p.body = form.content.data
        p.creator = u
        print ' post - post build '
        pe = PostArrayEl()
        pe.key="1"
        pe.post=p
        t = Thread()
        t.title = form.name.data
        t.creator = u
        t.posts.append(pe)
        print ' thread - post build '
        t.postcnt=1
        return t
#
    def build_post(self,form,user):
        u = UserDT()
        u.first_name = user
        u.last_name = "b"
        u.email =  user + "@here.com"
        p = Post()
        p.title = form.title.data
        p.body = form.content.data
        p.creator = u
        print ' post - post build '
        return p

#
    def build_occurrence(self,key,form,occurrence):
        print 'build_occurence'
        print 'Event key %s' % key
        rec_cnt=0
        for o in occurrence:
            rec_cnt += 1
            if o.key == key:
                o_ret = o.occurrence
                break
        form.start_time = o_ret.start_time
        form.end_time = o_ret.end_time

        return form
#
    def find_occurrence(self,key,occurrence):
        rec_cnt=0
        for o in occurrence:
            rec_cnt += 1
            if o.key == key:
                o_ret = o.occurrence
                break
        return rec_cnt    

    def time_delta_total_seconds(self,time_delta):
        '''
        Calculate the total number of seconds represented by a 
        ``datetime.timedelta`` object
    
        '''
        return time_delta.days * 3600 + time_delta.seconds