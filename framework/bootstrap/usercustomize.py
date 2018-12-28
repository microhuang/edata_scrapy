# -*- coding: utf-8 -*-

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

#安装reactor
import _reactor

#hook scrapy.utils.spider
import _import

#import _scrapy

#scrapy()

#print('this is usercustomize')



#scrapy.utils.spider.iterate_spider_output => iterate_spider_output_wrapper
def iterate_spider_output_wrapper(func):
    import functools
    import asyncio
    import inspect
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = args[0]
        if asyncio is not None and hasattr(result, '__await__') and asyncio.coroutines.iscoroutine(result):
            d = _aio_as_deferred(result)
            d.addCallback(iterate_spider_output)
            return d
        elif hasattr(inspect, 'isasyncgen') and inspect.isasyncgen(result):
            d = _aio_as_deferred(collect_asyncgen(result))
            d.addCallback(iterate_spider_output)
            return d
        else:
            return func(*args, **kwargs)
    return wrapper
  
  
#_hook_modules = {'hello':('sleep',func_wrapper),'tutorial.spiders.hello':('sleep',func_wrapper),'scrapy.utils.spider':('iterate_spider_output',iterate_spider_output_wrapper)}
_hook_modules = {'scrapy.utils.spider':('iterate_spider_output',iterate_spider_output_wrapper)}
    
_import._hook(_hook_modules)
del _import._hook