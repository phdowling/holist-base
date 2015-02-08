from threading import Thread

from holist.core.control.AnnotatorManager import AnnotatorManager

from holist.collect.db.CollectorDatabaseInterface import CollectorDatabaseInterface
from holist.core.model.MongoDBCorpus import MongoDBCorpus
from holist.util.util import *


ln = getModuleLogger(__name__)

import time


# we wait until there are at least 20 new documents OR 3 minutes have passed.
MINIMUM_QUEUE_SIZE = config.update_new_documents_threshold
MINIMUM_WAIT_TIME = config.update_minimum_wait_time


def convertDocumentsToDicts(documents):
    dicts = [document.__dict__ for document in documents]
    for docDict in dicts:
        docDict["_id"] = str(docDict["_id"])
    return dicts


class CoreController(object):

    def __init__(self, annotators):
        self.updating = None

        self.database_interface = CollectorDatabaseInterface()  # for retrieving new documents

        self.strategyManager = AnnotatorManager(self, annotators)

        self.lastUpdated = "never"

        ln.info("Starting update loop.")
        self.start_update_loop()

    def start_update_loop(self):
        def update_loop():
            while True:
                self._update_loop_iteration()
                time.sleep(config.core_update_wait_time)

        update_loop_thread = Thread(target=update_loop)
        update_loop_thread.setDaemon(True)
        update_loop_thread.start()

    def _update(self):
        self.updating = True
        newDocuments = self.database_interface.getQueuedDocuments()
        newDocCount = self.database_interface.getQueuedDocumentCount()
        if newDocuments:
            ln.info("Running update iteration, got about %s new documents from collector.", newDocCount)

            for chunk_no, document_chunk in enumerate(grouper(newDocuments, config.annotators_chunk_size)):
                annotated_documents = self.strategyManager.run_annotators(document_chunk)
                self.database_interface.addDocuments(annotated_documents)
                self.database_interface.signalDocumentsHandled(annotated_documents)
                self.lastUpdated = time.time()
                ln.debug("%s chunks processed by core.", chunk_no + 1)
        else:
            ln.debug("No new documents. Cancelling update iteration.")
        self.updating = False

    def _update_loop_iteration(self):
        if self.updating or not self.database_interface.getQueuedDocumentCount():
            return
        num_new = self.database_interface.getQueuedDocumentCount()
        if num_new >= MINIMUM_QUEUE_SIZE or time.time() - self.lastUpdated >= MINIMUM_WAIT_TIME:
            self._update()