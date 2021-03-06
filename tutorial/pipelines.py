# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

#from twisted.enterprise import adbapi #提供异步数据库访问


import json

import codecs

from scrapy.exporters import JsonItemExporter


class TutorialPipeline(object):
    def process_item(self, item, spider):
        return item


class EdataPipeline(object):
#    def __init__(self):
#        self.file = open('/tmp/items.json', 'w+', encoding='utf-8')
#        
#    @classmethod
#    def from_crawler(cls,crawler):
#        cls.file = open('/tmp/items.json', 'w+', encoding='utf-8')
        
    def process_item(self, item, spider):
#        if spider.crawler.stats.get_value(item['task_id'])==0:
#            #通知任务完成
#            #重启爬虫
#            from scrapy.exceptions import CloseSpider
#            raise CloseSpider('任务结束，重启Sprider！')
#            pass
        #todo:xxxx
        
#        line = json.dumps(dict(item), ensure_ascii=False, sort_keys=False) + "\n"
#        self.file.write(line)
        
#        line = json.dumps(dict(item),ensure_ascii=False) + "\n"
##        self.file = open('/tmp/items.json', 'w+', encoding='utf-8')
#        self.file.write(line)
##        self.file.close()
#        self.exporter.export_item(item)
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/jobcn.json', 'wb', encoding='utf-8')
#        self.file = open('items.json', 'wb')
#        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
#        self.exporter.start_exporting()
        
    def close_spider(self, spider):
#        self.exporter.finish_exporting()
        self.file.close()


class Job5156Pipeline(object):
    def process_item(self, item, spider):
        if item.__class__.__name__=='Job5156SearchJsonItem' or item.__class__.__name__=='Job5156SearchItem':
            try:
#                companys = json.loads(item['companys'])
#                for c in companys:
#                    line = c + "\n"
#                    self.file.write(line)
                positions = json.loads(item['positions'])
                for p in positions:
                    line = str(p) + "\n"
                    self.file.write(line)
                    self.file.flush()
            except KeyError:
                print('缺少有效数据！')
                pass
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/job5156.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()
        
#    @classmethod
#    def from_settings(cls, settings):
#        cls.save_path = '/tmp/'
#        return cls
        
class JobcnPipeline(object):
    def process_item(self, item, spider):
        if item.__class__.__name__=='JobcnSearchJsonItem':
            try:
#                companys = json.loads(item['companys'])
#                for c in companys:
#                    line = c + "\n"
#                    self.file.write(line)
                positions = json.loads(item['positions'])
                for p in positions:
                    line = str(p) + "\n"
                    self.file.write(line)
                    self.file.flush()
            except KeyError:
                print('缺少有效数据！')
                pass
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/jobcn.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()


class Job51Pipeline(object):
    def process_item(self, item, spider):
#        if item.__class__.__name__=='Job51SearchItem':
#            companys = json.loads(item['companys'])
#            for c in companys:
#                line = c + "\n"
#                self.file.write(line)
        if item.__class__.__name__=='Job51PositionItem':
            line = str(item) + "\n"
            self.file.write(line)
            self.file.flush()
        return item
    
    def open_spider(self,spider):
        self.file = codecs.open('/tmp/job51.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()
        
    
class CjolPipeline(object):
    def process_item(self, item, spider):
#        if item.__class__.__name__=='CjolSearchItem':
#            try:
#                companys = json.loads(item['companys'])
#                for c in companys:
#                    line = c + "\n"
#                    self.file.write(line)
#            except KeyError:
#                print('缺少有效数据！')
#                pass
        if item.__class__.__name__=='CjolPositionItem':
            line = str(item) + "\n"
            self.file.write(line)
            self.file.flush()
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/cjol.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()


class ZhaopinPipeline(object):
    def process_item(self, item, spider):
#        if item.__class__.__name__=='ZhaopinSearchJsonItem':
#            try:
#                companys = json.loads(item['companys'])
#                for c in companys:
#                    line = c + "\n"
#                    self.file.write(line)
#            except KeyError:
#                print('缺少有效数据！')
#                pass
        if item.__class__.__name__=='ZhaopinPositionItem':
            line = str(item) + "\n"
            self.file.write(line)
            self.file.flush()
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/zhaopin.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()
        
        
class JobcnHireViewPipeline(object):
    def process_item(self, item, spider):
        if item.__class__.__name__=='JobcnHireViewItem':
            line = str(item) + "\n"
            self.file.write(line)
            self.file.flush()
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/jobcnhire.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()