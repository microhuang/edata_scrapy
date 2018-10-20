# -*- coding: utf-8 -*-


from scrapy.http import Request

import re, time


class LocalNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "http://localhost:8081/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}
    
#百度url页面的next提取逻辑
class BaiduNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "https://www.baidu.com/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}

class SinaNext(object):
    #必须由yield Request返回
    @staticmethod
    def extract(response,spider):
        #todo
        next_url = "http://www.sina.com.cn/"
        dont_filter = False
        return {'url':next_url,'dont_filter':dont_filter}

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
        next_urls = re.finditer(r'<a .*?href="(.*?)"',response_body)
        
        #作为next处理：静态list
        for next_url in next_urls:
            next_url = next_url.group(1)
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
                spider.server.lpush("%(name)s:next_urls"%{'name':spider.name},{'url':next_url,'start':'xxxx','timestamp':int(time.time())})
                #or todo: db
                #or todo: api
                pass
        
            #这是一个demo，只对当前页面“百度搜索结果”中的link?链接进行深入爬取
            if next_url.startswith('http://www.baidu.com/link?url='):
                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
                yield req

