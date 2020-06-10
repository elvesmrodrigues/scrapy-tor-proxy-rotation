import logging
import random
import time
import requests

from stem import Signal
from stem.control import Controller
from stem.util.log import get_logger

logger = get_logger()
logger.propagate = False

# site to get ip
IP_CHECK_SERVICE = 'http://icanhazip.com/'

class TorController:
    def __init__(self, allow_reuse_ip_after: int = 10):
        """Creates a new instance of TorController.
        
        Keywords arguments:
            allow_reuse_ip_after -- When an already used IP can be used again. If 0, there will be no IP reuse control. (default 10). 
        """

        self.allow_reuse_ip_after = allow_reuse_ip_after

        self.used_ips = list()
        self.proxies = {'http':  'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050'}

        self.renew_ip()

    def get_ip(self) -> str:
        """Returns the current IP used by Tor."""

        with requests.Session() as session:
            r = session.get(IP_CHECK_SERVICE, proxies = self.proxies)
            
            if r.ok:
                session.close()
                return r.text.replace('\n', '')
            return r.text.replace('\n', '')

        return ''

    def change_ip(self) -> None:
        """Send IP change signal to Tor."""

        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)

    def renew_ip(self) -> None:
        """Change Tor's IP
           
        Returns the new IP or '', if is not possible to change the IP.
        """
        new_ip = None

        # Try to change the IP 10 times
        for _ in range(10):
            self.change_ip()

            new_ip = self.get_ip() 
            
            # Waits for possible IP change
            waiting = 0
            while waiting <= 30:
                if new_ip in self.used_ips:
                    waiting += 2.5
                    time.sleep(2.5)

                    new_ip = self.get_ip()

                    if not new_ip:
                        break

                else:
                    break
            
            # If we can recover the IP, check if it has already been used
            if new_ip:

                # Controls IP reuse
                if self.allow_reuse_ip_after > 0:
                    if len(self.used_ips) == self.allow_reuse_ip_after:
                        del self.used_ips[0]
                    self.used_ips.append(new_ip)

                return new_ip

            # Wait a random time to try again
            time.sleep(random.randint(5,30))

        # Could not change IP
        return '' 