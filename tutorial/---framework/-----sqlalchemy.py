# -*- coding: utf-8 -*-

from __future__ import absolute_import

from apscheduler.jobstores.base import BaseJobStore, JobLookupError, ConflictingIdError
from apscheduler.util import maybe_ref, datetime_to_utc_timestamp, utc_timestamp_to_datetime
from apscheduler.job import Job

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle
    
import json

try:
    from sqlalchemy import (
        create_engine, Table, Column, MetaData, Unicode, Float, LargeBinary, String, select)
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.expression import null
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')


from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

class JsonSQLAlchemyJobStore(SQLAlchemyJobStore):
    def __init__(self, url=None, engine=None, tablename='apscheduler_jobs', metadata=None,
                 pickle_protocol=pickle.HIGHEST_PROTOCOL, tableschema=None, engine_options=None, use_json=None):
        super(JsonSQLAlchemyJobStore, self).__init__(url, engine, tablename, metadata,
                 pickle_protocol, tableschema, engine_options)
                 
        self.use_json = use_json
        self.pickle_protocol = pickle_protocol
        metadata = maybe_ref(metadata) or MetaData()

        if engine:
            self.engine = maybe_ref(engine)
        elif url:
            self.engine = create_engine(url, **(engine_options or {}))
        else:
            raise ValueError('Need either "engine" or "url" defined')

        # 191 = max key length in MySQL for InnoDB/utf8mb4 tables,
        # 25 = precision that translates to an 8-byte float
        self.jobs_t = Table(
            tablename, metadata,
            Column('id', Unicode(191, _warn_on_bytestring=False), primary_key=True),
            Column('next_run_time', Float(25), index=True),
            Column('job_state', LargeBinary, nullable=False),
            Column('job_json', String(512), nullable=False),
            schema=tableschema
        )
        
    def start(self, scheduler, alias):
        super(JsonSQLAlchemyJobStore, self).start(scheduler, alias)
        self.jobs_t.create(self.engine, True)
    
    def add_job(self, job):
        #print(json.dumps(job.__getstate__(), cls=JobEncoder))
        insert = self.jobs_t.insert().values(**{
            'id': job.id,
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol),
            'job_json': json.dumps(job.__getstate__(), cls=JobEncoder)
        })
        try:
            self.engine.execute(insert)
        except IntegrityError:
            raise ConflictingIdError(job.id)

    def update_job(self, job):
        update = self.jobs_t.update().values(**{
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol),
            'job_json': json.dumps(job.__getstate__(), cls=JobEncoder)
        }).where(self.jobs_t.c.id == job.id)
        result = self.engine.execute(update)
        if result.rowcount == 0:
            raise JobLookupError(id)
        
    def _reconstitute_job(self, job_state, job_json):
        #print("_______")
        if self.use_json==True:
            job_state = json.loads(job_json,cls=JobDecoder)
        else:
            job_state = pickle.loads(job_state)
        #print(job_state)
        #print(json.loads(job_json,cls=JobDecoder))
        #print("--------")
        job_state['jobstore'] = self
        job = Job.__new__(Job)
        job.__setstate__(job_state)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        return job
    
    def _get_jobs(self, *conditions):
        jobs = []
        selectable = select([self.jobs_t.c.id, self.jobs_t.c.job_state, self.jobs_t.c.job_json]).\
            order_by(self.jobs_t.c.next_run_time)
        selectable = selectable.where(*conditions) if conditions else selectable
        failed_job_ids = set()
        for row in self.engine.execute(selectable):
            try:
                jobs.append(self._reconstitute_job(row.job_state, row.job_json))
            except BaseException:
                self._logger.exception('Unable to restore job "%s" -- removing it', row.id)
                failed_job_ids.add(row.id)

        # Remove all the jobs we failed to restore
        if failed_job_ids:
            delete = self.jobs_t.delete().where(self.jobs_t.c.id.in_(failed_job_ids))
            self.engine.execute(delete)

        return jobs
    
    
