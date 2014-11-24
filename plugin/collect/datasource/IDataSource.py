class IDataSource(object):
    def getDocuments(self):
        raise Exception("Not implemented!")
    def updateAndGetDocuments(self):
        raise Exception("Not implemented!")
    @staticmethod
    def getUniqueIdField():
        raise Exception("Not implemented! This should return a field that is unique for each doc from this source.")
