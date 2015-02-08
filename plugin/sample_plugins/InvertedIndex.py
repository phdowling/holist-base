__author__ = 'dowling'
from holist.correlate.LinkController import entrypoint

from collections import defaultdict

from holist.correlate.Correlator import Correlator

import json

class InvertedIndex(Correlator):
    name = "index"

    def __init__(self):
        self.index = defaultdict(list)

    def on_new_documents(self, documents):
        for document in documents:
            for word, count in document.annotations["word_counts"].items():
                self.index[word].append((count, document))
                self.index[word].sort(reverse=True)

    @entrypoint("/", methods=["GET"])
    def root(self):
        return "<this is the search page html>"

    @entrypoint("/find_relevant", params=["query"], methods=["GET"])
    def find_relevant_documents(self, query):
        results = []

        for word in query.split():
            results += self.index[word].items()

        results.sort(reverse=True)
        return json.dumps([{"id": doc.holist_unique_id, "text": doc.text, "rel": score} for score, doc in results])


