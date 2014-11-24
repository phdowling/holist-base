__author__ = 'raoulfriedrich'

from backend.util.util import *
ln = getModuleLogger(__name__)

from twisted.web.resource import Resource

from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor


class RESTfulApi(object):

    def __init__(self, controller):
        self.controller = controller

        self.root = File("./holist-web")
        self.api = Resource()
        self.root.putChild("api", self.api)

        factory = Site(self.root)
        reactor.listenTCP(config.link_node_port, factory)

    def addApiResource(self, resource, relative_path):
        """
        used to provide access to the APIs defined by the strategies, called by LinkController.
        :param resource: the resource to be provided access to.
        :param relative_path: the relative path (access will be to http://holisturl.tld/api/relative_path)
        """
        self.api.putChild(relative_path, resource)

