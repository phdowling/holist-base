holist-base
===========

Holist is a framework for easily building data analysis systems and web apps. It relies on Celery for delegating tasks, Klein/Twisted for asynchronicity and web hosting, and MongoDB for data storage.

You basically implement three things to build a data analysis app on top of Holist:
* DataSources: adapters that read or fetch data from somewhere, extract plain text, and return the document objects. The source may be streamed or static.
* Annotators: workers which processes and annotates each document with some extracted information (e.g. word counts, named entities, geographic coordinates..)
* Applications: Uses the annotated documents and content, as well as possibly other knowledge sources to create some view or application of the data (clustering, map view, timeline, graphs, charts, etc. would fit into this)

The example in `sample_plugin` implements a simple search application based on word counts, on a random data source. It contains example classes for each of the concepts listed above. It uses some default settings for where to serve content, defined in `holist/util/config.py`

To run the example, you first have to start a MongoDB instance, and Celery workers. For me, this is done via 
```bash
> sudo mongod &
> celery -A example_celery_tasks_main worker --loglevel=info
```
Then, start Holist using 
```bash
> python holist_example.py
```
By default, the app should then be served on `http://localhost:8080/`.


