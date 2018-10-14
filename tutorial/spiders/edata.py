# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scrapy_redis.spiders import RedisSpider


class EdataSpider(RedisSpider):
    name = 'edata'
    redis_key = 'edata:start_urls'

    def parse(self, response):
        # do stuff
        pass


'''
class EdataSpider(CrawlSpider):
    name = 'edata'
    allowed_domains = ['tech.china.com']
    start_urls = ['http://tech.china.com/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        print("iiiiiiiiiiiiiiiiiiiiiiiiii")
        super(EdataSpider, self).__init__(*args, **kwargs)
        pass

    def _make_request(self, mframe, hframe, body):
        print("mmmmmmmmmmmmmmmmmmmmmmmmmm")
        url = body.decode()
        return scrapy.Request(url, callback=self.parse)

    def parse_item(self, response):
        i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
'''




