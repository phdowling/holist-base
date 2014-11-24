__author__ = 'dowling'

class ILinkStrategy(object):
    def getApiResource(self):
        raise Exception("Not implemented! Should provide a resource representing this strategy's API.")
    def getApiPath(self):
        raise Exception("Not implemented! Should provide the path through which this strategy's API is accessed.")