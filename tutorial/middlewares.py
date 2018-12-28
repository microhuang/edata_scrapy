# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

from scrapy.http import HtmlResponse

#from scrapy.http import FormRequest

from scrapy.mail import MailSender

import re

import json

from collections import OrderedDict

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
#        mailer = MailSender.from_settings(settings)
#        mailer.send(to=["someone@example.com"], subject="Some subject", body="Some body", cc=["another@example.com"])
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

from scrapy_pyppeteer import BrowserRequest
from scrapy_pyppeteer import BrowserResponse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import asyncio
from pyppeteer import launch

async def ppeteer(url):
#    browser = await launch({'executablePath': '/Users/1data/Downloads/Chromium.app'})
    browser = await launch({'headless': True})
    page = await browser.newPage()
    response = await page.goto(url)
    body = await page.content()
    localstorages = await page.evaluate('''() => { var l = {}; for(var i=0; i<localStorage.length; i++){ l[localStorage.key(i)] = localStorage.getItem(localStorage.key(i)); } return l; }''')
    cookies = await page.cookies()
    await page.close()
    await browser.close()
    return body,localstorages,cookies,response.status,response.headers

def ppeteer_body(t, future):
    return future.result

#url = 'http://www.iwencai.com/index?tid=info&ts=1&qs=index_channel'
#url='chrome-devtools://devtools/bundled/inspector.html'
#asyncio.get_event_loop().run_until_complete(ppeteer(url))
#task = asyncio.ensure_future(ppeteer(url))
#task.add_done_callback(ppeteer_body)
#asyncio.get_event_loop().run_until_complete(asyncio.ensure_future(ppeteer(url)))

# ua\ip\...
# # IP池请参考： http://pkmishra.github.io/blog/2013/03/18/how-to-run-scrapy-with-TOR-and-multiple-browser-agents-part-1-mac/
class EdataDownloaderMiddleware(UserAgentMiddleware):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        #cls.crawler = crawler
        #s = cls(timeout=1, service_args=3)
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
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
        if self.browser and hasattr(self.browser, 'close'):
            self.browser.close()
            
    def spider_opened(self, spider):
        spider.logger.info('%s opened' % spider.name)
            
    def process_exception(self, request, exception, spider):
        #计数
        if 'task_id' in request.meta:
            spider.crawler.stats.inc_value(request.meta['task_id'], -(request.meta.get('retry_times', 0)+1))
#            #todo:xxxx
##            print(99999, spider.crawler.stats.get_value(request.meta['task_id']))
#            #任务完成？
#            if spider.crawler.stats.get_value(request.meta['task_id'])==0:
##                mailer = MailSender.from_settings(settings)
##                mailer.send(to=["someone@example.com"], subject="Some subject", body="Some body", cc=["another@example.com"])
#                pass
            
    def process_response(self, request, response, spider):
        #计数
        if 'task_id' in request.meta:
            spider.crawler.stats.inc_value(request.meta['task_id'], -1)
#            #todo:xxxx
#            print(88888, spider.crawler.stats.get_value(request.meta['task_id']))
#            #任务完成？
#            if spider.crawler.stats.get_value(request.meta['task_id'])==0:
##                mailer = MailSender.from_settings(settings)
##                mailer.send(to=["someone@example.com"], subject="Some subject", body="Some body", cc=["another@example.com"])
#                pass
            
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
        # 使用后释放标记，防止污染
#        spider.request_res_route_key = None
#        print(999999, self.browser.execute_script('return localStorage.getItem("hexin-v");'))
        if self.browser is not None:
            response.browser = self.browser
        return response
        
    def process_request(self, request, spider):
#        print(444444444, request.url)
        if isinstance(request, BrowserRequest):
            return None
#        print(55555, request.headers)
#        from scrapy.exceptions import CloseSpider
#        raise CloseSpider('任务结束，重启Sprider！')
        #help(self.crawler.engine.downloader)
        #ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'
        #request.headers.setdefault('User-Agent', ua)
        
        #task_id
        if 'task_id' not in request.meta:
            from uuid import uuid4
            task_id = uuid4().hex
            spider.logger.warn('缺少task_id！ 由框架生成： %s' % task_id)
            request.meta['task_id'] = task_id
        
        #计数
#        print(777777, spider.crawler.stats.get_value(request.meta['task_id']))
        spider.crawler.stats.inc_value(request.meta['task_id'], 1)

        # request_res_route
        if spider.request_res_route:
            for k in spider.request_res_route:
                if k==request.url or 'type' in spider.request_res_route[k] and spider.request_res_route[k]['type']=='starts' and request.url.startswith(k) or isinstance(k, re.Pattern) and re.match(k,request.url):
                    spider.logger.info('request_res_route_key: %s | %s => %s => %s' % (k, spider.request_res_route_key, spider.request_res_route[k], request.url))
                    spider.request_res_route_key = k #注意： spider成员存在线程安全！
#                    spider.request_res_route_url = request.url #注意： spider成员存在线程安全！
                    request.meta['request_res_route_key'] = k
                    break
#            else:
#                spider.request_res_route_key = None
##                spider.request_res_route_url = None
#        else:
#            spider.request_res_route_key = None
##            spider.request_res_route_url = None

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
            
        #phantomjs、HeadlessChrome（ppeteer、chromedriver）、HeadlessFirefox
        # Selenium
