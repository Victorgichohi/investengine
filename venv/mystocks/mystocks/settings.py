# -*- coding: utf-8 -*-

# Scrapy settings for mystocks project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mystocks'

SPIDER_MODULES = ['mystocks.spiders']
NEWSPIDER_MODULE = 'mystocks.spiders'
ITEM_PIPELINES = {'mystocks.pipelines.MystocksPipeline': 300 }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mystocks (+http://www.yourdomain.com)'

