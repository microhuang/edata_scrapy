#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# python3 ./run.py
# or
# ./run.py


from tutorial.spiders.edata import EdataSpider
#from tutorial.spiders.github import GithubLoginSpider

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
 
process = CrawlerProcess(get_project_settings())
 
process.crawl(EdataSpider)
#process.crawl(GithubLoginSpider)

process.start()






