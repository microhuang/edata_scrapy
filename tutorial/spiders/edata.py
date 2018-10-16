# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Request

from scrapy_redis.spiders import RedisSpider

from tutorial.items import BaiduItem

import re


class EdataSpider(RedisSpider):
    name = 'edata'
    redis_key = 'edata:start_urls'

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
                      }

    def parse(self, response):
        #提取内容
        item = self.__extract_item(response)
        if item:
            yield item

        #提取url
        next_url = self.__extract_url(response)
        if 'url' in next_url and next_url['url']:
            if not next_url['dont_filter']:
                next_url['dont_filter'] = False
            req = Request(url=next_url['url'], callback=self.parse, dont_filter=next_url['dont_filter'])
            if req:
                yield req

    def __extract_url(self, response):
        #请求资源匹配
        url = ''

        try:
            for k in self.request_res_route:
                if k==response.url or isinstance(k, re.Pattern) and re.match(k,response.url):
                    url = eval(self.request_res_route[k]+'Next').extract(response)
                    break
        except KeyError:
            pass
        except:
            pass
            
        return url

    def __extract_item(self, response):
        #模版资源匹配
        item = None
        
        try:
            for k in self.item_res_route:
                if k==response.url or isinstance(k, re.Pattern) and re.match(k,response.url):
                    item = eval(self.item_res_route[k]+'Item').extract(response)
                    break
        except KeyError:
            pass
        except:
            pass

        return item
    

#todo：以下建议模块化
class LocalNext(object):
    @staticmethod
    def extract(response):
        #todo
        next_url = "http://localhost:8081/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}
    
#百度url页面的next提取逻辑
class BaiduNext(object):
    @staticmethod
    def extract(response):
        #todo
        next_url = "https://www.baidu.com/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}

class SinaNext(object):
    @staticmethod
    def extract(response):
        #todo
        next_url = "http://www.sina.com.cn/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}

class BaiduListNext(object):
    @staticmethod
    def extract(response):
        next_url = None
        #todo
        r_next_url = re.search(r'href="(.*?)"',str(response.body, encoding='utf-8'))
        if r_next_url:
            next_url = r_next_url.group(1)
            if next_url.startswith('/'):
                next_url = 'http://www.baidu.com'+next_url
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}
    

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




