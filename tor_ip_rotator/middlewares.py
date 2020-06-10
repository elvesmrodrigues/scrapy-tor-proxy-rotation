'''Middleware linking Scrapy to Tor'''

from scrapy import signals
from tor_ip_rotator import TorController

class TorProxyMiddleware(object):
    def __init__(self, max_count, allow_reuse_ip_after = 10):
        '''Creates a new instance of X
        
        Keywords arguments:
            max_count -- Maximum IP usage
            allow_reuse_ip_after -- When an IP can be reused
        '''
        
        self.items_scraped = 0
        self.max_count = max_count

        self.tc = TorController(allow_reuse_ip_after=allow_reuse_ip_after)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('TOR_IPROTATOR_ENABLED', False):
            raise NotConfigured()

        max_count = crawler.settings.getint('TOR_IPROTATOR_CHANGE_AFTER', 1000)
        allow_reuse_ip_after = crawler.settings.getint('TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER', 10)

        mw = cls(max_count=max_count, allow_reuse_ip_after=allow_reuse_ip_after)

        return mw

    def process_request(self, request, spider):
        if self.items_scraped >= self.max_count:
            spider.log('Changing Tor IP...')
            self.items_scraped = 0
            
            new_ip = self.tc.renew_ip() 
            if not new_ip:
                raise Exception('FatalError: Failed to find a new IP')
            
            spider.log(f'New Tor IP: {new_ip}')

        # http://127.0.0.1:8118 is the default address for Privoxy
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        self.items_scraped += 1