class SQLAlchemyJobStore(BaseJobStore):
    """
    Stores jobs in a database table using SQLAlchemy.
    The table will be created if it doesn't exist in the database.
    Plugin alias: ``sqlalchemy``
    :param str url: connection string (see
        :ref:`SQLAlchemy documentation <sqlalchemy:database_urls>` on this)
    :param engine: an SQLAlchemy :class:`~sqlalchemy.engine.Engine` to use instead of creating a
        new one based on ``url``
    :param str tablename: name of the table to store jobs in
    :param metadata: a :class:`~sqlalchemy.schema.MetaData` instance to use instead of creating a
        new one
    :param int pickle_protocol: pickle protocol level to use (for serialization), defaults to the
        highest available
    :param str tableschema: name of the (existing) schema in the target database where the table
        should be
    :param dict engine_options: keyword arguments to :func:`~sqlalchemy.create_engine`
        (ignored if ``engine`` is given)
    """

    def __init__(self, url=None, engine=None, tablename='apscheduler_jobs', metadata=None,
                 pickle_protocol=pickle.HIGHEST_PROTOCOL, tableschema=None, engine_options=None):
        super(SQLAlchemyJobStore, self).__init__()
        self.pickle_protocol = pickle_protocol
        metadata = maybe_ref(metadata) or MetaData()

        if engine:
            self.engine = maybe_ref(engine)
        elif url:
            self.engine = create_engine(url, **(engine_options or {}))
        else:
            raise ValueError('Need either "engine" or "url" defined')

        # 191 = max key length in MySQL for InnoDB/utf8mb4 tables,
        # 25 = precision that translates to an 8-byte float
        self.jobs_t = Table(
            tablename, metadata,
            Column('id', Unicode(191, _warn_on_bytestring=False), primary_key=True),
            Column('next_run_time', Float(25), index=True),
            Column('job_state', LargeBinary, nullable=False),
            Column('job_json', String(512), nullable=False),
            schema=tableschema
        )

    def start(self, scheduler, alias):
        super(SQLAlchemyJobStore, self).start(scheduler, alias)
        self.jobs_t.create(self.engine, True)

    def lookup_job(self, job_id):
        selectable = select([self.jobs_t.c.job_state,self.jobs_t.c.job_json]).where(self.jobs_t.c.id == job_id)
        job_state,job_json = self.engine.execute(selectable).scalar()
        return self._reconstitute_job(job_state,job_json) if job_state else None

    def get_due_jobs(self, now):
        timestamp = datetime_to_utc_timestamp(now)
        return self._get_jobs(self.jobs_t.c.next_run_time <= timestamp)

    def get_next_run_time(self):
        selectable = select([self.jobs_t.c.next_run_time]).\
            where(self.jobs_t.c.next_run_time != null()).\
            order_by(self.jobs_t.c.next_run_time).limit(1)
        next_run_time = self.engine.execute(selectable).scalar()
        return utc_timestamp_to_datetime(next_run_time)

    def get_all_jobs(self):
        jobs = self._get_jobs()
        self._fix_paused_jobs_sorting(jobs)
        return jobs

    def add_job(self, job):
        #print(json.dumps(job.__getstate__(), cls=JobEncoder))
        insert = self.jobs_t.insert().values(**{
            'id': job.id,
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol),
            'job_json': json.dumps(job.__getstate__(), cls=JobEncoder)
        })
        try:
            self.engine.execute(insert)
        except IntegrityError:
            raise ConflictingIdError(job.id)

    def update_job(self, job):
        update = self.jobs_t.update().values(**{
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol),
            'job_json': json.dumps(job.__getstate__(), cls=JobEncoder)
        }).where(self.jobs_t.c.id == job.id)
        result = self.engine.execute(update)
        if result.rowcount == 0:
            raise JobLookupError(id)

    def remove_job(self, job_id):
        delete = self.jobs_t.delete().where(self.jobs_t.c.id == job_id)
        result = self.engine.execute(delete)
        if result.rowcount == 0:
            raise JobLookupError(job_id)

    def remove_all_jobs(self):
        delete = self.jobs_t.delete()
        self.engine.execute(delete)

    def shutdown(self):
        self.engine.dispose()

    def _reconstitute_job(self, job_state, job_json):
        #job_state = pickle.loads(job_state)
        #print("_______")
        #print(job_state)
        #json.loads(job_json,cls=JobDecoder)
        #print(json.loads(job_json,cls=JobDecoder))
        job_state = json.loads(job_json,cls=JobDecoder)
        #print(job_json)
        #print("--------")
        job_state['jobstore'] = self
        job = Job.__new__(Job)
        job.__setstate__(job_state)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        return job

    def _get_jobs(self, *conditions):
        jobs = []
        selectable = select([self.jobs_t.c.id, self.jobs_t.c.job_state, self.jobs_t.c.job_json]).\
            order_by(self.jobs_t.c.next_run_time)
        selectable = selectable.where(*conditions) if conditions else selectable
        failed_job_ids = set()
        for row in self.engine.execute(selectable):
            try:
                jobs.append(self._reconstitute_job(row.job_state, row.job_json))
            except BaseException:
                self._logger.exception('Unable to restore job "%s" -- removing it', row.id)
                failed_job_ids.add(row.id)

        # Remove all the jobs we failed to restore
        if failed_job_ids:
            delete = self.jobs_t.delete().where(self.jobs_t.c.id.in_(failed_job_ids))
            self.engine.execute(delete)

        return jobs

    def __repr__(self):
        return '<%s (url=%s)>' % (self.__class__.__name__, self.engine.url)
    
    

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger 
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, tzinfo
from pytz import timezone
from apscheduler.triggers.cron.fields import (
    BaseField, MonthField, WeekField, DayOfMonthField, DayOfWeekField, DEFAULT_VALUES)
