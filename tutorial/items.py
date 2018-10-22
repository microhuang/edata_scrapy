# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


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

    
