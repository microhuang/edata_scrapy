# -*- coding: utf-8 -*-

#from apscheduler.scheduler import Scheduler
from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler
#from apscheduler.schedulers.background import BackgroundScheduler as Scheduler

import apscheduler.events
import datetime
import socket
import fcntl
import struct
import sys
from uuid import uuid4
            

#import pickle
import cloudpickle as pickle
#import dill as pickle  #不能处理six.with_metaclass(ABCMeta)继承的子类
#pickle.settings['recurse'] = True
#import copy_reg#python2
import copyreg
import types

#允许实例绑定方法序列化
def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

#copyreg.pickle(types.MethodType, _pickle_method)

def get_pickling_errors(obj,seen=None):
    if seen == None:
        seen = []
    try:
        state = obj.__getstate__()
    except AttributeError:
        return
    if state == None:
        return
    if isinstance(state,tuple):
        if not isinstance(state[0],dict):
            state=state[1]
        else:
            state=state[0].update(state[1])
    result = {}    
    for i in state:
        try:
            pickle.dumps(state[i],protocol=2)
        except pickle.PicklingError:
            if not state[i] in seen:
                seen.append(state[i])
                result[i]=get_pickling_errors(state[i],seen)
    return result

def lock(opener, job_id=None):
#    print(job_id)
    print('lock()')
    
    #mongo
    #now = datetime.datetime.now() - datetime.timedelta(seconds = 3)
    #lck = opener.find_one({'name': 't'})

    #redis
    lck = opener.hgetall('lockstore')
    if lck and 'update_time' in lck and lck['update_time']:
        lck['update_time'] = datetime.datetime.strptime(lck['update_time'][:19], '%Y-%m-%d %H:%M:%S')

    return lck

def hb(ip, now, opener, job_id=None, **attrs):
#    print(job_id)
    print('heartbeat()')
    attrs['active_ip'] = ip
    attrs['update_time'] = now
    #mongo
    #opener.update({'name': 't'}, {'$set': attrs}, upsert = True)
    #redis
    opener.hmset('lockstore', attrs)
    #print(attrs)
    #print(opener.hgetall('lockstore'))

def le(lock_rec, job_id=None):
#    print(job_id)
    if lock_rec:
#        print('active ip')
        print('active ip', lock_rec)
    else:
         print('lock else')

def err_listener(ev):
    if ev.exception:
        print(sys.exc_info())
                
def get_ip(ifname):
    name = socket.gethostname()
    return socket.gethostbyname(name)

#    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    return socket.inet_ntoa(fcntl.ioctl(
#                            s.fileno(),
#                            0x8915, # SIOCGIFADDR
#                            struct.pack('256s', bytes(ifname[:15],'utf-8'))
#                            )[20:24]
#                        )
         
         
    
#todo: scheduler阻止装饰过的脚本序列化、不能正确序列化
class MutexScheduler(Scheduler):
    def __init__(self, gconfig={}, ** options):
        Scheduler.__init__(self, gconfig, ** options)
        self.ip = get_ip('eth0')
        self.uuid = uuid4().hex
        
    def __getstate__(self):
         return self.__dict__
        
    def start(self):
        super(MutexScheduler, self).start()
        #todo:telnet
#        from twisted.internet import protocol
#        from scrapy.utils.reactor import listen_tcp
#        listen_tcp(123456, "localhost", self)

    def mutex(self, lock=None, heartbeat=None, lock_else=None, 
              unactive_interval=datetime.timedelta(seconds=30), opener=None):
		
        def mutex_func_gen(func, job_id):
            #重要：不要引入外部thread\queue\等数据，降导致序列化错误
            def mtx_func(** options):
                opener=None #todo:xxx
#                print(options)
                if lock:#有锁？
                    lock_rec = lock(opener, job_id)
                    now = datetime.datetime.now()
#                    print(lock_rec)
#                    print(('update_time' in lock_rec and lock_rec['update_time'] and now - lock_rec['update_time'] >= unactive_interval))

                    # execute mutex job when the server is active, or the other server is timeout.
                    if not lock_rec or ('active_ip' in lock_rec and lock_rec['active_ip'] == "self.ip") or ('update_time' in lock_rec and lock_rec['update_time'] and now - lock_rec['update_time'] >= unactive_interval):  
