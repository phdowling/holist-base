from backend.core.model.MongoDBCorpus import MongoDBCorpus
from backend.util.communication.NodeCommunicator import NodeCommunicator

__authors__ = ['raoulfriedrich', 'dowling']

from backend.util.util import *

logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor


from backend.link.api.RESTfulApi import RESTfulApi

CORE_IP = config.holistcoreurl
REGISTER_PORT = config.holistcoreport
LISTEN_PORT = config.link_node_port + 1
TESTING = True
REBUILD = False


class LinkController(object):

    def __init__(self, strategies):
        # init and start node communicator (connection to core node)
        #self.nodeCommunicator = NodeCommunicator(self, LISTEN_PORT, strategy=False)
        #self.nodeCommunicator.registerWithNode(CORE_IP, REGISTER_PORT)

        # init rest apis
        self.frontend = RESTfulApi(self)

        self.corpus = MongoDBCorpus()
        self.strategies = strategies
        self.setupApi()

        # start server
        ln.info("running reactor.")
        reactor.run()
        reactor.addSystemEventTrigger('before', 'shutdown', stopLogging)

    def setupApi(self):
        for strategy in self.strategies:
            self.frontend.addApiResource(strategy, strategy.getApiPath())

    def handleNewDocuments(self, doc_ids):
        # TODO: accept IDs, not full documents. then use MongoDBCorpus to batch retrieve documents

        documents = self.corpus.getDocuments(doc_ids)

        ln.debug("Got %s new documents.", len(documents))

        for document in documents:
            # TODO: pass the documents to each strategy
            pass
