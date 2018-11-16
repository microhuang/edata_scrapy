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
#import cloudpickle as pickle #不能处理_thread.lock
import dill as pickle  #不能处理six.with_metaclass(ABCMeta)继承的子类,从dispatch_table确认，dill处理的类型更多
#pickle.settings['recurse'] = True
#import copy_reg#python2
import copyreg
import types


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

# 1 加锁成功、 0 失败
# expire 锁超时时间，建议为分布节点时间同步误差略大
def rlo(opener, job_id=None, scheduler_id=None, role=None, expire=3):
    assert role in ("work","standby"), "MutexScheduler.lock参数值错误，role有效值：work、standby！"
    script = "if KEYS[3]=='work' and redis.call('sismember', KEYS[1], KEYS[2])==1 or KEYS[3]=='standby' and redis.call('exists', KEYS[1])==1 then return 0 else redis.call('sadd', KEYS[1], KEYS[2]); redis.call('expire', KEYS[1], ARGV[1]); return 1 end"
    #eval <script> 3 job_id1 scheduler_id standby 300
#    print(99999, job_id, scheduler_id, role)
    result = opener.register_script(script)(keys=[job_id, scheduler_id, role], args=[expire])
#    print(111111111,result,type(result))
    return result

# 1 释放成功 0 失败
def rle(opener, job_id=None, scheduler_id=None, role=None):
    assert role in ("work","standby"), "MutexScheduler.le参数值错误，role有效值：work、standby！"
    script = "return redis.call('srem', KEYS[1], KEYS[2])"
    result = opener.register_script(script)(keys=[job_id, scheduler_id], args=[])
#    print(333333333,result)
    return result
    
def lock(opener, job_id=None, scheduler_id=None, role=None):
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


def le(lock_rec, job_id=None, scheduler_id=None, role=None):
    #单实例redis锁
    #set lock_key1 requestid_argv1 EX 30 NX
    #set lock_key1 requestid_argv1 PX 30000 NX
    #加锁
    #eval "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 "lock_key1" "requestid_argv1"
    #lock_key1存在且==requestid_argv1，删除/释放锁、否则释放失败。
    #"if redis.call('get', KEYS[1])==ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
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
    def __init__(self, role, gconfig={}, ** options):
        assert role in ("work","standby"), "MutexScheduler.__init__参数值错误，role有效值：work、standby！"
        Scheduler.__init__(self, gconfig, ** options)
        self.ip = get_ip('eth0')
        self.uuid = uuid4().hex
        self.role = role #work:自己没有持有锁就可以获得锁、standby：任何人没有持有锁才可以获得锁
        self._logger.info("Scheduler: %s, Role: %s", self.uuid,self.role)
        
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
	
        def mutex_func_gen(func, job_id, ip, uuid, role):
            #重要：不要引入外部thread\queue\等数据，降导致序列化错误
#            opener=None #todo:序列化时，需要确保这里指向空（不引入线程锁）、反序列化时时恢复环境，以便代码执行
            def mtx_func(** options):
                if lock:#装配
                    if lock(opener, job_id, uuid, role, unactive_interval): #加锁
                        result = func( ** options )#干活
                        lock_else(opener, job_id, uuid, role) #释放
                        return result
                else:#不装配
                    result = func(** options)#todo:执行job？
                    return result
            
            def ___mtx_func(** options):
#                print(options)
                if lock:#装配
                    #加锁 todo:以下操作需要原子化
                    lock_rec = lock(opener, job_id)
                    if 'schedulers' not in lock_rec or not lock_rec['schedulers']:
                        lock_rec['schedulers'] = set()
                    now = datetime.datetime.now()