#                        print(3333)
                        if lock_rec:
                            del lock_rec['active_ip']
                            del lock_rec['update_time']

                        if not lock_rec:
                            lock_rec = {}

#                        print(func)
                        lock_attrs = func( ** options )#todo:执行job？
#                        print(lock_attrs)
                        if not lock_attrs:
                            lock_attrs = {}

                        # send heart beat
                        #print(344444)
                        heartbeat("self.ip", now, opener, job_id, ** lock_attrs)#todo:返回值写入lock？
                        return lock_attrs
                    else: 
#                        print(4444)
                        lock_else(lock_rec, job_id)
                else:
                    #print(1111)
                    lock_attrs = func(** options)#todo:执行job？
                    return lock_attrs

            return mtx_func

        self.mtx_func_gen = mutex_func_gen

        def inner(func):
#            self.mtx_func_gen = mutex_func_gen
#            pass
            return func

        return inner

    def _pickle_method(m):
        print(111111)
        pass
    copyreg.pickle(types.FunctionType, _pickle_method)
    
    #job.id
#    @override
    def scheduled_job(self, ** options):
#    def cron_schedule(self, ** options):
        def inner(func):
#            import traceback
#            traceback.print_stack()
            job_id = uuid4().hex #提前生成ID，便于JOB加锁
#            print(job_id)
            if hasattr(self, 'mtx_func_gen'):
#                print(111)
                func = self.mtx_func_gen(func, job_id)

#            print(func)
#            import pickle
#            import cloudpickle as pickle
#            print(func)
##            def _pickle_method(m):
##                print(1111111)
##                return m, ()
##            copyreg.pickle(func, _pickle_method)
#            print(pickle.dumps(func))
#            exit()
            func.job = self.add_job(func, id=job_id, ** options)
#            print(func)
#            print(func.job.id)
            return func
        return inner
    
       
# test
if __name__=='__main__':
    from framework.apscheduler.jsonsqlalchemy import JsonSQLAlchemyJobStore
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.jobstores.memory import MemoryJobStore
    jobstores = {
    'default': MemoryJobStore(),
##    'mongo': MongoDBJobStore(),
#    #'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
#    'mysql': SQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
#    'default': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs'),
    'mysql': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
    }

    sched = MutexScheduler(jobstores=jobstores)
    
    #import pymongo
    #mongo = pymongo.Connection(host = '127.0.0.1', port = 27017)
    #lock_store = mongo['lockstore']['locks']
    
    import redis
    from redis import StrictRedis as Redis
    pool = redis.ConnectionPool(host = '127.0.0.1', port = 6379, db = 0, decode_responses=True)
    lock_store = Redis(connection_pool = pool)

    i = 0

#    @sched.cron_schedule(trigger='cron', second = '*')
    @sched.scheduled_job(trigger='cron', kwargs={"aa":'aa111',"bb":'bb'}, second = '*/1', jobstore='mysql')
    @sched.mutex(lock = lock, heartbeat = hb, lock_else = le, opener=lock_store)
    # 由job向业务传递分片信息
    def job(aa="",bb=""):
        print(aa)
        global i
        i += 1
        print(i)
       
#    import pickle
#    print(job)
#    print(sched.mtx_func_gen())
#    print(pickle.dumps(job))
#    exit()
#    def ff(aa="aa", bb="bb"):
#        print(aa,bb)
#    ff=sched.mutex(lock = lock, heartbeat = hb, lock_else = le, opener=lock_store)
#    print(ff)
#    exit()
    
#    job=sched.scheduled_job(job,trigger='cron', kwargs={"aa":'aa111',"bb":'bb'}, second = '*/1')#todo:
#    print(job.job.id)
    
#    ii = 0 
#    
#    @sched.mutex(lock = lock, heartbeat = hb, lock_else = le, opener=lock_store)
##    @sched.cron_schedule(trigger='cron', second = '*')
#    @sched.scheduled_job(trigger='cron', second = '*/1')
#    # 由job向业务传递分片信息
#    def job2(**attr):
#        global ii
#        ii += 1
#        print(ii)
    
#    job = sched.add_job(func=job, kwargs={"aa":"aa","bb":"bb"}, trigger='cron', second='*/1')

    sched.add_listener(err_listener, apscheduler.events.EVENT_JOB_ERROR)
    
    sched.start()


