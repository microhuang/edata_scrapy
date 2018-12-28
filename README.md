# 分布式通用爬虫框架

### 特点
```
1、优先级+算力分配；
2、支持"业务"属性（meta）在request链路中保持传递；
3、start在每一个request后处理，而不是"整轮"后处理，业务实效性得到保证；
4、集成浏览器环境；
5、异步编程支持；
6、架构优化，具体见下图
```

### 架构
```
                                                                                     -------> (item_res_route) -> Item -> pipeline -> 入库
           （编排/调度）                                                              |
(User) => task => start(meta) -> request -> (request_res_route->middlewares) -> (response) -> (request_res_route) -> Next
            ^       ^              ^                                                                                | | |
            |       |              |________________________________________________________________________________| | |
            |       |                                                                             url(request)        | |
         (queue)    |_________________________________________________________________________________________________| |
            |                                                                                   sigle(item_scraped)     |
            |___________________________________________________________________________________________________________|
                                                                                                  url(task)

task（DB）: 任务池，编排规则由完全独立的业务系统定义

start（queue）: 任务入口
request（queue）: 任务执行

item_res_route: response to item 路由
request_res_route: response to url 路由

Item: 内容提取逻辑
Next: url头组装逻辑(包括IP/tor代理等策略)、next request url提取逻辑、next task url提取逻辑
```

### python37 -O -m scrapy crawl edata

```
middlewares控制请求头：ua、login、ip/tor/proxy、rate在此。
Next定义从当前request进入下一个request，否则停止。需返回Request类型生成器。
Item定义保存格式。
middlewares、Next、Item所需配置统一来自配置中心。
```

### DEMO - 任务1微博股市话题、任务2csdn开源文章：
```
lpush edata:start_urls "https://www.baidu.com/s?wd=股市 site:weibo.cn"
lpush edata:start_urls "https://www.baidu.com/s?wd=开源 site:blog.csdn.net"
```


# 分布式并行任务框架

### 任务类型：
```
1、指定单点（机）任务 -- 只在指定节点运行、任务实现者承担节点失败风险
2、随机单点（机）任务 -- 任意节点运行
3、集群调度任务 -- 所有节点同时运行、任务实现者承担重复计算责任
4、集群运行任务 -- 所有节点并行分片运行
5、DAG图式任务(airflow) -- 依赖任务完成才可运行
```