#                    print(lock_rec)
#                    print(('update_time' in lock_rec and lock_rec['update_time'] and now - lock_rec['update_time'] >= unactive_interval))

                    # execute mutex job when the server is active, or the other server is timeout.
                    #role=='work' or 'standby'?
                    #验锁
                    if not lock_rec or (self.role=='work' and self.uuid not in lock_rec['schedulers']) or ('active_ip' in lock_rec and lock_rec['active_ip'] == ip) or ('update_time' in lock_rec and lock_rec['update_time'] and now - lock_rec['update_time'] >= unactive_interval):  
                        #通过
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
                        if 'schedulers' not in lock_attrs or not lock_attrs['schedulers']:
                            lock_attrs['schedulers'] = set()
                        lock_attrs['schedulers'].add(self.uuid) #持锁人
                        #更新
                        heartbeat(ip, now, opener, job_id, ** lock_attrs)#todo:返回值写入lock？
                        return lock_attrs
                    else: 
                        #未通过
                        #释放 todo：存在释放他人所拥有锁的风险
#                        print(4444)
                        lock_else(lock_rec, job_id)
                else:#不装配
                    #print(1111)
                    lock_attrs = func(** options)#todo:执行job？
                    return lock_attrs
        
#            def _pickle_method(obj):
##                print(3233)
##                print(33333,obj)
##                exit()
##                pass
#                return _thread.LockType, ()
#            def _unpickle_method(func_name, obj, cls):
#                print(777777777)
#                return object
#                
##            print(55555)
#            import _thread
#            copyreg.pickle(_thread.LockType, _pickle_method, constructor_ob=_unpickle_method)#constructor_ob注册无效？
#            copyreg.constructor(_unpickle_method)#constructor注册无效？

            return mtx_func

        self.mtx_func_gen = mutex_func_gen

        def inner(func):
#            self.mtx_func_gen = mutex_func_gen
#            pass
            return func

        return inner
    
    #job.id
#    @override
    def scheduled_job(self, ** options):
#    def cron_schedule(self, ** options):
        def inner(func):
            if "id" not in options:
    #            import traceback
    #            traceback.print_stack()
                job_id = uuid4().hex #todo:提前生成ID，便于JOB加锁
                options['id'] = job_id
    #            options.setdefault("id", "{}.{}".format(func.__module__, func.__name__))
            else:
                job_id = options['id']
                
#            print(job_id)
            if hasattr(self, 'mtx_func_gen'):
#                print(111)
                func = self.mtx_func_gen(func, job_id, self.ip, self.uuid, self.role)

#            print(func)
#            import pickle
#            import cloudpickle as pickle
#            print(func)
#            print(type(func))
#            print(func is types.BuiltinMethodType)
##            def _pickle_method(m):
##                print(1111111)
##                return m, ()
##            copyreg.pickle(types.MethodType, _pickle_method)
#            print(66666)
#            sss=pickle.dumps(func)
#            print(77777,pickle.loads(sss))
#            exit()
            print(888888,job_id)
            func.job = self.add_job(func, ** options)
#            print(func)
#            print(func.job.id)
            return func
        return inner
    
       
# test
if __name__=='__main__':
    from framework.apscheduler.jsonsqlalchemy import JsonSQLAlchemyJobStore
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
    executors = {
#    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(1)
    }
    jobstores = {
    'default': MemoryJobStore(),
##    'mongo': MongoDBJobStore(),
#    #'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
#    'mysql': SQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
#    'default': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs'),
    'mysql': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
    }

    sched = MutexScheduler("work",jobstores=jobstores,executors=executors)
    
    #import pymongo
    #mongo = pymongo.Connection(host = '127.0.0.1', port = 27017)
    #lock_store = mongo['lockstore']['locks']
    
    import redis
    from redis import StrictRedis as Redis
    pool = redis.ConnectionPool(host = '127.0.0.1', port = 6379, db = 0, decode_responses=True)
    lock_store = Redis(connection_pool = pool)

    i = 0

#    @sched.cron_schedule(trigger='cron', second = '*')
#    @sched.scheduled_job(trigger='cron', id="job1111", kwargs={"aa":'lkjadslfkjsaldfkj',"bb":'bb'}, second = '*/1', jobstore='default')
#    @sched.mutex(lock = lock, heartbeat = hb, lock_else = le, opener=lock_store)
#    @sched.mutex(lock = rlo, heartbeat = hb, lock_else = rle, opener=lock_store, unactive_interval=30)
    # 由job向业务传递分片信息
    def job(aa="",bb=""):
        import time
        print(time.time(), aa)
        global i
        i += 1
        print(i)
        time.sleep(5)
       
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


