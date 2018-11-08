# -*- coding: utf-8 -*-

#from apscheduler.scheduler import Scheduler
from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler
#from apscheduler.schedulers.background import BackgroundScheduler as Scheduler
import apscheduler.events
import datetime
import fcntl
import socket
import struct
import sys
	

def lock(opener):
    print('lock()')
    
    #mongo
    #now = datetime.datetime.now() - datetime.timedelta(seconds = 3)
    #lck = opener.find_one({'name': 't'})

    #redis
    lck = opener.hgetall('lockstore')
    if lck and 'update_time' in lck and lck['update_time']:
        lck['update_time'] = datetime.datetime.strptime(lck['update_time'][:19], '%Y-%m-%d %H:%M:%S')

    return lck

def hb(ip, now, opener, **attrs):
    print('heartbeat()')
    attrs['active_ip'] = ip
    attrs['update_time'] = now
    #mongo
    #opener.update({'name': 't'}, {'$set': attrs}, upsert = True)
    #redis
    opener.hmset('lockstore', attrs)
    #print(attrs)
    #print(opener.hgetall('lockstore'))

def le(lock_rec):
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
         
class MutexScheduler(Scheduler):
    def __init__(self, gconfig={}, ** options):
        Scheduler.__init__(self, gconfig, ** options)
        self.ip = get_ip('eth0')
        
    def start(self):
        super(MutexScheduler, self).start()
        #todo:telnet
#        from twisted.internet import protocol
#        from scrapy.utils.reactor import listen_tcp
#        listen_tcp(123456, "localhost", self)

    def mutex(self, lock=None, heartbeat=None, lock_else=None, 
              unactive_interval=datetime.timedelta(seconds=30), opener=None):
		
        def mutex_func_gen(func):
            def mtx_func():
                if lock:
                    lock_rec = lock(opener)
                    now = datetime.datetime.now()

                    # execute mutex job when the server is active, or the other server is timeout.
                    if not lock_rec or ('active_ip' in lock_rec and lock_rec['active_ip'] == self.ip) or ('update_time' in lock_rec and lock_rec['update_time'] and now - lock_rec['update_time'] >= unactive_interval):  
                        #print(3333)
                        if lock_rec:
                            del lock_rec['active_ip']
                            del lock_rec['update_time']

                        if not lock_rec:
                            lock_rec = {}

                        lock_attrs = func( ** lock_rec)
                        if not lock_attrs:
                            lock_attrs = {}

                        # send heart beat
                        #print(344444)
                        heartbeat(self.ip, now, opener, ** lock_attrs)
                    else: 
                        lock_else(lock_rec)
                else:
                    #print(1111)
                    func()

            return mtx_func

        self.mtx_func_gen = mutex_func_gen

        def inner(func):
            return func

        return inner

    def cron_schedule(self, ** options):
        def inner(func):
            if hasattr(self, 'mtx_func_gen'):
                func = self.mtx_func_gen(func)

            func.job = self.add_job(func, ** options) #todo:err
            return func
        return inner
    
       
# test
if __name__=='__main__':
#    from framework.apscheduler.sqlalchemy import JsonSQLAlchemyJobStore
#    jobstores = {
##    'mongo': MongoDBJobStore(),
#    #'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
#    #'mysql': SQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db?charset=utf8&use_unicode=0')
#    'default': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs'),
#    'mysql': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
#    }

    sched = MutexScheduler()
    
    #import pymongo
    #mongo = pymongo.Connection(host = '127.0.0.1', port = 27017)
    #lock_store = mongo['lockstore']['locks']
    
    import redis
    from redis import StrictRedis as Redis
    pool = redis.ConnectionPool(host = '127.0.0.1', port = 6379, decode_responses=True)
    lock_store = Redis(connection_pool = pool)

    i = 0

    @sched.mutex(lock = lock, heartbeat = hb, lock_else = le, opener=lock_store)
    @sched.cron_schedule(trigger='cron', second = '*')
    def job(**attr):
        global i
        i += 1
        print(i)

    sched.add_listener(err_listener, apscheduler.events.EVENT_JOB_ERROR)
    
    sched.start()


