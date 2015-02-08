__author__ = 'dowling'

class IDataSource(object):

    def getDocuments(self):
        raise Exception("Not implemented!")

    def updateAndGetDocuments(self):
        raise Exception("Not implemented!")

    @staticmethod
    def getUniqueIdField():
        raise Exception("Not implemented! This should return a field name for which the value is unique for each "
                        "document from this source.")