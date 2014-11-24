import requests

from backend.util.util import *

ln = getModuleLogger(__name__)


class Listener(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def notify(self, data=""):
        try:
            requests.post("http://"+self.ip+":"+str(self.port) + "/notify", data=data)
            ln.debug("notified: %s", "http://"+self.ip+":"+str(self.port))
            return True
        except Exception, e:
            ln.debug("error occured: %s", str(e))
            return False
