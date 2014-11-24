class IStrategy(object):
    def __init__(self):
        raise Exception("Not implemented!")

    def getNumFeatures(self):
        return Exception("Not implemented!")

    def handleDocument(self, document):
        raise Exception("Not implemented!")

    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
