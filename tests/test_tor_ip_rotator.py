import unittest
import requests
import time 

from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler

from tor_ip_rotator import TorProxyMiddleware

session = requests.sessions.Session()

# Where Tor is running 
session.proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}

class TestTorIPRotator(unittest.TestCase):
    def test_proxy_use(self):
        '''Tests whether the proxy is being used'''

        crawler = get_crawler(spidercls=Spider, settings_dict={'TOR_IPROTATOR_ENABLED': True, 'TOR_IPROTATOR_ITEMS_BY_IP': 50})
        spider = crawler._create_spider('foo')
        middleware = TorProxyMiddleware.from_crawler(crawler)
        
        urls = ['http://scrapytest.org/'] * 100

        for url in urls:
            req = Request(url)
            middleware.process_request(req, spider)

            self.assertEqual(req.meta['proxy'], 'http://127.0.0.1:8118')

    def test_change_ip_by_interval(self):
        '''Tests whether the IP changes in the interval'''

        change_ip_after = 10

        crawler = get_crawler(spidercls=Spider, settings_dict={'TOR_IPROTATOR_ENABLED': True, 'TOR_IPROTATOR_CHANGE_AFTER': change_ip_after})
        spider = crawler._create_spider('foo')
        middleware = TorProxyMiddleware.from_crawler(crawler)
        
        urls = ['http://icanhazip.com/'] * 101

        count = 0
        last_ip = ''

        for url in urls: 
            req = Request(url)
            middleware.process_request(req, spider)

            if count == change_ip_after:
                time.sleep(5)

                curr_ip = session.get('http://icanhazip.com/').text.replace('\n','')
                count = 0


                self.assertNotEqual(last_ip, curr_ip)
                last_ip = curr_ip

            count += 1

    def test_not_reuse_ip_in_interval(self):
        '''Tests if an IP is not reused in a range'''

        change_ip_after = 5
        allow_reuse_ip_after = 5

        used_ips = list()

        crawler = get_crawler(spidercls=Spider, settings_dict={'TOR_IPROTATOR_ENABLED': True, 'TOR_IPROTATOR_CHANGE_AFTER': change_ip_after, 'TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER': allow_reuse_ip_after})
        spider = crawler._create_spider('foo')
        middleware = TorProxyMiddleware.from_crawler(crawler)
        
        urls = ['http://icanhazip.com/'] * 100

        count = 0
        last_ip = ''

        for url in urls: 

            req = Request(url)
            middleware.process_request(req, spider)

            if count == change_ip_after:
                count = 0

                if len(used_ips) == allow_reuse_ip_after:
                    del used_ips[0]

                time.sleep(5)
                
                ip = session.get('http://icanhazip.com/').text.replace('\n','')
                self.assertNotIn(ip, used_ips)

                used_ips.append(ip)

            count += 1