#        spider.request_res_route[spider.request_res_route_key]['selenium'] = 'PhantomJS'
        if spider.request_res_route_key and spider.request_res_route and 'selenium' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['selenium']:
            self.use_selenium = True
#            if not self.browser:
            if True:
                if spider.request_res_route[spider.request_res_route_key]['selenium']=='PhantomJS': #2.1.1后暂停维护
                    #无窗
                    self.browser = webdriver.PhantomJS(executable_path=spider.settings['PHANTOMJS'],service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
                elif spider.request_res_route[spider.request_res_route_key]['selenium']=='chromedriver':
                    #有窗
                    self.browser = webdriver.Chrome(spider.settings['CHROMEDRIVER'])
                elif spider.request_res_route[spider.request_res_route_key]['selenium']=='ppeteer':
                    body,localstorages,cookies,status,headers = asyncio.get_event_loop().run_until_complete(ppeteer(request.url))
                    self.browser= {"localstorages": localstorages, "cookies": cookies}
                    self.use_browser = 'ppeteer'
                    return HtmlResponse(url=request.url, body=body, request=request, encoding='utf-8', status=status, headers=headers)
                elif spider.request_res_route[spider.request_res_route_key]['selenium'] == 'pyppeteer':
                    return BrowserRequest(request.url, callback=spider.parse, dont_filter=True, meta=request.meta)
                else:
                    #无窗
                    self.browser = webdriver.PhantomJS(executable_path=spider.settings['PHANTOMJS'],service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
                #self.use_selenium = True
        else:
            self.use_selenium = False
        if self.use_selenium:
            try:
                self.browser.get(request.url)
                self.wait = WebDriverWait(self.browser, 25)
#                time.sleep(5)
                localstorages = self.browser.execute_script('var l = {}; for(var i=0; i<localStorage.length; i++){ l[localStorage.key(i)] = localStorage.getItem(localStorage.key(i)); } return l;')
                cookies = self.browser.execute_script('return document.cookie;')
                body = self.browser.page_source
                har = json.loads(self.browser.get_log('har')[0]['message'])
                headers = OrderedDict(sorted([(header["name"], header["value"]) for header in har['log']['entries'][0]['response']["headers"]], key = lambda x: x[0]))
                status = (har['log']['entries'][0]['response']["status"], str(har['log']['entries'][0]['response']["statusText"]))
                if hasattr(self.browser, 'close'):
                    self.browser.close()
                self.browser = {"localstorages": localstorages, "cookies": cookies}
                return HtmlResponse(url=request.url, body=body, request=request, encoding='utf-8', status=200)#, headers=headers
            except Exception as e:
                return HtmlResponse(url=request.url, status=500, request=request)
            
            
            
            
            
            
import asyncio
import logging
from typing import Optional

import pyppeteer
from pyppeteer.browser import Browser
from scrapy.settings import Settings
from twisted.internet.defer import Deferred

from scrapy_pyppeteer import BrowserRequest
from scrapy_pyppeteer import BrowserResponse

from scrapy.http.response import Response


logger = logging.getLogger(__name__)


class ScrapyPyppeteerDownloaderMiddleware(object):
    """ Handles launching browser tabs, acts as a downloader.
    Probably eventually this should be moved to scrapy core as a downloader.
    """
    def __init__(self, settings: Settings):
        self._browser: Optional[Browser] = None
        self._launch_options = settings.getdict('PYPPETEER_LAUNCH') or {}
        self.browser = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_response(self, request, response, spider):
        if self.browser is not None:
            response.browser = self.browser
        return response

    def process_request(self, request, spider):
        if isinstance(request, BrowserRequest):
            return _aio_as_deferred(self.process_browser_request(request))
        else:
            return request

    async def process_browser_request(self, request: BrowserRequest):
        if self._browser is None:
            self._browser = await pyppeteer.launch(**self._launch_options)
        page = await self._browser.newPage()
        n_tabs = _n_browser_tabs(self._browser)
        logger.debug(f'{n_tabs} tabs open')
        if request.is_blank:
            url = request.url
            return BrowserResponse(url=url, browser_tab=page)
        else:
            response = await page.goto(request.url)
            url = page.url
            # TODO set status and headers
            body = await page.content()
            body = body.encode('UTF-8')
            localstorages = await page.evaluate('''() => { var l = {}; for(var i=0; i<localStorage.length; i++){ l[localStorage.key(i)] = localStorage.getItem(localStorage.key(i)); } return l; }''')
            cookies = await page.cookies()
            await page.close()#todo:
            self.browser= {"localstorages": localstorages, "cookies": cookies}
#            response = BrowserResponse(url=url, browser_tab=page, body=body, status=response.status)#todo: , headers=response.headers
            response = HtmlResponse(url=url, body=body, encoding='utf-8', status=200)#todo:同步？异步？   , headers=headers
            return response


def _n_browser_tabs(browser: Browser) -> int:
    """ A quick way to get the number of browser tabs.
    """
    n_tabs = 0
    for context in browser.browserContexts:
        for target in context.targets():
            if target.type == 'page':
                n_tabs += 1
    return n_tabs


def _aio_as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))
            
            





