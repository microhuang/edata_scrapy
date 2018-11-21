# -*- coding: utf-8 -*-


from scrapy.http import Request,FormRequest

import re, time

from urllib.parse import urlparse,parse_qs,urlunparse,urlencode,quote,unquote

import json

from scrapy import Selector

def url_query_string_update(url,key,value):
    up = list(urlparse(url))
    pq = parse_qs(up[4])
    
#    if key in pq and pq[key][0]:
#        pq[key][0] = str(int(pq[key][0])+1)
#    else:
#        pq[key][0] = '2'
        
    if key not in pq:
        pq[key] = [value]
    else:
        pq[key][0] = value
    up[4] = urlencode(pq, True)
    url = urlunparse(up)
    return url


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
    
#https://www.jobcn.com/search/result_servlet.ujson?
class JobcnSearchJsonNext(object):
    @staticmethod
    def extract(response,spider):
        response_url = response.url
        up = list(urlparse(response_url))
#        domain = up[0]+'://'+up[1]
        
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
#        return None
        if len(rows)>0:
#            for row in rows:
#                #详情
#                next_url = domain+"/position/detail.xhtml?redirect=0&posId="+row['posId']+"&comId="+row['comId']+"&s=search/advanced&acType=1"
#                dont_filter = False
#                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
#                yield req
            #翻页
            pq = parse_qs(up[4])
            if 'p.pageNo' in pq and pq['p.pageNo'][0]:
#                pq['p.pageNo'][0] = str(int(pq['p.pageNo'][0])+1)
                next_url = url_query_string_update(response_url, 'p.pageNo', str(int(pq['p.pageNo'][0])+1))
            else:
#                pq['p.pageNo'][0] = '2'
                next_url = url_query_string_update(response_url, 'p.pageNo', '2')
#            up[4] = urlencode(pq, True)
#            next_url = urlunparse(up)
            dont_filter = False
            req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
            yield req
        
class JobcnSearchNext(object):
    @staticmethod
    def extract(response,spider):
