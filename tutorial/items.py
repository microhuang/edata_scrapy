# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import json
from scrapy import Selector


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
    
class JobcnSearchJsonItem(scrapy.Item):
    url = scrapy.Field()
    companys = scrapy.Field()
    
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
        if len(rows)>0:
            for row in rows:
                companys.add(row['comName'])
        item['url'] = response.url
        item['companys'] = json.dumps(list(companys),ensure_ascii=False)
            
        return item
    
class JobcnPositionDetailItem(scrapy.Item):
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
    
class Job5156SearchItem(scrapy.Item):
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
    
class Job5156SearchJsonItem(scrapy.Item):
    url = scrapy.Field()
    companys = scrapy.Field()
    
    @staticmethod
    def extract(response):
        item = Job5156SearchJsonItem()
        item['url'] = response.url
        
        rows = json.loads(response.body)['page']['items']
        if rows:
            companys = set()
            for r in rows:
                companys.add(r['comName'])
            item['companys'] = json.dumps(list(companys),ensure_ascii=False)
        
        return item
    
class Job51SearchItem(scrapy.Item):
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

class CjolSearchItem(scrapy.Item):
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
    
    
    
    
    