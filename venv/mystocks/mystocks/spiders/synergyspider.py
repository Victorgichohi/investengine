import scrapy
from mystocks.items import MystocksItem
from scrapy.selector import Selector
import datetime

class Synergyspider(scrapy.Spider):
	name = "synergyspider"
	allowed_domains = ["http://live.mystocks.co.ke/price_list/"]
	

	def parse(self, response):

		sel = Selector(response)

		
		head = sel.xpath('//*[@id="main"]/h2')
		rows_r1 = sel.xpath('//tr[@class = "row r1"]')
		rows_r0 = sel.xpath('//tr[@class = "row r0"]')
		base = sel.xpath('//*[@class = "row"]')

		items = []


		for row in rows_r1:

			item = MystocksItem()
			item['date'] = head.xpath('text()').extract()[0]
			item['code'] = row.xpath('./td[1]/a/text()').extract()[0]
			item['name'] = row.xpath('./td[2]/text()').extract()[0]
			item['last12_low'] = row.xpath('./td[3]/text()').extract()[0]
			item['last12_high'] = row.xpath('./td[4]/text()').extract()[0]
			item['day_low'] = row.xpath('./td[5]/text()').extract()[0]
			item['day_high'] = row.xpath('./td[6]/text()').extract()[0]
			item['price'] = row.xpath('./td[7]/text()').extract()[0]
			item['previous'] = row.xpath('./td[8]/text()').extract()[0]
			item['change'] = row.xpath('./td[9]/text()').extract()[0]
			item['percentChange'] = row.xpath('./td[10]/text()').extract()[0]
			item['volume'] = row.xpath('./td[12]/text()').extract()[0]
			item['adjustedPrice'] = row.xpath('./td[13]/text()').extract()[0]

			items.append(item)

		for row in rows_r0:
			
			item = MystocksItem()
			item['date'] = head.xpath('text()').extract()[0]
			item['code'] = row.xpath('./td[1]/a/text()').extract()[0]
			item['name'] = row.xpath('./td[2]/text()').extract()[0]
			item['last12_low'] = row.xpath('./td[3]/text()').extract()[0]
			item['last12_high'] = row.xpath('./td[4]/text()').extract()[0]
			item['day_low'] = row.xpath('./td[5]/text()').extract()[0]
			item['day_high'] = row.xpath('./td[6]/text()').extract()[0]
			item['price'] = row.xpath('./td[7]/text()').extract()[0]
			item['previous'] = row.xpath('./td[8]/text()').extract()[0]
			item['change'] = row.xpath('./td[9]/text()').extract()[0]
			item['percentChange'] = row.xpath('./td[10]/text()').extract()[0]
			item['volume'] = row.xpath('./td[12]/text()').extract()[0]
			item['adjustedPrice'] = row.xpath('./td[13]/text()').extract()[0]

			items.append(item)
		return items		

			
			
		

