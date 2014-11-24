__author__ = 'raoulfriedrich'

from backend.util.util import *
ln = getModuleLogger(__name__)

UDP_PORT = 11593; CHECK_PERIOD = 20; CHECK_TIMEOUT = 15

import time
from twisted.application import internet
from twisted.internet import protocol, reactor, task

class TwistedBeatServer(object):

    def __init__(self, callback, udp_port):

        detectorSvc = DetectorService(callback)

        receiver = Receiver()
        receiver.callback = detectorSvc.update

        ln.info("Listen for heartbeats at port %s", udp_port)
        reactor.listenUDP(udp_port, receiver)

class Receiver(protocol.DatagramProtocol):

    def datagramReceived(self, data, (ip, port)):
        if data.startswith('PyHB'):
            #ln.debug("Heartbeat received from %s:%s Data: %s", ip, port, data)
            self.callback(ip, data.split('-')[1])

class DetectorService(internet.TimerService):

    def __init__(self, callback):
        self.callback = callback
        self.beats = {}
        self.lc = task.LoopingCall(self.detect)
        self.lc.start(CHECK_PERIOD)

    def update(self, ip, port):
        self.beats[ip] = [time.time(), port]

    def detect(self):
        limit = time.time() - CHECK_TIMEOUT
        silent = [(ip, port) for (ip, (ipTime, port)) in self.beats.items() if ipTime < limit]

        for (ip, port) in silent:
            del self.beats[ip]

        if(silent):
            self.callback(silent)