import re
  
class JobEncoder(json.JSONEncoder):  
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.__str__() #__repr__
        elif isinstance(obj, CronTrigger):
#            if isinstance(obj.timezone, tzinfo):
#                #print(type(obj.__str__()))
#                #print(obj)
#                obj.timezone = obj.timezone.__str__()
#            elif isinstance(obj.timezone, timezone):
#                #print(type(obj.__str__()))
#                #print(obj)
#                obj.timezone = obj.timezone.__str__()
            return obj.__repr__()
        return json.JSONEncoder.default(self, obj)
    
class JobDecoder(json.JSONDecoder): 
    #def decode(self, s, _w=<built-in method match of re.Pattern object at 0x10609a870>)
    def decode(self, d, **kwargs):
        d = json.loads(d)
        
        #trigger
        findall = re.findall(r"<(.*?) \((.*?,) timezone='(.*?)'\)>",d['trigger'])
        name = findall[0][0]
        if name in ("CronTrigger", "DateTrigger", "IntervalTrigger"):
            d['trigger'] = eval(name)()
        state = {}
        #fields = {}
        if findall[0][1]:
            attr = re.findall(r"(.*?)='(.*?)',", findall[0][1])
            for a in attr:
                state[a[0]] = a[1]
                #if a[0] not in ('start_date','end_date','fields','jitter','timezone'):
                #    fields[a[0]] = a[1]
                
        #print(name)
        if name=='CronTrigger':
            #state['second'] = '*/6'
            d['trigger'] = CronTrigger(**state)
            
        #next_run_time
        #todo:datetime.datetime(2018, 11, 7, 17, 54, 45, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>)}
        d['next_run_time'] = datetime.strptime(d['next_run_time'], "%Y-%m-%d %H:%M:%S%z")
        return d
    
        
    
    