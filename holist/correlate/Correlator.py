__author__ = 'dowling'


class Correlator(object):

    def onNewDocuments(self, documents):
        raise AttributeError("Not implemented by this strategy. Override to receive newly available documents.")
