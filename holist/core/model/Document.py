class Document(object):
    def __init__(self, text=None):
        self.text = text
        self.annotations = dict()