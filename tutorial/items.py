# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import json
import re
import sys
from urllib.parse import urlparse,parse_qs,urlunparse,urlencode,unquote,quote
from abc import ABCMeta, abstractmethod,abstractproperty
if sys.version_info > (3, 0):
    from abc import abstractstaticmethod
import six
from scrapy import Selector


@six.add_metaclass(ABCMeta)
class EdataItem(scrapy.Item):
    #为了保证pipeline获得任务信息，请确保task_id有效
    task_id = scrapy.Field()
    
#    @abstractstaticmethod
    @staticmethod
    def extract(response):
#        item = EdataItem()
#        item['task_id'] = response.meta['task_id']
        pass

    
class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


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

# https://blog.csdn.net/\w+/article/details/\d+
class CsdnArticleItem(scrapy.Item):
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        item = CsdnArticleItem()
        #todo
        #item['response'] = response
        item['title'] = response.xpath('//title/text()').extract()
        return item

# https://media.weibo.cn/article/amp?id=2309614279344888477175
# https://media.weibo.cn/article?id=2309614279344888477175
class WeiboMediaArticleItem(scrapy.Item):
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        item = WeiboMediaArticleItem()
        #todo
        #item['response'] = response
        item['title'] = response.xpath('//title/text()').extract()
        return item

# https://weibo.com/u/3659206143
class WeiboUserItem(scrapy.Item):
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        print("爬取到微博用户主页")
        item = WeiboUserItem()
        #todo
        #item['response'] = response
        item['title'] = response.xpath('//title/text()').extract()
        return item

# https://github.com/settings/profile
class GithubProfileItem(scrapy.Item): 
    title = scrapy.Field()

    @staticmethod
    def extract(response):
        print("Githubv用户主页")
        item = GithubProfileItem()
        #todo
        #item['response'] = response
        item['title'] = response.xpath('//title/text()').extract()
        return item
    
class JobcnSearchJsonItem(EdataItem):
    url = scrapy.Field()
    companys = scrapy.Field()
    positions = scrapy.Field()
    
    @staticmethod
    def extract(response):
        item = JobcnSearchJsonItem()
        
        response_body = ''
        try:
            response_body = str(response.body, encoding='utf-8')
        except:
            try:
                response_body = str(response.body, encoding='gbk')
            except:
                response_body = str(response.body, encoding='gb2312')
            pass
        
        rows = json.loads(response_body)['rows']
        companys = set()
        positions = []
        if len(rows)>0:
            for row in rows:
                if re.search(r'\bsolidwork|solidworks|sw\b',row['posDescription']):
                    companys.add(row['comName'])
                    positions.append({'company':row['comName'], 'position':row['posDescription']})
        item['url'] = response.url
        item['companys'] = json.dumps(list(companys),ensure_ascii=False)
        item['positions'] = json.dumps(list(positions),ensure_ascii=False)
            
        return item
    
class JobcnPositionDetailItem(EdataItem):
    company = scrapy.Field()
    
    @staticmethod
    def extract(response):
#        response_body = ''
#        try:
#            response_body = str(response.body, encoding='utf-8')
#        except:
#            try:
#                response_body = str(response.body, encoding='gbk')
#            except:
#                response_body = str(response.body, encoding='gb2312')
#            pass
        
        item = JobcnPositionDetailItem()
        
        item['company'] = response.xpath('//*[@id="menuHeader"]/div[1]/div[2]/h2/text()').extract()[0]
        return item
    
class Job5156SearchItem(EdataItem):
    url = scrapy.Field()
    companys = scrapy.Field()
    
    @staticmethod
    def extract(response):
        item = Job5156SearchItem()
        item['url'] = response.url
        
        selectors = response.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li')
        if selectors:
            companys = set()
            for s in selectors:
                companys.add(s.xpath('div/div[2]/a/text()').extract()[0])
            item['companys'] = json.dumps(list(companys),ensure_ascii=False)
        return item
    
class Job5156SearchJsonItem(EdataItem):
    url = scrapy.Field()
    companys = scrapy.Field()
    positions = scrapy.Field()
    
    @staticmethod
    def extract(response):
        item = Job5156SearchJsonItem()
        item['url'] = response.url
        
        if json.loads(response.body)['page']:
            
            rows = json.loads(response.body)['page']['items']
            if rows:
                companys = set()
                positions = []
                for row in rows:
                    if re.search(r'\bsolidwork|solidworks|sw\b',row['posDesc']):
                        companys.add(row['comName'])
                        positions.append({'company':row['comName'], 'position':row['posDesc']})
                item['companys'] = json.dumps(list(companys),ensure_ascii=False)
                item['positions'] = json.dumps(list(positions),ensure_ascii=False)
        
        return item
    
#Deprecated
class Job51SearchItem(EdataItem):
    url = scrapy.Field()
    companys = scrapy.Field()
    
    @staticmethod
    def extract(response):
        item = Job51SearchItem()
        
        item['url'] = response.url
        selectors = response.xpath('//*[@id="resultList"]/div/span[1]/a/text()').extract()
        if selectors:
            companys = set()
            for s in selectors:
                companys.add(s)
            item['companys'] = json.dumps(list(companys),ensure_ascii=False)
            
        return item
          
