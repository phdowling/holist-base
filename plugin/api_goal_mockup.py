__author__ = 'dowling'

from holist.Holist import Holist
from holist.collect.datasource.IDataSource import DataSource
from holist.core.annotators.Annotator import Annotator
from holist.correlate.Correlator import Correlator
from holist.correlate.LinkController import entrypoint

from gensim.corpora import Dictionary
import feedparser
from collections import defaultdict

from celery.contrib.methods import task
from celery_remote_methods import RemoteWorker, remote_task


@RemoteWorker
class RSSDataSource(DataSource):
    def __init__(self, url):
        self.url = url

    @remote_task
    def update_and_get_documents(self):
        docs = feedparser.parse(self.url)
        return docs


@RemoteWorker
class BagOfWordsAnnotator(Annotator):
    annotation_tag = "bow"

    def __init__(self):
        self.dictionary = Dictionary("word_ids.txt")

    @remote_task
    def get_annotations(self, documents):
        return [self.dictionary.doc2bow(doc) for doc in documents]


class InvertedIndex(Correlator):
    name = "index"

    def __init__(self):
        self.dictionary = Dictionary("word_ids.txt")
        self.index = defaultdict(list)

    def on_new_documents(self, documents):
        for document in documents:
            for word_id, count in document.annotations["bow"]:
                self.index[word_id].append((count, document))
                self.index[word_id].sort(reverse=True)

    @entrypoint("/", methods=["GET"])
    def root(self):
        return "<this is the search page html>"

    @entrypoint("/find_relevant", params=["query"], methods=["GET"])
    def find_relevant_documents(self, query):
        bow = self.dictionary.doc2bow(query)

        results = []
        for word_id, q_word_count in bow:
            for doc_word_count, document in self.index[word_id]:
                results.append((q_word_count * doc_word_count, document))
        results.sort(reverse=True)
        return [{"id": doc._id, "text": doc.text, "relevance": score} for score, doc in results]


if __name__ == "__main__":
    source = RSSDataSource("http://feeds.reuters.com/reuters/businessNews")
    bow_annotator = BagOfWordsAnnotator()
    inv_index = InvertedIndex()

    app = Holist(data_sources=[source], annotators=[bow_annotator], correlators=[inv_index])
    app.run("localhost", "8080")

def test():
    import requests
    requests.get("localhost:8080/index/find_relevant...")

