__author__ = 'dowling'
from holist.Holist import Holist
from plugin.sample_plugins.MockDataSource import MockDataSource, StaticMockDataSource
from plugin.sample_plugins.WordCountAnnotator import WordCountAnnotator

sources = [StaticMockDataSource(0), MockDataSource(0), MockDataSource(1)]
annotators = [WordCountAnnotator()]


holist = Holist(data_sources=sources, annotators=annotators)
holist.run("localhost", 8081)
