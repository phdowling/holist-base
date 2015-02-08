holist-base
===========

Holist is a framework for easily building data analysis systems and web apps. It relies on Celery for delegating tasks, Klein/Twisted for asynchronicity and web hosting, and MongoDB for data storage.

You basically implement three things to build a data analysis app on top of Holist:
* One or more DataSources: adapters that read data from somewhere, extract plain text, and return the document objects. The source may be streamed or static.
*  One or more Annotators: workers which processes and annotates each document with some extracted information (e.g. word counts, named entities, geographic coordinates..)
* Applications: Uses the annotated documents and content, as well as possibly other knowledge sources to create some view or application of the data (clustering, map view, timeline, graphs, charts, etc. would fit into this)




