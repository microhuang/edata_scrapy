# -*- coding: utf-8 -*-


#from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler
#from apscheduler.schedulers.background import BackgroundScheduler as Scheduler

import apscheduler.events
import logging
import datetime
import time
import sys
from uuid import uuid4
import random

import socket
import fcntl
import struct
            
#import pickle
#import cloudpickle as pickle #不能处理_thread.lock
import dill as pickle  #不能处理six.with_metaclass(ABCMeta)继承的子类,从dispatch_table确认，dill处理的类型更多
#pickle.settings['recurse'] = True
#import copy_reg#python2
import copyreg
import types
import traceback


def err_listener(ev):
    if ev.exception:
        print(sys.exc_info())
        
#关于锁
#https://www.cnblogs.com/ironPhoenix/p/6048467.html
#https://redis.io/topics/distlock/
        
# 1 加锁成功、 0 失败
# expire 锁超时时间，建议为分布节点时间同步误差略大
def rlo(opener, key=None, owner=None, role=None, expire=3):
    assert role in ("work","standby"), "MutexScheduler.lock参数值错误，role有效值：work、standby！"
    script = "if KEYS[3]=='work' and redis.call('sismember', KEYS[1], KEYS[2])==1 or KEYS[3]=='standby' and redis.call('exists', KEYS[1])==1 then return 0 else redis.call('sadd', KEYS[1], KEYS[2]); redis.call('expire', KEYS[1], ARGV[1]); return 1 end"
    #eval <script> 3 job_id1 scheduler_id standby 300
#    print(99999, job_id, scheduler_id, role)
    result = opener.register_script(script)(keys=[key, owner, role], args=[expire])
#    print(111111111,result,type(result))
    logging.info("role: %s", role)
    return result

# 1 释放成功 0 失败
def rle(opener, key=None, owner=None, role=None):
    assert role in ("work","standby"), "MutexScheduler.le参数值错误，role有效值：work、standby！"
    script = "return redis.call('srem', KEYS[1], KEYS[2])"
    result = opener.register_script(script)(keys=[key, owner], args=[])
    #eval <script> 2 job_id1 scheduler_id standby
#    print(333333333,result)
    return result

def rhb(opener, ip, now, key=None, **attrs):
    pass
    
#def lock(opener, job_id=None, scheduler_id=None, role=None):
##    print(job_id)
#    print('lock()')
#    
#    #mongo
#    #now = datetime.datetime.now() - datetime.timedelta(seconds = 3)
#    #lck = opener.find_one({'name': 't'})
#
#    #redis
#    lck = opener.hgetall('lockstore')
#    if lck and 'update_time' in lck and lck['update_time']:
#        lck['update_time'] = datetime.datetime.strptime(lck['update_time'][:19], '%Y-%m-%d %H:%M:%S')
#
#    return lck
#
#def hb(ip, now, opener, job_id=None, **attrs):
##    print(job_id)
#    print('heartbeat()')
#    attrs['active_ip'] = ip
#    attrs['update_time'] = now
#    #mongo
#    #opener.update({'name': 't'}, {'$set': attrs}, upsert = True)
#    #redis
#    opener.hmset('lockstore', attrs)
#    #print(attrs)
#    #print(opener.hgetall('lockstore'))
#
#
#def le(lock_rec, job_id=None, scheduler_id=None, role=None):
#    #单实例redis锁
#    #set lock_key1 requestid_argv1 EX 30 NX
#    #set lock_key1 requestid_argv1 PX 30000 NX
#    #加锁
#    #eval "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 "lock_key1" "requestid_argv1"
#    #lock_key1存在且==requestid_argv1，删除/释放锁、否则释放失败。
#    #"if redis.call('get', KEYS[1])==ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
##    print(job_id)
#    if lock_rec:
##        print('active ip')
#        print('active ip', lock_rec)
#    else:
#         print('lock else')
                
#def get_ip(ifname):
#    name = socket.gethostname()
#    return socket.gethostbyname(name)
#
##    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
##    return socket.inet_ntoa(fcntl.ioctl(
##                            s.fileno(),
##                            0x8915, # SIOCGIFADDR
##                            struct.pack('256s', bytes(ifname[:15],'utf-8'))
##                            )[20:24]
##                        )

