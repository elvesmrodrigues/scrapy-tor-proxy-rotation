'''Middleware linking Scrapy to Tor'''

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        '''Configures proxy so that every request is passed by Tor'''

        # http://127.0.0.1:8118 is the default address for Privoxy
        request.meta['proxy'] = 'http://127.0.0.1:8118'
