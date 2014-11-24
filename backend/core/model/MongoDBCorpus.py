from backend.core.model.ICorpus import ICorpus
from backend.util.util import *

ln = getModuleLogger(__name__)


class MongoDBCorpus(ICorpus):  # This updates ONLY the articles collection
    def __init__(self):
        ln.info("initializing MongoDB corpus.")

        self.client = getDatabaseConnection()
        self.database = self.client[config.dbname]
        self.documents = self.database.documents

        ln.info("corpus has been initialized")

    def __len__(self):
        return self.documents.find().count()

    def __iter__(self):
        ln.debug("iterating through DATABASE")
        for doc_bson in self.documents.find():
            document = convertToDocument(doc_bson)
            yield document
    
    def __getitem__(self, _id):
        return convertToDocument(self.documents.find_one({"_id": _id}))
    
    def getDocuments(self, idlist):
        return [convertToDocument(doc_bson) for doc_bson in self.documents.find({"_id": {"$in": idlist}})]

    def addDocuments(self, documents):
        for document in documents:
            self.addDocument(document)

    def addDocument(self, document):
        for strategyName in document.vectors:
            document.vectors[strategyName] = list(document.vectors[strategyName])
        self.documents.insert(document.__dict__)  # insert the whole object to the main documents collection
