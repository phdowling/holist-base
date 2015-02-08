__author__ = 'dowling'
from holist.Holist import Holist
from sample_app.plugins.MockDataSource import MockDataSource, StaticMockDataSource
from sample_app.plugins.WordCountAnnotator import WordCountAnnotator
from sample_app.plugins.InvertedIndex import InvertedIndex

sources = [StaticMockDataSource(0), MockDataSource(0), MockDataSource(1)]
annotators = [WordCountAnnotator()]
index = InvertedIndex()
applications = [index]

holist = Holist(data_sources=sources, annotators=annotators, applications=applications)

holist.run()
