__author__ = 'dowling'
from celery import Celery
app = Celery('holist_tasks', backend='amqp', broker='amqp://')
from celery_remote_methods import remote_work
remote_work.initialize(app)

from sample_app.plugins import MockDataSource
from sample_app.plugins import WordCountAnnotator