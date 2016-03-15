import csv
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
import time
from datetime import date
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MystocksPipeline(object):

	def process_item(self, item, spider):

		today = time.strftime("%Y-%m-%d")

		name = item['code']
		filename = "%s.csv" % name


		self.csvwriter = csv.writer(open(../../base, 'a'),lineterminator='\n')
		item['volume'] = item['volume'].replace('M','')
		item['adjustedPrice'] = item['adjustedPrice'].replace('-','0')
		item['percentChange'] = item['percentChange'].replace('-','0')
		item['change'] = item['change'].replace('-','0')



	
		self.csvwriter.writerow([item['date'], item['previous'], item['day_high'], item['day_low'], item['last12_high'], item['last12_low'], item['price'], item['change'], item['percentChange'], item['volume'], item['adjustedPrice']])

		return item






