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
from holist.util.util import startLogging, stopLogging
startLogging('holist')

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
            self.correlator_manager = ApplicationController(self.applications)
            self.core_controller.add_update_callback("correlators", self.correlator_manager.handleNewDocuments)

    def run(self):
        reactor.addSystemEventTrigger('before', 'shutdown', stopLogging)
        klein.run(config.app_ip, config.app_port)

