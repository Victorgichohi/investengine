from twisted.internet import reactor
from scrapy import log, signals
from scrapy.crawler import Crawler

import logging
from scrapy.utils.project import get_project_settings
from mystocks.spiders.synergyspider import Synergyspider


def spidermain():
	spider = Synergyspider(domain='http://live.mystocks.co.ke/price_list')
	spider.start_urls =([
			'http://live.mystocks.co.ke/price_list/20140402',
            ])
	settings = get_project_settings()
	crawler = Crawler(settings)
	crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
	crawler.configure()
	crawler.crawl(spider)
	crawler.start()	
	
	log.start(loglevel=logging.DEBUG)
	log.msg('Running reactor...')
	reactor.run()  # the script will block here until the spider is closed
	
	
	log.msg('Reactor stopped.')  		

spidermain()





