from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.util import config

from pymongo import MongoClient


LOCAL_DB_LOCATION = config.dblocation
LOCAL_DB_PORT = config.dbport
LOCAL_DB_NAME = config.dbname


class CollectorDatabaseInterface(object):
    def __init__(self):
        self.documentClient = MongoClient(LOCAL_DB_LOCATION, LOCAL_DB_PORT)
        self.new_documents = self.documentClient[LOCAL_DB_NAME].new_documents
        self.documents = self.documentClient[LOCAL_DB_NAME].documents

    def get_all_document_ids(self):
        qd = list((doc["holist_unique_id"] for doc in self.new_documents.find()))
        old = list((doc["holist_unique_id"] for doc in self.documents.find()))
        all_ = set(qd + old)
        assert len(all_) == len(qd) + len(old)
        return all_

    def queueDocuments(self, documents):
        for document in documents:
            bson = document.__dict__
            self.new_documents.insert(bson)

    def getQueuedDocuments(self):
        return (bson_to_document(bson) for bson in self.new_documents.find())

    def getQueuedDocumentCount(self):
        return self.new_documents.find().count()

    def signalDocumentsHandled(self, documents):
        ids = [doc.holist_unique_id for doc in documents]
        self.new_documents.remove({"holist_unique_id": {"$in": ids}})

    def isDocumentKnown(self, document):
        if self.new_documents.find({"holist_unique_id": document.holist_unique_id}).count():
            return True
        else:
            return bool(self.documents.find({"holist_unique_id": document.holist_unique_id}).count())

    ### CORPUS METHODS
    def __len__(self):
        return self.documents.find().count()

    def __iter__(self):
        ln.debug("iterating through database")
        for doc_bson in self.documents.find():
            document = bson_to_document(doc_bson)
            yield document

    def __getitem__(self, _id):
        return bson_to_document(self.documents.find_one({"_id": _id}))

    def getDocuments(self, idlist):
        return [bson_to_document(doc_bson) for doc_bson in self.documents.find({"holist_unique_id": {"$in": idlist}})]

    def addDocuments(self, documents):
        for document in documents:
            self.addDocument(document)

    def addDocument(self, document):
        # todo: maybe pickle the annotations that mongoDB doesn't understand? e.g. numpy arrays
        self.documents.insert(document.__dict__)  # insert the whole object to the main documents collection
