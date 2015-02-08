__author__ = 'dowling'
from holist.Holist import Holist
from plugin.sample_plugins.MockDataSource import MockDataSource, StaticMockDataSource
from plugin.sample_plugins.WordCountAnnotator import WordCountAnnotator
from plugin.sample_plugins.InvertedIndex import InvertedIndex

from klein import route

sources = [StaticMockDataSource(0), MockDataSource(0), MockDataSource(1)]
annotators = [WordCountAnnotator()]
index = InvertedIndex()
applications = [index]


route("/", methods=["GET"])(index.get_root)
route("/find_relevant", methods=["GET"])(index.find_relevant_documents)

holist = Holist(data_sources=sources, annotators=annotators, applications=applications)
holist.run()
