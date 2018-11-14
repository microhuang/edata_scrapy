# -*- coding: utf-8 -*-

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger


class JsonCronTrigger(CronTrigger):
    def __repr__(self):
        options = ["%s='%s'" % (f.name, f) for f in self.fields if not f.is_default]
        if self.start_date:
            options.append("start_date=%r" % datetime_repr(self.start_date))
        if self.end_date:
            options.append("end_date=%r" % datetime_repr(self.end_date))
        if self.jitter:
            options.append('jitter=%s' % self.jitter)

        return "<%s (%s, timezone='%s')>" % (
            self.__class__.__name__, ', '.join(options), self.timezone)
            
    @classmethod
    def from_crontab(cls, expr, timezone=None):
        CronTrigger.from_crontab(cls,expr, timezone)
        
        