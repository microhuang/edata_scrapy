# -*- coding: utf-8 -*-


from scrapy.http import Request,FormRequest

import re, time

from urllib.parse import urlparse


class LocalNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "http://localhost:8081/"
        dont_filter = False
        req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
        yield req
        #return {'url':next_url,'dont_filter':dont_filter}
    
#百度url页面的next提取逻辑
class BaiduNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "https://www.baidu.com/"
        dont_filter = False
        req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
        yield req
        #return {'url':next_url,'dont_filter':dont_filter}

class SinaNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "http://www.sina.com.cn/"
        dont_filter = False
        req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
        yield req
        #return {'url':next_url,'dont_filter':dont_filter}

# www.baidu.com/s?wd=\w
class BaiduListNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        next_url = None
        dont_filter = True
        domain='http://www.baidu.com'
        if response.url.startswith('https://www.baidu.com/'):
            domain='https://www.baidu.com'
        #todo
        #next_urls = re.findall(r'<a .*?href="(.*?)"',str(response.body, encoding='utf-8'))
        rsp = ''
        try:
            response_body = str(response.body, encoding='utf-8')
        except:
            try:
                response_body = str(response.body, encoding='gbk')
            except:
                response_body = str(response.body, encoding='gb2312')
            pass
        # '<a href="abc">aaa</a><a href="efg">bbb</a>' => ['abc', 'efg']
        #next_urls = re.finditer(r'<a .*?href=["|\'](.*?)["|\']',response_body)
        # '<a href="abc">aaa</a><a href="efg">bbb</a>' => [('abc', 'aaa'), ('efg', 'bbb')]
        next_urls = re.finditer(r'<a .*?href="(.*?)".*?>(.*?)</a>', response_body)
        
        #作为next处理：静态list
        for url in next_urls:
            next_url = url.group(1)
            next_a = url.group(2)
            if 'javascript:;'==next_url or "javascript"==next_url or next_url.startswith('#'):
                continue
            if next_url.startswith('/'):
                next_url=domain+next_url
            #if next_url.startswith('http://www.baidu.com/link?url'):
            #    print(next_url)

            #作为start处理：动态搜索/如果不做为start下次重写搜索不一定有这个
            if spider.request_res_route_key in spider.request_res_route and 'hasStart' in spider.request_res_route[spider.request_res_route_key] and spider.request_res_route[spider.request_res_route_key]['hasStart']:
                #is start_url
                #todo: queue
                self.logger.info(response.meta)
                spider.server.lpush("%(name)s:next_urls"%{'name':spider.name},{'url':next_url,'task':response.meta['task'],'start':'yyyy','timestamp':int(time.time())})
                #or todo: db
                #or todo: api
                pass

            #这是一个demo，进入结果页，只对当前页面“百度搜索结果”中的link?链接进行深入爬取
            if next_url.startswith('http://www.baidu.com/link?url='):
                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
                #req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter, meta=response.meta)
                yield req

            #进入下一页
            if next_a=='下一页':
                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
                yield req

class WeiboPassportNext(object):
    @staticmethod
    def extract(response,spider):
        #todo
        pass

class GithubLoginNext(object):
    @staticmethod
    def extract(response,spider):
        pass
    
    @staticmethod
    def login(request, response, spider):
        request = FormRequest.from_response(response=response,
                                            meta={'cookiejar': response.meta['cookiejar'] if response and hasattr(response, 'meta') and 'cookiejar' in response.meta else None},
                                            #headers=self.post_headers,
                                            formdata={
                                                #"utf8": utf8,
                                                #"authenticity_token": authenticity_token,
                                                "login": spider.request_res_route[spider.request_res_route_key]['LoginUser'],
                                                "password": spider.request_res_route[spider.request_res_route_key]['LoginPass'] if spider.request_res_route[spider.request_res_route_key]['LoginPass'] else '',
                                                #"commit": commit
                                            },
                                            callback=request.callback,
                                            dont_filter=request.dont_filter)
        return request


class JobcnSearchNext(object):
    @staticmethod
    def extract(response,spider):
        up = urlparse(response.url)
        domain = up.scheme+'://'+up.netloc
        response_body = ''
        try:
            response_body = str(response.body, encoding='utf-8')
        except:
            try:
                response_body = str(response.body, encoding='gbk')
            except:
                response_body = str(response.body, encoding='gb2312')
            pass
        #提取所有a链接
        next_urls = re.finditer(r'<a .*?href="(.*?)".*?>(.*?)</a>', response_body)
        for url in next_urls:
            next_url = url.group(1)
            next_a = url.group(2)
            #岗位详情
            if next_url.startswith('/position/detail.xhtml?'):
                dont_filter = False
                req = Request(url=domain+next_url, callback=spider.parse, dont_filter=dont_filter)
                yield req
            #列表翻页
            #todo
#        next_url = "http://localhost:8081/"
#        dont_filter = False
#        req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
#        yield req
    
    