#        ['<div class="item_box" data-applieddate="" group="0" ga=\'{posId:"3819846",bidding:"false",detailId:0,fromKeyWord:"",fromArea:"",type:1}\' actype="6" onclick="_jsp.Grid.Detail.toggle(0,\'3819846\',this,event)" onmousedown="_jsp.Grid.Detail.mouseDown()">\n          <div class="item_job"> <a class="job_check " data-value="3819846"></a>\n            <div class="job_main  ">\n              <div class="job_title"> <span class="hide mapIcon mComId460308"></span>\n                <h4 class="job_name"><a href="/position/detail.xhtml?redirect=0&amp;posId=3819846&amp;comId=460308&amp;s=search/advanced&amp;acType=1" target="_blank">模具设计师</a>\n                  \n                        <!-- 新增急招-->\n                  \n                </h4>\n              </div>\n              \n              <div class="job_info "> <a href="/position/home.xhtml?redirect=0&amp;comId=460308&amp;s=search/advanced&amp;acType=2" target="_blank" title="钜佳合成金属制品（深圳）有限公司">钜佳合成金属制品（深圳）有限公司</a>\n                 <a class="certificate_icon2" style="cursor:pointer;" title="证照已提交" href="/position/certificate.xhtml?comId=460308" target="_blank">\xa0</a> <a href="/position/album.xhtml?redirect=0&amp;comId=460308&amp;s=search/advanced" target="_blank" class="pic_com" comid="460308" comname="钜佳合成金属制品（深圳）有限公司" jobs="模具设计师" title="企业图片展示">\xa0</a> \n                <p> <span>|</span>\n                  深圳<span>|</span>中专以上<span>|</span>3年经验<span>|</span><span style="font-weight:bold;color:#5B6A84">¥5-7K</span><span>|</span>\n                  <span class="view-pos-date">02分钟前刷新</span>\n                  <span class="view-insert-date">02分钟前刷新</span>\n                  \n                  </p>\n              </div>\n              <div id="pos_desc_0">\n                <div id="job_desc_0" class="job_desc " title="点击查看详情"> 要求：1.性别不限，2名，20-40周岁，中专及以上学历；      \r\n      2.三年以上五金连续模具设计及制作相关工作经验；\r\n      3.熟悉操作CAD、Solidworks、quickpres、ERP、word、Excel等软件；\r\n      4.对数字敏感、责任心强、有良好的沟通能力、有一定的抗压...\n                </div>\n                <div class="job_operate" data-posid="3819846">\n                \t<a href="javascript:;" class="jobcn_apply" actype="4" onclick="jobcn.Person.Position.apply(\'3819846\');">应聘</a>\n                \t<a href="javascript:;" data-isadd="true" id="desc_collect_3819846" class="jobcn_collect collect_3819846" actype="5" onclick="jobcn.Search.Position.MyFavourite.add(\'3819846\', this, event)"><span class="text">收藏</span></a>\n                \t<span class="open">点击任意位置可展开<i></i></span> </div>\n              </div>\n              <div id="pos_detail_0" class="job_detail"> </div>\n            </div>\n          </div>\n        </div>']
#        print(4444444,response.xpath('//*[@id="result_data"]/div/div[1]').extract())
#        return None
    
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
#curl 'https://www.jobcn.com/search/result_servlet.ujson?s=search%2Ftop' \
#-XPOST \
#-H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
#-H 'Accept: application/json, text/javascript, */*; q=0.01' \
#-H 'Host: www.jobcn.com' \
#-H 'Accept-Language: zh-cn' \
#-H 'Accept-Encoding: br, gzip, deflate' \
#-H 'Origin: https://www.jobcn.com' \
#-H 'Referer: https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=solidwork%3B+solidworks%3B+sw%3B+%BB%FA%D0%B5%B9%A4%B3%CC%CA%A6%3B+%BD%E1%B9%B9%B9%A4%B3%CC%CA%A6%3B+%C9%E8%BC%C6%B9%A4%B3%CC%CA%A6%3B+%CF%EE%C4%BF%BE%AD%C0%ED&p.keywordType=2&p.workLocation=' \
#-H 'Connection: keep-alive' \
#-H 'Content-Length: 5646' \
#-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15' \
#-H 'Cookie: Hm_lpvt_8180e13f3ce10ef1c58778a9785ec8fc=1542613364; Hm_lvt_8180e13f3ce10ef1c58778a9785ec8fc=1542295053; __utma=75346313.672548434.1542295053.1542605389.1542600826.5; __utmb=75346313.35.6.1542613235476; __utmc=75346313; __utmv=75346313.|2=member=IM=1; __utmz=75346313.1542295053.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); searchCondition=c29saWR3b3JrOyBzb2xpZHdvcmtzOyBzdzsgu%2FrQtbmks8zKpjsgveG5ubmks8zKpjsgyei8xrmks8zKpjsgz%2B7Ev76twO0%3D--2----------366-10-70--11-3-15-40-100000; __utmt=1; c_pos_viewhis=2944912%2C4005007%2C3926670%2C2039133%2C3995839; c_pos_viewhis_syn=false; hlkw=; JCNID=jcnp60179331678804c93d79' \
#-H 'X-Requested-With: XMLHttpRequest' \
#--data 'p.querySwitch=0&p.searchSource=default&p.keyword=solidwork%3B+solidworks%3B+sw%3B+%E6%9C%BA%E6%A2%B0%E5%B7%A5%E7%A8%8B%E5%B8%88%3B+%E7%BB%93%E6%9E%84%E5%B7%A5%E7%A8%8B%E5%B8%88%3B+%E8%AE%BE%E8%AE%A1%E5%B7%A5%E7%A8%8B%E5%B8%88%3B+%E9%A1%B9%E7%9B%AE%E7%BB%8F%E7%90%86&p.keyword2=&p.keywordType=2&p.pageNo=255&p.pageSize=40&p.sortBy=postdate&p.statistics=false&p.totalRow=1000&p.cachePageNo=1&p.jobnature=15&p.comProperity=0&p.JobLocationTown=&p.salary=-1&p.highSalary=100000&p.salarySearchType=1&p.includeNeg=1&p.inputSalary=-1&p.workYear1=-1&p.workYear2=11&p.degreeId1=10&p.degreeId2=70&p.posPostDate=366&p.otherFlag=3'
#            https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=solidwork%3B+solidworks%3B+sw%3B+%BB%FA%D0%B5%B9%A4%B3%CC%CA%A6%3B+%BD%E1%B9%B9%B9%A4%B3%CC%CA%A6%3B+%C9%E8%BC%C6%B9%A4%B3%CC%CA%A6%3B+%CF%EE%C4%BF%BE%AD%C0%ED&p.keywordType=2&p.workLocation=
#            https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=solidwork%3B+solidworks%3B+sw%3B+%BB%FA%D0%B5%B9%A4%B3%CC%CA%A6%3B+%BD%E1%B9%B9%B9%A4%B3%CC%CA%A6%3B+%C9%E8%BC%C6%B9%A4%B3%CC%CA%A6%3B+%CF%EE%C4%BF%BE%AD%C0%ED&p.keywordType=2&p.workLocation=#P2
#            https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=solidwork%3B+solidworks%3B+sw%3B+%BB%FA%D0%B5%B9%A4%B3%CC%CA%A6%3B+%BD%E1%B9%B9%B9%A4%B3%CC%CA%A6%3B+%C9%E8%BC%C6%B9%A4%B3%CC%CA%A6%3B+%CF%EE%C4%BF%BE%AD%C0%ED&p.keywordType=2&p.workLocation=#P255
            #todo
