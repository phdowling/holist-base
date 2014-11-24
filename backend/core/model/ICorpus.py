class ICorpus(object):
    """Interface for Corpus classes"""

    def __init__(self):
        raise Exception("Not implemented!")

    def getDescription(self):
        raise Exception("Not implemented!")

    def addDocuments(self, docs):
        raise Exception("Not implemented!")

    def addDocument(self, doc):
        raise Exception("Not implemented!")

    def __iter__(self):
        raise Exception("Not implemented!")

    def __getitem__(self, key):
        raise Exception("Not implemented!")

    def getDocuments(self, docidlist):
        raise Exception("Not implemented")

    def __len__(self):
        raise Exception("Not implemented!")