#def get_pickling_errors(obj,seen=None):
#    if seen == None:
#        seen = []
#    try:
#        state = obj.__getstate__()
#    except AttributeError:
#        return
#    if state == None:
#        return
#    if isinstance(state,tuple):
#        if not isinstance(state[0],dict):
#            state=state[1]
#        else:
#            state=state[0].update(state[1])
#    result = {}    
#    for i in state:
#        try:
#            pickle.dumps(state[i],protocol=2)
#        except pickle.PicklingError:
#            if not state[i] in seen:
#                seen.append(state[i])
#                result[i]=get_pickling_errors(state[i],seen)
#    return result

         
def MutexSchedulerProxy(Scheduler):

    #todo: 当前的序列化方案，将code序列化，包括：self.role等数据，导致不恰当的行为？
    class MutexScheduler(Scheduler):
        def __init__(self, role, gconfig={}, ** options):
            assert role in ("work","standby"), "MutexScheduler.__init__参数值错误，role有效值：work、standby！"
            logging.getLogger().setLevel(logging.NOTSET) #todo: xxxx
            logging.info("") #todo: xxxx
            Scheduler.__init__(self, gconfig, ** options)
            self.uuid = uuid4().hex
            self.role = role #work:自己没有持有锁就可以获得锁、standby：任何人没有持有锁才可以获得锁
    #        self.ip = get_ip('eth0')
            self._logger.info("Scheduler: %s, Role: %s", self.uuid,self.role)

    #    def __getstate__(self):
    #         return self.__dict__

    #    #添加telnet协议方便查看运行状态
    #    #@override
    #    def start(self):
    #        super(MutexScheduler, self).start()
    #        #todo:telnet
    ##        from twisted.internet import protocol
    ##        from scrapy.utils.reactor import listen_tcp
    ##        listen_tcp(123456, "localhost", self)

        #todo:执行锁
        #shards人工分片（数据分布不均匀时），否则，size自动分片（数据分布均匀时）
        def mutex_run(self, lock=None, lock_else=None, heartbeat=None,
                  unactive_interval=datetime.timedelta(seconds=30), opener=None, size=100, _shards=((1, 10),(11, 20))):
            def mutex_run_gen(func, job_id):
                def mtx_func(** options):
                    #待处理分片，从1开始
                    shard_id=1
                    shards=set((1,))
                    #记录分片扫描次数
                    shard_inc=1
                    uuid=uuid4().hex
                    while True:
                        #分片已经处理完
                        if not shards:
                            return 0
                        #锁分片：有待处理数据从头抢分片，没有待处理数据任务完成
                        while True:
                            try:
                                if shard_inc>10:
#                                    self._logger.warn("分片循环扫描过多！")
                                    pass
                                #人工分片
                                if _shards and len(shard_id)<=shard_id:
                                    shard_id=1
                                    shard_inc=shard_inc+1
                                #自动分片
                                elif 99999999<shard_id:
#                                    self._logger.warn("自动分片数过多！")
                                    pass
                                if lock(opener, job_id+shard_id+"_run", uuid, "standby", 0):
                                    shards.remove(shard_id)#移除处理的分片
                                    shard_id=shard_id+1#准备下一分片
                                    break
                                else:
                                    shards.add(shard_id)#记录未处理的分片
                                    shard_id=shard_id+1
                            except:
                                #上报错误
#                                self._logger.info("锁异常，未能加锁，请处理： %s", job_id+shard_id+"_run")
                                pass
                            #抢锁过程慢一点，随机暂停减少死锁
                            time.sleep(random.randint(1,100)/1000)
                        #处理人工分片参数
                        if _shards:
                            options.setdefault("shard", _shards[shard_id-1])
                        #处理自动分片参数
                        else:
                            options.setdefault("shard", (shard_id, shard_id*size))
                        #处理分片，干活
                        #必须：1、接收分片参数，2、返回是否有待处理记录数
                        cnt = func(**options) #返回是否有待处理记录数，如果还有待处理数据，则从头扫描
                        #释放锁    未释放的锁，会导致任务空转
                        for i in (1,2,3):
                            #非超时锁，释放失败必须额外处理
                            try:
                                if lock_else(opener, job_id+shard_id+"_run", uuid, "standby"):
                                    break
                            except:
                                #上报错误
    #                            self._logger.info("锁异常，未能释放，请清理： %s", job_id+shard_id+"_run")
                                pass
                            time.sleep(0.001)
                        if cnt>0:
                            #重置分片位置
                            shard_id=1
                            shard_inc=shard_inc+1
                        #暂停一小会
                        time.sleep(1)
            
                return mtx_func
        
            self.mtx_run_gen = mutex_run_gen

            def inner(func):
                return func

            return inner
        
        #调度锁
        def mutex(self, lock=None, lock_else=None, heartbeat=None,
                  unactive_interval=datetime.timedelta(seconds=30), opener=None):

            def mutex_func_gen(func, job_id, uuid, role):
                #重要：不要引入外部thread\queue\等数据，降导致序列化错误
                def mtx_func(** options):
                    if lock:#装配
                        if lock(opener, job_id, uuid, role, unactive_interval): #加锁
                            result = func( ** options )#干活
                            #超时锁，释放失败影响不大
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
                            heartbeat(opener, ip, now, job_id, ** lock_attrs)#todo:返回值写入lock？
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
        #            traceback.print_stack()
                    job_id = uuid4().hex #todo:提前生成ID，便于JOB加锁
                    options['id'] = job_id
        #            options.setdefault("id", "{}.{}".format(func.__module__, func.__name__))
                else:
                    job_id = options['id']
                    
                #todo:处理分片锁
                if hasattr(self, 'mtx_run_gen'):
                    func = self.mtx_run_gen(func, job_id)

                #处理任务锁
                if hasattr(self, 'mtx_func_gen'):
                    func = self.mtx_func_gen(func, job_id, self.uuid, self.role)

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
    #            print(888888,job_id)
                func.job = self.add_job(func, ** options)
    #            print(func)
    #            print(func.job.id)
                return func
            return inner
        
    return MutexScheduler
    
       
