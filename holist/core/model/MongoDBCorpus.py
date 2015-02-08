from holist.util.util import *
from holist.core.model.ICorpus import ICorpus

ln = getModuleLogger(__name__)

from holist.util import config

from pymongo import MongoClient


LOCAL_DB_LOCATION = config.dblocation
LOCAL_DB_PORT = config.dbport
LOCAL_DB_NAME = config.dbname



class MongoDBCorpus(ICorpus):  # This updates ONLY the documents collection
    def __init__(self):
        ln.info("initializing MongoDB corpus.")

        self.documentClient = MongoClient(LOCAL_DB_LOCATION, LOCAL_DB_PORT)
        self.documents = self.documentClient[LOCAL_DB_NAME].documents

        ln.info("corpus has been initialized")

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
        return [bson_to_document(doc_bson) for doc_bson in self.documents.find({"_id": {"$in": idlist}})]

    def addDocuments(self, documents):
        for document in documents:
            self.addDocument(document)

    def addDocument(self, document):
        self.documents.insert(document.__dict__)  # insert the whole object to the main documents collection
