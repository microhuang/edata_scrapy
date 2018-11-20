# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


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
        #todo:xxxx
        if item.__class__.__name__=='JobcnSearchJsonItem':
            companys = json.loads(item['companys'])
            for c in companys:
                line = c + "\n"
                self.file.write(line)
        if item.__class__.__name__=='Job5156SearchJsonItem' or item.__class__.__name__=='Job5156SearchItem':
            companys = json.loads(item['companys'])
            for c in companys:
                line = c + "\n"
                self.file.write(line)
        
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


class Job51Pipeline(object):
    def process_item(self, item, spider):
        if item.__class__.__name__=='Job51SearchItem':
            companys = json.loads(item['companys'])
            for c in companys:
                line = c + "\n"
                self.file.write(line)
        return item
    
    def open_spider(self,spider):
        self.file = codecs.open('/tmp/job51.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()
        
    
class CjolPipeline(object):
    def process_item(self, item, spider):
        if item.__class__.__name__=='CjolSearchItem':
            try:
                companys = json.loads(item['companys'])
                for c in companys:
                    line = c + "\n"
                    self.file.write(line)
            except KeyError:
                print('缺少有效数据！')
                pass
        return item

    def open_spider(self,spider):
        self.file = codecs.open('/tmp/cjol.json', 'wb', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()
