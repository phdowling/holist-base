from celery.utils.log import get_task_logger

ln = get_task_logger(__name__)

from holist.core.annotators.Annotator import Annotator

from celery_remote_methods.remote_work import RemoteWorker, remote_task

from collections import defaultdict

import numpy as np


@RemoteWorker(remote_only=True)
class WordCountAnnotator(Annotator):
    tag = "word_counts"

    def __init__(self):
        self.model = None

    @remote_task
    def get_annotations(self, documents):
        res = []
        for document in documents:
            counts = defaultdict(int)
            for word in document.text.split():
                counts[word] += 1
            res.append(dict(counts))
        return res



