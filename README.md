# 通用爬虫框架

### scrapy crawl edata

```
middlewares控制请求头：ua、login、ip、rate在此。
Next定义从当前request进入下一个request，否则停止。需返回Request类型生成器。
Item定义保存格式。
middlewares、Next、Item所需配置统一来自配置中心。
```

### DEMO - 从百度结果页到csdn：
```
#lpush edata:start_urls https://www.baidu.com/s?wd=abc%20site%3Ablog.csdn.net
lpush edata:start_urls "https://www.baidu.com/s?wd=abc site:blog.csdn.net"
```


