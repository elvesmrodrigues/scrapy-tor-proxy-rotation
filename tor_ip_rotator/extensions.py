'''Extension that controls and manages IP changes via Tor.

    See: https://docs.scrapy.org/en/latest/topics/extensions.html
'''

import logging
import random
import time 

from scrapy import signals 
from scrapy.exceptions import NotConfigured

from tor_ip_rotator.tor_controller import TorController

logger = logging.getLogger(__name__)

class TorRenewIp(object):
    def __init__(self, crawler, item_count, allow_reuse_ip_after = 10):
        self.crawler = crawler
        self.item_count = item_count
        self.items_scraped = 0

        self.tc = TorController(allow_reuse_ip_after=allow_reuse_ip_after)
        
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('TOR_IPROTATOR_ENABLED', False):
            raise NotConfigured()

        item_count = crawler.settings.getint('TOR_IPROTATOR_ITEMS_BY_IP', 1000)
        allow_reuse_ip_after = crawler.settings.getint('TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER', 10)

        ext = cls(crawler=crawler, item_count=item_count, allow_reuse_ip_after=allow_reuse_ip_after)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    def item_scraped(self, item, spider):
        self.items_scraped += 1
        if self.items_scraped == self.item_count:
            self.items_scraped = 0
            
            self.crawler.engine.pause()
            if not self.tc.renew_ip():
                raise Exception('FatalError: Failed to find a new IP')
            self.crawler.engine.unpause()
