import random
import requests
import time
import logging

from stem import Signal
from stem.control import Controller
from stem.util.log import get_logger

import os

logger = get_logger()
logger.propagate = False

# Site to get IP
IP_CHECK_SERVICE = 'http://icanhazip.com/'

tc_logging = logging.getLogger(__name__)

class TorController:
    def __init__(self, control_port: int = 9051, password: str = 'my password', host: str = '127.0.0.1', port: int = 9050, allow_reuse_ip_after: int = 5):
        '''Creates a new instance of TorController.
        Keywords arguments:
        control_port -- Standard Tor control port (default 9051)
        password -- Password to control Tor (default 'my password')
        host -- Tor server default IP address (default '127.0.0.1')
        port -- Standard Tor server port (default 9050)
        allow_reuse_ip_after -- When an already used IP can be used again. If 0, there will be no IP reuse control. (default 5). 
        '''

        self.control_port = control_port
        self.password = password
        self.used_ips = list()
        self.allow_reuse_ip_after = allow_reuse_ip_after
        self.proxies = {'http':  f'socks5://{host}:{port}',
                        'https': f'socks5://{host}:{port}'}

    def get_ip(self) -> str:
        '''Returns the current IP of the machine.'''

        r = requests.get(IP_CHECK_SERVICE)
        if r.ok:
            return r.text.replace('\n', '')
        raise Exception()

    def get_tor_ip(self) -> str:
        '''Returns the current IP used by Tor.'''
        r = requests.get(IP_CHECK_SERVICE, proxies=self.proxies)
        if r.ok:
            return r.text.replace('\n', '')
        raise Exception()

    def change_ip(self):
        '''Send IP change signal to Tor.'''

        with Controller.from_port(port=self.control_port) as controller:
            controller.authenticate(password=self.password)
            controller.signal(Signal.NEWNYM)

    def renew_ip(self):
        '''Change Tor's IP (what differs from this change_ip method is that change_ip does not guarantee that the IP has been changed or has been changed to the same).
           
            Returns False if the attempt was unsuccessful or True if the IP was successfully changed.
        '''
        tc_logging.debug('Alterando IP...')
        # Makes up to 30 IP change attempts
        for _ in range(30):
            self.change_ip()

            try:
                current_ip = self.get_tor_ip()
            except:
                time.sleep(random.randint(1, 10))
                continue

            # Checks that within 7.5 seconds the IP has been changed
            used_time = 0
            while used_time < 15:
                if current_ip in self.used_ips:
                    used_time += 1
                    time.sleep(.5)
                else:
                    break

            if used_time < 15:
                # Controls IP reuse
                if self.allow_reuse_ip_after > 0:
                    if len(self.used_ips) == self.allow_reuse_ip_after:
                        del self.used_ips[0]
                    self.used_ips.append(current_ip)
                tc_logging.debug('IP alterado')
                return True
                
        tc_logging.error('Falha ao alterar IP')
        return False
