# -*- coding: utf-8 -*-
import scrapy

# 通用爬虫
from scrapy.contrib.spiders import CrawlSpider, Rule


class DmozSpider(scrapy.Spider):
    name = 'dmoz'
    allowed_domains = ['dmoz.org']
    start_urls = ['http://dmoz.org/']

    def parse(self, response):
        pass
