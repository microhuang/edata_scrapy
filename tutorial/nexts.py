# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.http import Request

import re


class LocalNext(object):
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "http://localhost:8081/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}
    
#百度url页面的next提取逻辑
class BaiduNext(object):
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "https://www.baidu.com/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}

class SinaNext(object):
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "http://www.sina.com.cn/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}

class BaiduListNext(object):
    @staticmethod
    def extract(response,spider):
        next_url = None
        dont_filter = True
        domain='http://www.baidu.com'
        if response.url.startswith('https://www.baidu.com/'):
            domain='https://www.baidu.com'
        #todo
        #next_urls = re.findall(r'<a .*?href="(.*?)"',str(response.body, encoding='utf-8'))
        next_urls = re.finditer(r'<a .*?href="(.*?)"',str(response.body, encoding='utf-8'))
        for next_url in next_urls:
            next_url = next_url.group(1)
            if 'javascript:;'==next_url or "javascript"==next_url or next_url.startswith('#'):
                continue
            if next_url.startswith('/'):
                next_url=domain+next_url
            #if next_url.startswith('http://www.baidu.com/link?url'):
            #    print(next_url)
            #这是一个demo，只对当前页面“百度搜索结果”中的link?链接进行深入爬取
            if next_url.startswith('http://www.baidu.com/link?url='):
                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
                yield req

