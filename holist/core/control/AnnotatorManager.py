from holist.util.util import *

ln = getModuleLogger(__name__)

from toposort import toposort


from Queue import Queue


class AnnotatorManager(object):
    def __init__(self, controller, strategies):
        self.resultQueue = Queue()
        self.controller = controller
        self.annotators = {}
        self.dependency_graph = {}
        for strategy in strategies:
            self.registerAnnotator(strategy)

    def queueCallback(self, results):
        self.resultQueue.put(results)

    def registerAnnotator(self, annotator):
        annotator.dependsOn = getattr(annotator, "dependsOn", lambda: [])

        self.dependency_graph[annotator.tag] = set(annotator.dependsOn())
        self.annotators[annotator.tag] = annotator
        ln.info("Registered annotator %s", annotator)

    def run_annotators(self, document_chunk):
        for group in toposort(self.dependency_graph):
            current_results = []
            for annotation_tag in group:
                annotator = self.annotators[annotation_tag]
                #task_d = [{dep: doc.annotations[dep] for dep in annotator.dependsOn()} for doc in document_chunk]
                task_data = document_chunk
                async_res = annotator.get_annotations_delay(task_data)
                current_results.append((annotation_tag, async_res))

            # todo: we can save time by not waiting for all strategies, but only ones that are dependencies
            for annotation_tag, async_result in current_results:
                document_annotations = async_result.get()
                assert len(document_chunk) == len(document_annotations), "Annotator %s did not return the correct number of annotations!"

                if async_result.status != 'SUCCESS':
                    ln.error("Annotator %s threw an error!", annotation_tag)
                    if isinstance(async_result.result, Exception):
                        raise async_result.result

                for annotation, document in zip(document_annotations, document_chunk):
                    document.annotations[annotation_tag] = annotation

        return document_chunk

