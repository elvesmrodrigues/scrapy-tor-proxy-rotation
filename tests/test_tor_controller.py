import unittest
import requests
from tor_ip_rotator import TorController

IP_CHECK_SERVICE = 'http://icanhazip.com/'
TOR_CONTROLLER = TorController(allow_reuse_ip_after=10)

class TestTorController(unittest.TestCase):
    def test_anonymity(self):
        """Tests whether the IP used by Tor is different from the machine in use"""
        machine_ip = requests.get(IP_CHECK_SERVICE).text.replace('\n','')
        tor_ip = TOR_CONTROLLER.get_ip()

        self.assertNotEqual(machine_ip, tor_ip)

    def test_renew_ip(self):
        """Tests if the Tor IP change command is working"""
        last_ip = TOR_CONTROLLER.get_ip()
        new_ip = TOR_CONTROLLER.renew_ip()

        self.assertNotEqual(last_ip, new_ip)

    def test_reuse_ip(self):
        """Tests if an IP is not reused for a minimum number of times"""
        init_ip = TOR_CONTROLLER.get_ip()

        used_ips = list()
        for _ in range(10): 
            #Because 10 is the minimum that an IP needs to wait to be 
            # reused (see parameter allow_reuse_ip_after in TorController above)
        
            new_ip = TOR_CONTROLLER.renew_ip()
            used_ips.append(new_ip)

        self.assertNotIn(init_ip, used_ips)
        
if __name__ == "__main__":
    unittest.main()