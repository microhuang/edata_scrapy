# -*- coding: utf-8 -*-

import functools
import importlib
import sys


#def func_wrapper(func):
#  @functools.wraps(func)
#  def wrapper(*args, **kwargs):
#    import time
#    print('start func')
#    start = time.time()
#    result = func(*args, **kwargs)
#    end = time.time()
#    print('spent {}s'.format(end - start))
#    return result
#  return wrapper

def iterate_spider_output_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import asyncio
        import inspect
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
  
  
class MetaPathFinder:
  def find_module(self, fullname, path=None):
#    print('find_module %s, path %s' % (fullname, path))
#    if fullname=='scrapy.core.scraper':
#        print(22222222222)
    if fullname in _hook_modules.keys():
      return MetaPathLoader()
  
class MetaPathLoader:
  def load_module(self, fullname):
#    print('load_module {}'.format(fullname))
    # ``sys.modules`` 中保存的是已经导入过的 module
    if fullname in sys.modules:
      return sys.modules[fullname]
    # 先从 sys.meta_path 中删除自定义的 finder
    # 防止下面执行 import_module 的时候再次触发此 finder
    # 从而出现递归调用的问题
    finder = sys.meta_path.pop(0)
    # 导入 module
    module = importlib.import_module(fullname)
#    print(1111111,  module, _hook_modules[fullname][0],  module, _hook_modules[fullname][1])
    module_hook(fullname, module, _hook_modules[fullname][0], _hook_modules[fullname][1])
    sys.meta_path.insert(0, finder)
    return module
  
def _hook():
    sys.meta_path.insert(0, MetaPathFinder())
    
_hook()
del _hook
  
def module_hook(fullname, module, func, wrapper):
#  print(1111, fullname, module)
  if fullname in _hook_modules.keys():
#    print(3333333, func, getattr(module, func), wrapper)
    setattr(module, func, wrapper(getattr(module, func)))#module.sleep
#    setattr(module, func, getattr(module, func))#module.sleep
#    print(4444444, getattr(module, func))
#    module.sleep = wrapper(module.sleep)
  


