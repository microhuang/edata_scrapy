# -*- coding: utf-8 -*-

from scrapy.cmdline import execute
from scrapy.utils.python import garbage_collect


def scrapy():
    try:
        execute()
    finally:
        # Twisted prints errors in DebugInfo.__del__, but PyPy does not run gc.collect()
        # on exit: http://doc.pypy.org/en/latest/cpython_differences.html?highlight=gc.collect#differences-related-to-garbage-collection-strategies
        garbage_collect()
  

if __name__ == '__main__':
    scrapy()