# test
if __name__=='__main__':
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    import logging
    from framework.apscheduler.jsonsqlalchemy import JsonSQLAlchemyJobStore
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
    executors = {
#    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(1)
    }
    jobstores = {
#    'default': MemoryJobStore(),
##    'mongo': MongoDBJobStore(),
#    #'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
#    'mysql': SQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
#    'default': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs'),
    'mysql': JsonSQLAlchemyJobStore(url='mysql+mysqlconnector://root:12345678@localhost/scrapy_db',tablename='apscheduler_jobs')
    }

    sched = MutexSchedulerProxy(BlockingScheduler)("standby",jobstores=jobstores,executors=executors)
    
    #import pymongo
    #mongo = pymongo.Connection(host = '127.0.0.1', port = 27017)
    #lock_store = mongo['lockstore']['locks']
    
    import redis
    from redis import StrictRedis as Redis
    pool = redis.ConnectionPool(host = '127.0.0.1', port = 6379, db = 0, decode_responses=True)
    lock_store = Redis(connection_pool = pool)

    i = 0

#    @sched.cron_schedule(trigger='cron', second = '*')
    @sched.scheduled_job(trigger='cron', id="job11111111", replace_existing=True, kwargs={"aa":'lkjadslfkjsaldfkj',"bb":'bb'}, second = '*/1', jobstore='mysql')
#    @sched.mutex(lock = lock, heartbeat = hb, lock_else = le, opener=lock_store)
    @sched.mutex(lock = rlo, heartbeat = rhb, lock_else = rle, opener=lock_store, unactive_interval=30)
#    @sched.mutex_run(lock = rlo, heartbeat = rhb, lock_else = rle, opener=lock_store, unactive_interval=30, size=10, _shards=((1, 10),(11, 20)))
    # 由job向业务传递分片信息
    def job(aa="",bb="",shard=(1,10)):
        #待处理分片，从1开始
        shards=set((1,))
        shard_id=1
        while True:
            #分片已经处理完
            if not shards:
                return 0
            #锁分片
            while True:
                if rlo(lock_store, job_id, shard_id, 0):
                    shards.remove(shard_id)#移除处理的分片
                    shard_id=shard_id+1#准备下一分片
                    break
                else:
                    shards.add(shard_id)#记录未处理的分片
                    shard_id=shard_id+1
            #处理分片，确保分片参数有效覆盖任务数据 -- begin
            #select * from dual where state=0 and id>shard[0] and id<shard[1] order by updated
            items = ({"key":"val1"},{"key":"val2"})
            if items:
                for item in items:
#                    #收到退出信号
#                    if sigle=='exit':
#                        return 1
#                    #收到暂停信号
#                    elif sigle=='pause':
#                        return 2
#                    #收到恢复信号
#                    elif sigle=='resume':
#                        return 3
                    #todo: 干活
                    print(item)
                #通知框架是否有其他分片数据
                #items = select * from dual where state=0 limit 1;
#                return len(items)
            #处理分片，确保通知调度框架分片命中记录数 -- end
                #释放锁
                rle(lock_store, job_id, shard_id)
            else:
                #重置分片位置
                shard_id=1
#                return 0
            #暂停一小会
            time.sleep(10)
       
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


