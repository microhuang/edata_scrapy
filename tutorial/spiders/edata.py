# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Request

from scrapy_redis.spiders import RedisSpider

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from tutorial.items import *
from tutorial.nexts import *

import re


class EdataSpider(RedisSpider):
    name = 'edata'
    redis_key = 'edata:start_urls'

    '''
    #todo:请从数据库初始化配置
    # url => next_url
    # 1、全匹配，2、正则匹配
    request_res_route = {'http://localhost:8081/':'Local',
                         'https://www.baidu.com/':'Baidu',
                         'http://www.sina.com.cn/':'Sina',
                         re.compile(r'https://www.baidu.com/s\?wd=\w'):'BaiduList',
                         }
    # url => item
    # 1、全匹配，2、正则匹配
    item_res_route = {'http://localhost:8081/':'Local',
                      'https://www.baidu.com/':'Baidu',
                      'http://www.sina.com.cn/':'Sina',
                      #re.compile(r'https://www.baidu.com/s\?wd=\w'):'BaiduList',
                      re.compile(r'https://blog.csdn.net/\w+/article/details/\d+'):'CsdnArticle',
                      }
    '''

    def __init__(self):
        #可闲时更新配置
        dispatcher.connect(self.setup, signals.spider_idle)
        pass

    def setup(self):
        #从配置库获取这些数据
        self.request_res_route = {'http://localhost:8081/':'Local',
                         'https://www.baidu.com/':'Baidu',
                         'http://www.sina.com.cn/':'Sina',
                         re.compile(r'https://www.baidu.com/s\?wd=\w'):'BaiduList',
                         }
        self.item_res_route = {'http://localhost:8081/':'Local',
                      'https://www.baidu.com/':'Baidu',
                      'http://www.sina.com.cn/':'Sina',
                      #re.compile(r'https://www.baidu.com/s\?wd=\w'):'BaiduList',
                      re.compile(r'https://blog.csdn.net/\w+/article/details/\d+'):'CsdnArticle',
                      }
        pass
                           
    def parse(self, response):
        #提取内容
        item = self.__extract_item(response)
        #print(44444)
        if item:
            #print(item)
            yield item

        #提取url
        next_url = self.__extract_url(response)
        for req in next_url:
            yield req
        '''
        if 'url' in next_url and next_url['url']:
            if not next_url['dont_filter']:
                next_url['dont_filter'] = False
            req = Request(url=next_url['url'], callback=self.parse, dont_filter=next_url['dont_filter'])
            if req:
                yield req
        '''

    def __extract_url(self, response):
        #请求资源匹配
        url = ''

        try:
            for k in self.request_res_route:
                if k==response.url or isinstance(k, re.Pattern) and re.match(k,response.url):
                    url = eval(self.request_res_route[k]+'Next').extract(response,self)
                    for r in url:
                        yield r
                    break
        except KeyError:
            pass
        #except:
            pass
            
        return url

    def __extract_item(self, response):
        #模版资源匹配
        item = None
        
        try:
            for k in self.item_res_route:
                #print(33333)
                #print(response.url)
                #print(444444)
                if k==response.url or isinstance(k, re.Pattern) and re.match(k,response.url):
                    #print(response.url)
                    item = eval(self.item_res_route[k]+'Item').extract(response)
                    break
        except KeyError:
            pass
        #except:
            pass

        return item
    

'''
#todo：以下建议模块化
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
'''

'''
#请从items实现
class LocalItem(scrapy.Item):
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        item = LocalItem()
        #todo
        #item['response'] = response
        item['title'] = 'local'
        return item
    
#百度url页面的item提取逻辑     
class BaiduItem(scrapy.Item):
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        item = BaiduItem()
        #todo
        #item['response'] = response
        item['title'] = response.xpath('//title/text()').extract()
        return item

class SinaItem(scrapy.Item):
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        item = SinaItem()
        #todo
        #item['response'] = response
        item['title'] = 'sina'
        return item
'''




