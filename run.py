#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# python3 ./run.py
# or
# ./run.py


#from tutorial.spiders.edata import EdataSpider
##from tutorial.spiders.github import GithubLoginSpider
#
#import scrapy
#from scrapy.crawler import CrawlerProcess
#from scrapy.crawler import CrawlerRunner
#from scrapy.utils.project import get_project_settings
# 
#process = CrawlerProcess(get_project_settings())
# 
#process.crawl(EdataSpider)
##process.crawl(GithubLoginSpider)
#
#process.start()





# python3 -O ./run.py crawl edata
# or
# ./run.py -O crawl edata


## Install twisted asyncio loop
#
##import importlib
##import sys
##if 'twisted.internet.reactor' in sys.modules:
##    del sys.modules['twisted.internet.reactor']
#def _install_asyncio_reactor():
#    try:
#        import asyncio
#        from twisted.internet import asyncioreactor
#    except ImportError:
#        pass
#    else:
#        # FIXME maybe we don't need this? Adapted from pytest_twisted
#        from twisted.internet.error import ReactorAlreadyInstalledError
#        try:
#            asyncioreactor.install(asyncio.get_event_loop())
#        except ReactorAlreadyInstalledError:
#            import twisted.internet.reactor
#            if not isinstance(twisted.internet.reactor,
#                              asyncioreactor.AsyncioSelectorReactor):
#                raise
#_install_asyncio_reactor()
##from twisted.internet import reactor
##importlib.reload(reactor)
#del _install_asyncio_reactor


#import framework.bootstrap._hook


#from scrapy.cmdline import execute
#from scrapy.utils.python import garbage_collect



#def _aio_as_deferred(f):
#    return Deferred.fromFuture(asyncio.ensure_future(f))
#def _iterate_spider_output(result):
#    print(66666666666666)
#    # FIXME check if changes need to be made here or just when calling from  scrapy.core.scraper
#    # TODO probably add other cases from ensure_future here
#    # FIXME hmm which is the proper check for async def coroutines?
#    if asyncio is not None and hasattr(result, '__await__') and asyncio.coroutines.iscoroutine(result):
#        d = _aio_as_deferred(result)
#        d.addCallback(iterate_spider_output)
#        return d
#    elif hasattr(inspect, 'isasyncgen') and inspect.isasyncgen(result):
#        d = _aio_as_deferred(collect_asyncgen(result))
#        d.addCallback(iterate_spider_output)
#        return d
#    else:
#        return arg_to_iter(result)









#def scrapy():
#    try:
#        execute()
#    finally:
#        # Twisted prints errors in DebugInfo.__del__, but PyPy does not run gc.collect()
#        # on exit: http://doc.pypy.org/en/latest/cpython_differences.html?highlight=gc.collect#differences-related-to-garbage-collection-strategies
#        garbage_collect()



import os
import sys

 
current_dir = os.path.dirname(os.path.realpath(__file__))
boot_dir = os.path.join(current_dir, 'framework/bootstrap')

 
def main():
    args = sys.argv[1:]
    args.insert(0, '_scrapy.py')
    if not __debug__:
        args.insert(0, '-O')
    os.environ['PYTHONPATH'] = boot_dir
    # 执行后面的 python 程序命令
    # sys.executable 是 python 解释器程序的绝对路径 ``which python``
    # >>> sys.executable
    # '/usr/local/var/pyenv/versions/3.5.1/bin/python3.5'
#    print(args)
#    return
    os.execl(sys.executable, sys.executable, *args)
 
if __name__ == '__main__':
    main()