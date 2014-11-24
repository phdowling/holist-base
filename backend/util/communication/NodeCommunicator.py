from backend.util.communication.Heartbeat.TwistedBeatServer import TwistedBeatServer
from backend.util.util import *

ln = getModuleLogger(__name__)

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.internet.threads import deferToThread

import requests
import json
import time
import cgi

class Task(Resource):
    def __init__(self, controller, strategy):
        self.controller = controller
        self.isStrategy = strategy

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")
        data = request.content.read()
        ln.debug("received task: %s", data[:1000])
        try:
            data = json.loads(data)
        except:
            ln.error("got invalid data: %s", data[:1000])
            return 0

        if self.isStrategy:
            sender = data["respondTo"]
            docs = data["documents"]
            relabel = data.get("relabel", False)

            self.controller.queueDocuments(sender, docs, relabel)
        else:
            docs = data["documents"]
            self.controller.handleNewDocuments(docs)
        ln.info("Queued task.")

        return json.dumps({"result": "ok"})

class RegisterListener(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")
        ln.debug("received registration request: %s", request.args)
        ip = cgi.escape(request.args["ip"][0])
        port = cgi.escape(request.args["port"][0])
        if None not in (ip, port):
            self.controller.registerListener(ip, port)
            return json.dumps({"result": "success"})
        else:
            return json.dumps({"result": "failure"})

class SmallTask(Resource):
    def __init__(self, controller):
        self.controller = controller

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        document = cgi.escape(request.args["document"][0])
        return json.dumps(self.controller.handleOne(document))

class NodeCommunicator(object):

    def __init__(self, controller, listenPort, strategy=True):
        self.controller = controller
        self.listenPort = listenPort
        self.isStrategy = strategy

        self.setupResources()
        self.loopingCall = None

    def setupResources(self):
        root = Resource()
        self.heartbeatServer = None;
        taskPage = Task(self.controller, self.isStrategy)
        registerPage = RegisterListener(self.controller)
        if self.isStrategy:
            root.putChild("small_task", SmallTask(self.controller))
            root.putChild("task", taskPage)
        else:
            root.putChild("notify", taskPage)
            root.putChild("register_listener", registerPage)
        factory = Site(root)
        reactor.listenTCP(self.listenPort, factory)

        ln.debug("Listening on port %s", self.listenPort)

    def respond(self, sender, data):
        ln.debug("attempting to respond to %s", sender)
        requests.post(sender, data=json.dumps(data))

    def registerWithNode(self, nodeIp, registerPort, maxRetries=300):
        deferToThread(self._registerWithNode, nodeIp, registerPort, maxRetries)

    def _registerWithNode(self, nodeIp, registerPort, maxRetries):
        for x in range(maxRetries):
            ln.debug("attempting to register with node on %s:%s", nodeIp, registerPort)
            try:
                if self.isStrategy:
                    r = requests.post("http://" + nodeIp + ":"+str(registerPort)+"/register_strategy",
                                      {"strategy": self.controller.NAME, "ip": "localhost", "port": self.listenPort})
                else:
                    r = requests.post("http://" + nodeIp + ":"+str(registerPort)+"/register_listener",
                                      {"ip": "localhost", "port": self.listenPort})

            except Exception as e:
                ln.error("Couldn't connect to node on localhost:%s", registerPort)
                time.sleep(2)
                continue
            if r.status_code == 200:
                ln.info("registered with node.")
                if self.heartbeatServer is None:
                    self.heartbeatServer = TwistedBeatServer(self.handleServerDown, self.listenPort)
                return True
        return False

    def handleServerDown(self, clients):
        for (ip, port) in clients:
            self.registerWithNode(ip, port)
