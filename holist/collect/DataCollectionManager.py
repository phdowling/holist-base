import logging
from threading import Thread
from celery.exceptions import TimeoutError

from holist.collect.db.CollectorDatabaseInterface import CollectorDatabaseInterface
from holist.util import util
from holist.util import config as holistConfig


logging.basicConfig(format=holistConfig.logFormat, level=logging.DEBUG if holistConfig.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

import time

# USE_WHOLE_DB = False assumes that sources do not repeat old IDs over longer times
USE_WHOLE_DB = holistConfig.memorize_all_documents


class DataCollectionManager(object):
    def __init__(self, sources, hashfxn=hash):
        self.listeners = []

        self.databaseInterface = CollectorDatabaseInterface()
        ln.debug("on startup, have %s queued documents.", self.databaseInterface.getQueuedDocumentCount())

        self.sources = sources
        self._validate_sources()
        self.hashfxn = hashfxn

        self.connected = False

        if USE_WHOLE_DB:
            self.knownDocuments = set(self.databaseInterface.get_all_document_ids())
        else:
            self.knownDocuments = set()

        self._iteration_states = dict([(source, True) for source in self.sources])

        self.started = time.time()

        self.updating = None
        ln.debug("Starting update loop")
        self._start_update_loop()
        ln.info("DataCollectionManager fully initialized.")

    def _validate_sources(self):  # todo: we should eventually use zope.interface or something like that
        for source in self.sources:
            if hasattr(source, "update_and_get_documents"):
                assert hasattr(source, "update_and_get_documents_delay"), "Need @remote_task decorator on update method"
            elif hasattr(source, "get_documents"):
                assert hasattr(source, "get_documents_delay"), "Need to add @remote_task decorator to update method"
            else:
                raise AttributeError("source class %s does not define update_and_get_documents or get_documents!",
                                     source.__class__.__name__)
            if not hasattr(source, "updating"):
                ln.warn("Source %s does not define its self.updating state", source.__class__)
                source.updating = False

    def isFirstIteration(self, source):
        return self._iteration_states[source]

    def signalFirstIteration(self, source):
        self._iteration_states[source] = False

    def _start_update_loop(self):
        self.updating = True

        def update_loop():
            while self.updating:
                self._update()
                time.sleep(holistConfig.collect_update_wait_time)

        update_thread = Thread(target=update_loop)
        update_thread.setDaemon(True)
        update_thread.start()

    def shutdown(self):
        ln.info("Shutting down DataCollectionManager.")
        self.updating = False

    def _update(self):
        updates = []
        for source in self.sources[:]:
            if not source.updating:
                if hasattr(source, "update_and_get_documents"):
                    res = source.update_and_get_documents_delay()
                else:
                    ln.info("Source %s will not support updates, getting data and discarding source.", source.__class__)
                    res = source.get_documents_delay()
                    self.sources.remove(source)
                updates.append((source, res))
            else:
                ln.debug("skipping update for source of class %s", source.__class__)

        for source, async_result in updates:
            try:
                result = async_result.get(timeout=holistConfig.data_source_update_timeout)
            except TimeoutError:
                ln.exception("Async task timed out for source %s!", source)
                async_result.forget()
                source.updating = False
                continue

            if async_result.status == 'SUCCESS':
                self.handleData(source, result)
            elif async_result.status == 'FAILURE':
                ln.error("DataSource %s threw an error! Status is FAILURE, message: %s.", result)
            elif async_result.status == 'RETRY':
                ln.error("Task status is retry, don't know how to handle this yet!")
            else:
                ln.error("Task has a state (%s) we don't understand.", async_result.status)

            source.updating = False

    def handleData(self, source, result):
        # don't re-add documents that were already in the DB when the node was started
        ln.debug("Source %s returned %s documents. Filtering out known documents...", source, len(result))
        self.ensureUniqueIds(source, result)
        kept = self.filterKnownDocuments(source, result)
        ln.info("Received a total of %s new documents from data source %s.", len(kept), source)

        self.databaseInterface.queueDocuments(kept)

    def ensureUniqueIds(self, source, result):
        for document in result:
            document.holist_unique_id = self.hashfxn(getattr(document, source.getUniqueIdField()))

    def filterKnownDocuments(self, source, documents):
        filter_using_db = False

        if self.isFirstIteration(source):
            ln.debug("first iteration, filtering from database.")
            filter_using_db = True

        keep = []
        for document in documents:
            is_known = False

            if filter_using_db:
                # USE_WHOLE_DB = False assumes that sources do not repeat old IDs over longer times
                if not USE_WHOLE_DB and self.databaseInterface.isDocumentKnown(document):
                    is_known = True

            if document.holist_unique_id in self.knownDocuments:
                is_known = True

            if not is_known:
                keep.append(document)
            self.knownDocuments.add(document.holist_unique_id)

        self.signalFirstIteration(source)
        return keep