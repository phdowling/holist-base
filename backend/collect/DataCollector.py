import logging

from backend.collect.api.RESTfulAPI import RESTfulFrontend
from backend.collect.db.CollectorDatabaseInterface import CollectorDatabaseInterface
from backend.util import util
from backend.util.communication.Listener import Listener
from backend.util import config as holistConfig


logging.basicConfig(format=holistConfig.logFormat, level=logging.DEBUG if holistConfig.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

import time

from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from backend.util.communication.Heartbeat.HeartbeatClient import HearbeatClient


class DataCollector(object):
    def __init__(self, sources):
        self.listeners = []

        heartbeatThread = HearbeatClient(self.listeners, holistConfig.collectNodePort)
        heartbeatThread.start()

        self.frontend = RESTfulFrontend(self)
        self.databaseInterface = CollectorDatabaseInterface()
        self.sources = sources

        self.connected = False
        self.loop = LoopingCall(self.update)
        self.loop.start(10)
        self.started = time.time()

        self.firstIteration = dict([(source.__class__.__name__, True) for source in self.sources])
        self.knownDocuments = set()

        reactor.run()
        reactor.addSystemEventTrigger('before', 'shutdown', util.stopLogging)

    def update(self):
        deferToThread(self.__update)

    def getQueuedDocumentCount(self):
        return self.databaseInterface.getQueuedDocumentCount()

    def __update(self):
        for source in self.sources:
            if not source.updating:
                d = deferToThread(source.updateAndGetDocuments)
                cbk = lambda result: self.handleData(source, result)
                d.addCallback(cbk)
                err = lambda result: self.handleFailure(source, result)
                d.addErrback(err)
            else:
                ln.debug("skipping update for source of class %s", source.__class__)

    def handleData(self, source, result):
        # don't re-add documents that were already in the DB when the node was started
        ln.debug("have %s documents. Filtering out known documents...", len(result))
        self.ensureUniqueIds(source, result)
        result = self.filterKnownDocuments(source, result)
        ln.info("Received a total of %s new documents from %s data sources.", len(result), len(self.sources))

        self.databaseInterface.addDocuments(result)
        source.updating = False
        if result:
            self.notifyListeners()

    @staticmethod
    def ensureUniqueIds(source, result):
        for document in result:
            document.holist_unique_id = hash(document.__dict__[source.getUniqueIdField()])

    def filterKnownDocuments(self, source, documents):
        if self.firstIteration[source.__class__.__name__]:
            ln.debug("first iteration, filtering from database.")
        keep = []
        for document in documents:
            if self.firstIteration[source.__class__.__name__]:
                if self.databaseInterface.isDocumentKnown(document):
                    self.knownDocuments.add(document.id)
                else:
                    keep.append(document)
            else:
                if document.id not in self.knownDocuments:
                    keep.append(document)
        self.firstIteration[source.__class__.__name__] = False
        return keep

    def handleFailure(self, source, result):
        ln.warn("there was an error from source %s: %s", source.__class__, result.getTraceback())
        source.updating = False

    def registerListener(self, ip, port):
        for listener in self.listeners:
            if listener.ip == ip and listener.port == port:
                return

        listener = Listener(ip, port)
        self.listeners.append(listener)
        ln.info("registered listener at %s:%s", ip, port)

    def notifyListeners(self):
        for listener in self.listeners[:]:
            res = listener.notify()
            if not res:
                ln.warn("Listener at %s:%s not responsive, removing.", listener.ip, listener.port)
                self.listeners.remove(listener)