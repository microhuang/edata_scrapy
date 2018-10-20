# 通用爬虫框架

### 特点
```
1、支持"业务"属性（meta）在request链路中保持传递；
2、start在每一个request后处理，而不是"整轮"后处理，业务实效性得到保证；
3、架构优化，具体见下图
```

### 架构
```
                                        -----> (response) -> (item_res_route) -> Item -> 入库
           （编排/调度）               |
(User) => task => start(meta) -> request -> (response) -> (request_res_route) -> Next
            ^       ^              ^                                            | | |
            |       |              |____________________________________________| | |
            |       |                                                      url    | |
         (queue)    |_____________________________________________________________| |
            |                                                             sigle     |
            |_______________________________________________________________________|
                                                                           url

task（DB）: 任务池，编排规则由完全独立的业务系统定义

start（queue）: 任务入口
request（queue）: 任务执行

item_res_route: response to item 路由
request_res_route: response to url 路由

Item: 内容提取逻辑
Next: url头组装逻辑、next request url提取逻辑、next task url提取逻辑
```

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


