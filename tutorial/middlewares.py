# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

import re


class TutorialSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TutorialDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# ua\ip\...
# # IP池请参考： http://pkmishra.github.io/blog/2013/03/18/how-to-run-scrapy-with-TOR-and-multiple-browser-agents-part-1-mac/
class EdataDownloaderMiddleware(UserAgentMiddleware):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        #s = cls(timeout=1, service_args=3)
        s = cls()
        return s
    
    #def __init__(self, timeout=None, service_args=[]):
    def __init__(self):
        '''
        #只在需要时初始化
        self.use_selenium = False
        if self.use_selenium:
            self.browser = webdriver.PhantomJS(service_args=service_args)
            #self.browser = webdriver.Chrome()
            self.wait = WebDriverWait(self.browser, 25)
            self.use_selenium = True
        '''

    def __del__(self):
        if self.browser:
            self.browser.close()
        
    def process_request(self, request, spider):
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'
        request.headers.setdefault('User-Agent', ua)

        # request_res_route
        for k in spider.request_res_route:
            if k==request.url or isinstance(k, re.Pattern) and re.match(k,request.url):
                spider.logger.info('request_res_route_key: %s' % k)
                spider.request_res_route_key = k
                break

        # UA
        if spider.request_res_route_key and spider.request_res_route and 'UA' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['UA']:
            ua = spider.request_res_route[spider.request_res_route_key]['UA']

        request.headers['USER_AGENT']=ua

        # Selenium
        if spider.request_res_route_key and spider.request_res_route and 'UseSelenium' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['UseSelenium']==True:
            self.use_selenium = True
            if not self.browser:
                self.browser = webdriver.PhantomJS()
                #self.browser = webdriver.Chrome()
                self.wait = WebDriverWait(self.browser, 25)
                #self.use_selenium = True
        else:
            self.use_selenium = False
        if self.use_selenium:
            try:
                spider.browser.get(request.url)
            except Exception as e:
                return HtmlResponse(url=request.url, status=500, request=request)
            else:
                return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8', status=200)
            

    
