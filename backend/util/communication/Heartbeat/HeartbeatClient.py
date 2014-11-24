__author__ = 'raoulfriedrich'

from backend.util.util import *
ln = getModuleLogger(__name__)

import threading, socket, time

BEAT_PERIOD = 5

class HearbeatClient(threading.Thread):

    def __init__(self, listeners, port):
        super(HearbeatClient, self).__init__()
        self.listeners = listeners
        self.port = port

    def run(self):
        while True:
            hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            for listener in self.listeners:
                hbSocket.sendto('PyHB-' + str(self.port), (listener.ip, int(listener.port)))
                #ln.debug("Heartbeat sent to %s:%s", listener.ip, listener.port)

            time.sleep(BEAT_PERIOD)