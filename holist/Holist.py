__author__ = 'dowling'
from celery import Celery
app = Celery('holist_tasks', backend='amqp', broker='amqp://')
from celery_remote_methods import remote_work
remote_work.initialize(app)
from twisted.internet import reactor

from holist.collect.DataCollectionManager import DataCollectionManager
from holist.core.control.CoreController import CoreController
from holist.correlate.LinkController import LinkController
from holist.util.util import startLogging, stopLogging
startLogging('holist')

from klein import Klein


class Holist(object):
    def __init__(self, data_sources=None, annotators=None, correlators=None):
        self.data_sources = data_sources
        self.annotators = annotators
        self.correlators = correlators

        description_str = "_".join([("collect" if data_sources else ""),
                                    ("core" if annotators else ""),
                                    ("correlate" if correlators else "")])

        self.api = Klein()

        if self.data_sources:
            self.collection_manager = DataCollectionManager(self.data_sources)
        if self.annotators:
            self.core_controller = CoreController(annotators)
        if self.correlators:
            self.correlator_manager = LinkController(self.correlators, self.api)

    def run(self, url, port):
        reactor.addSystemEventTrigger('before', 'shutdown', stopLogging)
        self.api.run(url, port)