class Job51PositionItem(EdataItem):
    url = scrapy.Field()
    company = scrapy.Field()
    position = scrapy.Field()
    @staticmethod
    def extract(response):
        item = Job51PositionItem()
        selector = response.xpath('/html/body/div[3]/div[2]')
        if selector:
            position = selector.xpath("div[3]/div[1]/div").extract()[0]
            if re.search(r'\bsolidwork|solidworks|sw\b',position):
                company = selector.xpath("div[2]/div/div[1]/p[1]/a[1]/text()").extract()[0]
                item['company'] = company
                item['position'] = position
        return item

#Deprecated
class CjolSearchItem(EdataItem):
    url = scrapy.Field()
    companys = scrapy.Field()
    
    @staticmethod
    def extract(response):
        item = CjolSearchItem()
        
        item['url'] = response.url
        html = json.loads(response.body)['JobListHtml']
        if html:
            selector = Selector(text=html)
            selectors = selector.xpath('//*[@id="searchlist"]/ul/li[3]/a/text()').extract()
            if selectors:
                companys = set()
                for s in selectors:
#                    print(9999,s)
                    companys.add(s)
                item['companys'] = json.dumps(list(companys),ensure_ascii=False)
            
        return item
    
class CjolPositionItem(EdataItem):
    url = scrapy.Field()
    company = scrapy.Field()
    position = scrapy.Field()
    @staticmethod
    def extract(response):
        item = CjolPositionItem()
        selector = response.xpath("/html/body/div[4]/div[1]/div")
        if selector:
            position = selector.xpath("div[3]/div[2]").extract()[0]
            if re.search(r'\bsolidwork|solidworks|sw\b',position):
                company = selector.xpath("div[1]/div/div[1]/div[1]/div[2]/a/text()").extract()[0]
                item['company'] = company
                item['position'] = position
#                print(66666, position)
#            print(7777, position)
        return item
    
class ZhaopinSearchJsonItem(EdataItem):
    url = scrapy.Field()
    companys = scrapy.Field()
    @staticmethod
    def extract(response):
        item = ZhaopinSearchJsonItem()
        
        item['url'] = response.url
        rows = json.loads(response.body)['data']['results']
        if rows:
            companys = set()
            for c in rows:
                companys.add(c['company']['name'])
            item['companys'] = json.dumps(list(companys),ensure_ascii=False)
            
        return item
    
#company从列表页带入
class ZhaopinPositionItem(EdataItem):
    url = scrapy.Field()
    company = scrapy.Field()
    position = scrapy.Field()
    @staticmethod
    def extract(response):
        item = ZhaopinPositionItem()
        selector = response.xpath("/html/body/div[1]/div[3]/div[5]/div[1]")
        position = selector.extract()[0]
        if re.search(r'\bsolidwork|solidworks|sw\b',position):
            #来自列表页
            company = response.meta['company']
            item['company'] = company
            item['position'] = position
        
        return item
    
#版面识别
class SinaItem(EdataItem):
    url = scrapy.Field()
    a_urls_json = scrapy.Field()
    @staticmethod
    def extract(response):
        item['url'] = response.url
        response_body = ''
        try:
            response_body = str(response.body, encoding='utf-8')
        except:
            try:
                response_body = str(response.body, encoding='gbk')
            except:
                response_body = str(response.body, encoding='gb2312')
            pass
        next_urls = re.finditer(r'<a .*?href="(.*?)".*?>(.*?)</a>', response_body)
        for url in next_urls:
            next_url = url.group(1)
            next_a = url.group(2)
        
   
#简历页面
class JobcnHireViewItem(EdataItem):
    url = scrapy.Field()
    html_all = scrapy.Field()
#    html_base = scrapy.Field()
#    html_desc = scrapy.Field()
    @staticmethod
    def extract(response):
        item = JobcnHireViewItem()
        item['url'] = response.url
        response_body = ''
        try:
            response_body = str(response.body, encoding='utf-8')
        except:
            try:
                response_body = str(response.body, encoding='gbk')
            except:
                response_body = str(response.body, encoding='gb2312')
            pass
        try:
            k = parse_qs(urlparse(response.url)[4])['ref'][0]
            html_all = response.xpath('//*[@id="%s"]/tbody/tr/td/table' % k).extract()
#            html_base = response.xpath('//*[@id="%s"]/tbody/tr/td/table/tbody/tr[2]/td/div/table' % k).extract()
#            html_desc = response.xpath('//*[@id="%s"]/tbody/tr/td/table/tbody/tr[4]/td/table[2]' % k).extract()
            item['html_all'] = html_all
#            item['html_base'] = html_base
#            item['html_desc'] = html_desc
#            print(8888, html_base, html_desc)
        except Exception as e:
            print('提取错误', e)
            pass
        return item
    
    
    
    
    
    
