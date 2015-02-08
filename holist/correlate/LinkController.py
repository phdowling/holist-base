from holist.core.model.MongoDBCorpus import MongoDBCorpus

from holist.util.util import *
from holist.util import config

from klein import Klein

import inspect

logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

#CORE_IP = config.holistcoreurl
#REGISTER_PORT = config.holistcoreport
#LISTEN_PORT = config.link_node_port + 1
TESTING = True
REBUILD = False

_endpoints = dict()


def entrypoint(*args_outer, **kwargs_outer):
    def entrypoint_decorator(endpoint_method):
        assert inspect.ismethod(endpoint_method), "endpoint decorator applies to bound methods!"
        assert hasattr(endpoint_method.__self__, "name"), "Correlator needs to define a name attribute!"

        correlator_name = endpoint_method.__self__.name
        _endpoints[correlator_name] = (endpoint_method, (args_outer, kwargs_outer))

        return endpoint_method
    return entrypoint_decorator


class LinkController(object):
    def __init__(self, strategies, api):
        self.corpus = MongoDBCorpus()
        self.correlators = strategies
        self.api = api
        self.setupApi()

    def setupApi(self):
        for correlator in self.correlators:
            endpoint_method, (args, kwargs) = _endpoints[correlator.name]
            self.api.route(*args, **kwargs)(endpoint_method)

    def handleNewDocuments(self, doc_ids):
        documents = self.corpus.getDocuments(doc_ids)

        ln.debug("Got %s new documents.", len(documents))

        for correlator in self.correlators:
            try:
                correlator.on_new_documents(documents)
            except AttributeError:
                ln.debug("Correlator %s does not implement onNewDocuments")