from holist.collect.db.CollectorDatabaseInterface import CollectorDatabaseInterface

from holist.util.util import *
from holist.util import config

import inspect

logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

#CORE_IP = config.holistcoreurl
#REGISTER_PORT = config.holistcoreport
#LISTEN_PORT = config.link_node_port + 1
TESTING = True
REBUILD = False

#global __entrypoints


class ApplicationController(object):

    def __init__(self, strategies):
        self.corpus = CollectorDatabaseInterface()
        self.correlators = strategies

    def handleNewDocuments(self, doc_ids):
        documents = self.corpus.getDocuments(doc_ids)

        ln.debug("Got %s new documents.", len(documents))

        for correlator in self.correlators:
            try:
                correlator.on_new_documents(documents)
            except AttributeError:
                ln.debug("Correlator %s does not implement onNewDocuments")