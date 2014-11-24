from pymongo import MongoClient

from backend.util import config

LOCAL_DB_LOCATION = config.dblocation
LOCAL_DB_PORT = config.dbport
LOCAL_DB_NAME = config.dbname

class CollectorDatabaseInterface(object):
    def __init__(self):
        self.documentClient = MongoClient(LOCAL_DB_LOCATION, LOCAL_DB_PORT)
        self.new_documents = self.documentClient[LOCAL_DB_NAME].new_documents
        self.documents = self.documentClient[LOCAL_DB_NAME].documents

    def addDocuments(self, documents):
        for document in documents:
            bson = document.__dict__
            self.new_documents.insert(bson)

    def getQueuedDocuments(self):
        return self.new_documents.find()

    def getQueuedDocumentCount(self):
        return self.new_documents.find().count()

    def isDocumentKnown(self, document):
        return bool(self.new_documents.find({"holist_unique_id":document.holist_unique_id}).count() +
                    self.documents.find({"holist_unique_id":document.holist_unique_id}).count())