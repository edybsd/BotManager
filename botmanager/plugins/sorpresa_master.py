from bs4 import BeautifulSoup
import certifi
import urllib3
import logging
from botmanager.plugin import PluginError
from botmanager.utils import DictQuery

log = logging.getLogger('PluginSorpresaMaster')


class PluginSorpresaMaster(object):
    def __init__(self,config=None):
        if config is not None:
            self.proxy=DictQuery(config).get('PluginSorpresaMaster/proxy',
                                        DictQuery(config).get('General/proxy'))



    def get_commands(self):
        print("SorpresaMaster get_commands")

    def process_command(self, args):
        """

        :rtype: object
        """
        try:
            if self.proxy is None:
                http = urllib3.PoolManager(
                            cert_reqs='CERT_REQUIRED',
                            ca_certs=certifi.where())
            else :
                http = urllib3.ProxyManager('http://openfirevc.sis.ad.bia.itau:9128/',
                            cert_reqs = 'CERT_REQUIRED',
                             ca_certs = certifi.where())

            r = http.request('GET', 'https://sorpresas.mastercard.com/ar/beneficios')

            if r.status != 200:
                raise PluginError('https://sorpresas.mastercard.com/ar/beneficios returned [%d]' % r.status)

            soup = BeautifulSoup(r.data, "html.parser")

            message = "*Promos Sorpresas Master*:\n"
            for item in soup.select('div.promotion-body-caption'):
                message += '  - ' + item.string.strip() + "\n"
            print (message)
        except  Exception as e:
            log.error('PluginSorpresaMaster error: %s', e)
            raise e

def get_instance(config=None):
    return PluginSorpresaMaster(config)
