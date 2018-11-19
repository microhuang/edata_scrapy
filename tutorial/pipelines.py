# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import json

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
#        line = json.dumps(dict(item),ensure_ascii=False) + "\n"
##        self.file = open('/tmp/items.json', 'w+', encoding='utf-8')
#        self.file.write(line)
##        self.file.close()
        self.exporter.export_item(item)
        return item

    def open_spider(self,spider):
        self.file = open('items.json', 'wb')
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()
        
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
