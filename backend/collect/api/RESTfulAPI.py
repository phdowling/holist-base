from backend.util.util import *
from backend.util import config as holistConfig

ln = getModuleLogger(__name__)

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
import cgi
import json


class RESTfulFrontend(object):
    def __init__(self, controller):
        self.controller = controller

        root = Resource()
        registerPage = RegisterListener(self.controller)
        root.putChild("register_listener", registerPage)
        
        statusPage = StatusPage(self.controller)
        root.putChild("status", statusPage)

        factory = Site(root)
        reactor.listenTCP(holistConfig.collectNodePort, factory)


class RegisterListener(Resource): 
    #todo: some checks for ip, port correctness
    def __init__(self, controller):
        self.controller = controller
    def render_POST(self, request):
        ln.debug("received registration request: %s", request.args)
        ip = cgi.escape(request.args["ip"][0])
        port = cgi.escape(request.args["port"][0])
        if None not in (ip, port):
            self.controller.registerListener(ip, port)
            return json.dumps({"result": "success"})
        else:
            return json.dumps({"result": "failure"})


class StatusPage(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        return json.dumps(
            {"started": self.controller.started,
             "documentsOnStartup": len(self.controller.articlesOnStartup),
             "queuedDocuments": self.controller.getQueuedDocumentCount(),
             "listeners": len(self.controller.listeners),
             "sources": [source.__class__.__name__ for source in self.controller.sources]})

