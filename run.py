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



# python3 ./run.py crawl edata
# or
# ./run.py crawl edata


# Install twisted asyncio loop

#import importlib
#import sys
#if 'twisted.internet.reactor' in sys.modules:
#    del sys.modules['twisted.internet.reactor']
def _install_asyncio_reactor():
    try:
        import asyncio
        from twisted.internet import asyncioreactor
    except ImportError:
        pass
    else:
        # FIXME maybe we don't need this? Adapted from pytest_twisted
        from twisted.internet.error import ReactorAlreadyInstalledError
        try:
            asyncioreactor.install(asyncio.get_event_loop())
        except ReactorAlreadyInstalledError:
            import twisted.internet.reactor
            if not isinstance(twisted.internet.reactor,
                              asyncioreactor.AsyncioSelectorReactor):
                raise
_install_asyncio_reactor()
#from twisted.internet import reactor
#importlib.reload(reactor)
del _install_asyncio_reactor


from scrapy.cmdline import execute
from scrapy.utils.python import garbage_collect

if __name__ == '__main__':
    try:
        execute()
    finally:
        # Twisted prints errors in DebugInfo.__del__, but PyPy does not run gc.collect()
        # on exit: http://doc.pypy.org/en/latest/cpython_differences.html?highlight=gc.collect#differences-related-to-garbage-collection-strategies
        garbage_collect()
