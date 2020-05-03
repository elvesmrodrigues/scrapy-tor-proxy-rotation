'''Extension that controls and manages IP changes via Tor.

    See: https://docs.scrapy.org/en/latest/topics/extensions.html
'''

import logging
import random
import time 

from scrapy import signals 
from scrapy.exceptions import NotConfigured

from .tor_controller import TorController

logger = logging.getLogger(__name__)

class TorRenewIp(object):
    def __init__(self, crawler, item_count, password, allow_reuse_ip_after = 10):
        self.crawler = crawler
        self.item_count = item_count
        self.items_scraped = 0

        self.tc = TorController(password=password, allow_reuse_ip_after=allow_reuse_ip_after)
        self.tc.renew_ip()
        
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('TOR_RENEW_IP_ENABLED', False):
            raise NotConfigured()

        item_count = crawler.settings.getint('TOR_ITEMS_BY_IP', 1000)
        allow_reuse_ip_after = crawler.settings.getint('TOR_ALLOW_REUSE_IP_AFTER', 10)
        tor_pass = crawler.settings.get('TOR_PASSWORD', 'my password')

        ext = cls(crawler=crawler, item_count=item_count, password=tor_pass, allow_reuse_ip_after=allow_reuse_ip_after)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    def item_scraped(self, item, spider):
        self.items_scraped += 1
        if self.items_scraped == self.item_count:
            self.items_scraped = 0
            
            self.crawler.engine.pause()
            if not self.tc.renew_ip():
                raise Exception('FatalError: Falha ao encontrar novo IP')
            self.crawler.engine.unpause()
