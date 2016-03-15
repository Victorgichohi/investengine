# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MystocksItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	date = scrapy.Field()
	code = scrapy.Field()
	name = scrapy.Field()
	last12_low = scrapy.Field()
	last12_high = scrapy.Field()
	day_low = scrapy.Field()
	day_high = scrapy.Field()
	price = scrapy.Field()
	previous = scrapy.Field()
	change = scrapy.Field()
	percentChange = scrapy.Field()
	volume = scrapy.Field()
	adjustedPrice = scrapy.Field()
	pass