#        next_url = "http://localhost:8081/"
#        dont_filter = False
#        req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
#        yield req
    

    
#http://www.job5156.com/s/result/kt0_kw-
class Job5156SearchNext(object):
    @staticmethod
    def extract(response,spider):
#        response_body = ''
#        try:
#            response_body = str(response.body, encoding='utf-8')
#        except:
#            try:
#                response_body = str(response.body, encoding='gbk')
#            except:
#                response_body = str(response.body, encoding='gb2312')
#            pass
        
        selectors = response.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li')
        if selectors:
            dont_filter = False
            r = re.match(r".*\/kt0_kw\-(.*)\/.*",response.url)
            if r:
                k = r.group(1)
                next_url = "http://www.job5156.com/s/result/ajax.json?keyword=zhanweifu&keywordType=0&posTypeList=&locationList=&taoLabelList=&degreeFrom=&propertyList=&industryList=&sortBy=0&urgentFlag=&maxSalary=&salary=&workyearFrom=&workyearTo=&degreeTo=&pageNo=2"
                next_url = url_query_string_update(next_url, 'keyword', unquote(k))
                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
                yield req
            
class Job5156SearchMoreNext(object):
    @staticmethod
    def extract(response,spider):
        rows = json.loads(response.body)['page']['items']
        if rows:
            dont_filter = False
            next_url = response.url
            next_url = url_query_string_update(next_url, 'pageNo', int(parse_qs(response.url)['pageNo'][0])+1)
            req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
            yield req
    
#https://search.51job.com/list/000000,000000,0000,00,9,99,%25E6%259C%25BA%25E6%25A2%25B0%25E5%25B7%25A5%25E7%25A8%258B%25E5%25B8%2588,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=
#https://search.51job.com/list/080200,000000,0000,00,9,99,%25E6%259C%25BA%25E6%25A2%25B0%25E5%25B7%25A5%25E7%25A8%258B%25E5%25B8%2588,2,3.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=
class Job51SearchNext(object):
    @staticmethod
    def extract(response,spider):
        selectors = response.xpath('//*[@id="resultList"]/div')
        if selectors:
            page = re.match(r'(?P<b>.*,)(?P<pageNo>[\d]+)(?P<e>.html\?.*)', response.url).group("pageNo")
            page = str(int(page)+1)
            next_url = re.sub(r'(?P<b>.*,)(?P<pageNo>[\d]+)(?P<e>.html\?.*)', '\g<b>'+page+'\g<e>', response.url)
            dont_filter = False
            req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
            yield req
    
    
#http://s.cjol.com/service/joblistjson.aspx?KeywordType=3&RecentSelected=43&KeyWord=%E6%9C%BA%E6%A2%B0%E5%B7%A5%E7%A8%8B%E5%B8%88&SearchType=1&ListType=2&page=1
class CjolSearchNext(object):
    @staticmethod
    def extract(response,spider):
        next_url = response.url
        html = json.loads(response.body)['JobListHtml']
        if html:
            selector = Selector(text=html)
            companys = selector.xpath('//*[@id="searchlist"]/ul/li[3]/a/text()')
            if companys:
                next_url = url_query_string_update(next_url, 'page', int(parse_qs(response.url)['page'][0])+1)
#                print(333333, next_url)
                dont_filter = False
                req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
                yield req
    
  
#https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=%E6%9C%BA%E6%A2%B0%E5%B7%A5%E7%A8%8B%E5%B8%88&kt=3&_v=0.02290825&x-zp-page-request-id=24b0a34d0b2e40a3a3e199b2822e96f5-1542773033547-230569
#https://fe-api.zhaopin.com/c/i/sou?start=60&pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=%E6%9C%BA%E6%A2%B0%E5%B7%A5%E7%A8%8B%E5%B8%88&kt=3&_v=0.02290825&x-zp-page-request-id=24b0a34d0b2e40a3a3e199b2822e96f5-1542773033547-230569
class ZhaopinSearchJsonNext(object):
    @staticmethod
    def extract(response,spider):
        rows = json.loads(response.body)['data']['results']
        if rows:
            next_url = response.url
            if 'start' not in parse_qs(response.url):
                start=60
            else:
                start=int(parse_qs(response.url)['start'][0])+60
            next_url = url_query_string_update(next_url, 'start', start)
            dont_filter = False
            req = Request(url=next_url, callback=spider.parse, dont_filter=dont_filter)
            yield req
        
        
    