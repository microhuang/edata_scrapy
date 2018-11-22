# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

#from scrapy.http import FormRequest

import re

from tutorial.nexts import *


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
        #cls.crawler = crawler
        #s = cls(timeout=1, service_args=3)
        s = cls()
        return s
    
    #def __init__(self, timeout=None, service_args=[]):
    def __init__(self):
        self.browser = None
        
        UserAgentMiddleware.__init__(self)
        
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
            
    def process_response(self, request, response, spider):
        # todo:获取登陆账号
        if spider.request_res_route_key and 'LoginUser' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['LoginUser']:
            spider.logger.info('edata logining ... %s ' % response.url)
#            request = FormRequest.from_response(response=response,
#                                                meta={'cookiejar': response.meta['cookiejar'] if response and hasattr(response, 'meta') and 'cookiejar' in response.meta else None},
#                                                #headers=self.post_headers,
#                                                formdata={
#                                                    #"utf8": utf8,
#                                                    #"authenticity_token": authenticity_token,
#                                                    "login": spider.request_res_route[spider.request_res_route_key]['LoginUser'],
#                                                    "password": spider.request_res_route[spider.request_res_route_key]['LoginPass'] if spider.request_res_route[spider.request_res_route_key]['LoginPass'] else '',
#                                                    #"commit": commit
#                                                },
#                                                callback=request.callback,
#                                                dont_filter=request.dont_filter)
            request = eval(spider.request_res_route[spider.request_res_route_key]['next']+'Next').login(request, response, spider)
            # 使用后释放标记，防止污染
            spider.request_res_route_key = None
            return request
        return response
        
    def process_request(self, request, spider):
        #help(self.crawler.engine.downloader)
        #ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'
        #request.headers.setdefault('User-Agent', ua)

        # request_res_route
        if spider.request_res_route:
            for k in spider.request_res_route:
                if k==request.url or 'type' in spider.request_res_route[k] and spider.request_res_route[k]['type']=='starts' and request.url.startswith(k) or isinstance(k, re.Pattern) and re.match(k,request.url):
                    spider.logger.info('request_res_route_key: %s => %s' % (k, spider.request_res_route[k]))
                    spider.request_res_route_key = k
                    break
            else:
                spider.request_res_route_key = None

        # UA
        if spider.request_res_route_key and spider.request_res_route and 'UA' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['UA']:
            ua = spider.request_res_route[spider.request_res_route_key]['UA']
            request.headers['USER_AGENT']=ua

        # cookie
        #if spider.request_res_route_key and spider.request_res_route and 'useCookie' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['useCookie']:
        #    self.crawler.settings.set('COOKIES_ENABLED', True)
        #else:
        #    self.crawler.settings.set('COOKIES_ENABLED', False)

        # login
        #if spider.request_res_route_key and spider.request_res_route and 'LoginUser' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['LoginUser']:
        #    request = FormRequest(request.url, callback=request.callback, dont_filter=request.dont_filter, method = 'POST', formdata={'login':spider.request_res_route[spider.request_res_route_key]['LoginUser'],'password':spider.request_res_route[spider.request_res_route_key]['LoginPass']})
        #elif 'LoginUser' in request.meta:
        #    del request.meta['LoginUser']
        
        # proxy
        if spider.request_res_route_key and spider.request_res_route and 'proxy' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['proxy']:
            request.meta['proxy'] = spider.request_res_route[spider.request_res_route_key]['proxy']
        elif 'proxy' in request.meta:
            del request.meta['proxy']
            
        # Selenium
        if spider.request_res_route_key and spider.request_res_route and 'useSelenium' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['useSelenium']==True:
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
            

    
