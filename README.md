holist-base
===========

Holist is a platform for document analysis. This repository holds the basic structure of the system featuring the main controllers, wrappers and sample data sources and strategies.

Plug-ins to extend this skeleton can be grouped into the following:
- data source (collect layer) - an adapter that reads data from somewhere, extracts plain text, and returns the documents. The source may be streamed or static.
- annotator (core layer) - a model or algorithm that processes and annotates each document with some extracted information (e.g. named entities, LSA vector, geographic coordinates..)
- interface or visualization (link layer) - provides some view of the data by using different annotations and content, as well as possibly other knowledge sources (e.g. clustering, map view, timeline, graphs, charts..)


