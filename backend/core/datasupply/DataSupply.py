from backend.util.util import *
ln = getModuleLogger(__name__)
import requests
import json


class MongoDataSupply(object):  # This handles ONLY the new_documents collection
    """
    this is used to fetch documents from the database, which they're collected by the separate datacollector node.
    """
    def __init__(self):
        self.client = getDatabaseConnection()
        self.database = self.client[config.dbname]
        #self.database.authenticate(UNAME, PASSWD)
        self.newDocumentsCollection = self.database.new_documents

    def connect(self):
        try:
            ln.info("attempting to connect to collector node at %s:%s", config.collectNodeIP, config.collectNodePort)
            data = {"ip": config.holistcoreurl, "port": config.holistcoreport}
            res = requests.post("http://" + config.collectNodeIP+":"+str(config.collectNodePort)+"/register_listener",
                                data=data)
            success = json.loads(res.text)["result"] == "success"
            assert success
            ln.info("successfully connected.")
            return success
        except Exception, e:
            ln.exception("couldn't connect to collector!")
            return False

    def getNewDocuments(self):
        newDocuments = [convertToDocument(bson) for bson in self.newDocumentsCollection.find()]
        ids = [doc._id for doc in newDocuments]
        self.newDocumentsCollection.remove({"_id": {"$in": ids}})
        return newDocuments

    def countNewDocuments(self):
        return self.newDocumentsCollection.find().count()
