__author__ = 'dowling'
from celery import Celery
app = Celery('holist_tasks', backend='amqp', broker='amqp://')
from celery_remote_methods import remote_work
remote_work.initialize(app)

from twisted.internet import reactor

from holist.collect.DataCollectionManager import DataCollectionManager
from holist.core.control.CoreController import CoreController
from holist.application.ApplicationController import ApplicationController

from holist.util import config
from holist.util.util import startLogging, stopLogging, getModuleLogger
startLogging('holist')
ln = getModuleLogger(__name__)

from holist.api import routing_cache

import inspect
import klein


class Holist(object):
    def __init__(self, data_sources=None, annotators=None, applications=None):
        self.data_sources = data_sources
        self.annotators = annotators
        self.applications = applications

        if self.data_sources:
            self.collection_manager = DataCollectionManager(self.data_sources)
        if self.annotators:
            self.core_controller = CoreController(annotators)
        if self.applications:
            self.__setup_api()
            self.correlator_manager = ApplicationController(self.applications)
            self.core_controller.add_update_callback("correlators", self.correlator_manager.handleNewDocuments)

    def __setup_api(self):
        for application in self.applications:
            for method_name, method in inspect.getmembers(application.__class__, inspect.ismethod):
                if method.__func__ in routing_cache:
                    args, kwargs = routing_cache[method.__func__]
                    url = args[0]
                    klein.route(*args, **kwargs)(getattr(application, method_name))
                    ln.debug("routing \"%s\" to bound method %s of object %s", url, method_name, application)


    def run(self):
        reactor.addSystemEventTrigger('before', 'shutdown', stopLogging)
        klein.run(config.app_ip, config.app_port)

