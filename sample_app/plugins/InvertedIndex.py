__author__ = 'dowling'
from holist.util import config
from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.api import route

from collections import defaultdict

from holist.application.Correlator import Correlator

import json


class InvertedIndex(Correlator):
    name = "index"

    def __init__(self):
        self.index = defaultdict(list)


    def on_new_documents(self, documents):
        ln.info("on_new_documents called!")
        for document in documents:
            for word, count in document.annotations["word_counts"].items():
                self.index[word].append((count, document))
                self.index[word].sort(reverse=True)

    @route("/", methods=["GET"])
    def get_root(self, request):
        return """<!DOCTYPE html>
                    <html>
                       <body>
                          <form action="http://%s:%s/find_relevant" method="get">
                             <p>
                                Search! <input name="query" value="..." />
                             </p>
                             <p>
                                <input type="submit" />
                             </p>
                          </form>
                       </body>
                    </html>
                """ % (config.app_ip, config.app_port)

    @route("/find_relevant", methods=["GET"])
    def find_relevant_documents(self, request):
        query = request.args["query"][0]
        ln.debug("got query: %s", query)

        results = []

        for word in query.split():
            results += self.index[word]

        results = list(set(results))

        results.sort(reverse=True)
        return json.dumps([{"id": doc.holist_unique_id, "text": doc.text, "rel": score} for score, doc in results])



