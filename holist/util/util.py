import logging
from Queue import Queue

from holist.util import config
from holist.core.model.Document import Document
from pymongo import MongoClient


from twisted.internet.threads import deferToThread

import itertools

from Queue import Empty

import datetime
loggers = []
## Central queue for log statements. Needed for sync under windows.
logQueue = Queue()


keepLogging = False
logFrame = None


def grouper(iterable, chunksize):
    """
    iterate over iterable, chunksize elements at a time. Borrowed from gensim.
    :param iterable:
    :param chunksize:
    :return:
    """
    while True:
        wrapped_chunk = [list(itertools.islice(iterable, int(chunksize)))]
        if not wrapped_chunk[0]:
            break
        yield wrapped_chunk.pop()


class PoisonPill(object):
    pass


## Used as decorator to log a functions return value, using the appropriate logger. 
def logReturnValue(function):
    def loggedFunction(*args):
        moduleName = function.__module__
        funcName = function.__name__
        moduleLogger = getModuleLogger(moduleName)
        ret = function(*args)
        moduleLogger.debug("%s returned %s...", funcName, str(ret))
        return ret
    return loggedFunction


## Starts the logging task.
def startLogging(name):
    global keepLogging
    if not keepLogging:
        keepLogging = True
        deferToThread(refreshLog, name)

def refreshLog(name):
    #get log entry (blocking)
    todaysdate = datetime.date.today()
    logfile = open(config.logFilename % (name, todaysdate), "a")
    while True:
        #check if we need to start a new file
        if datetime.date.today() != todaysdate:
            logfile.close()
            todaysdate = datetime.date.today()
            logfile = open(config.logFilename % (name, todaysdate), "a")

        logentry = None
        try:
            logentry = logQueue.get(True, 3)
        except Empty:
            pass
        if logentry:
            if isinstance(logentry, PoisonPill):
                try:
                    logfile.close()
                except:
                    pass
                return

            ## Write to file
            logfile.write(logentry+"\n")

## Schedules the logging thread to stop.
def stopLogging():
    global keepLogging
    if keepLogging:
        getModuleLogger(__name__).info("Log is being shut down via poison pill.")
        logQueue.put(PoisonPill())
    keepLogging = False


## This is a custom log handler assigned to all loggers, which writes log messages to a synchronized queue.
class QueueLogHandler(logging.Handler):
    def emit(self, record):
        s = self.format(record)
        logQueue.put_nowait(s)


## Utilitiy function used to assign logger objects to modules. 
# This also assigns a custom handler to each logger, so that logs go into both our window as well as to disk.
# Note: Logger name is cut off to fixed length so that log messages align when a monospace font is used.
def getModuleLogger(namespace):
    ln = logging.getLogger(namespace[-config.logNameLength:])
    if not len(ln.handlers):
        filehandler = QueueLogHandler()
        filehandler.setFormatter(logging.Formatter(config.logFormat))
        ln.addHandler(filehandler)

    loggers.append(ln)
    return ln


def getDatabaseConnection():
    client = MongoClient(config.dblocation, config.dbport)
    return client


def bson_to_document(bson):
    document = Document()
    document.__dict__ = bson
    return document


def moduleApiRequest(moduleName):
    ln_ = getModuleLogger(moduleName)
    def apiRequest_(render_func):
        """
        decorator that enables remote access for a resource, and sets the content-type to json
        """
        def wrapped_render(self, request):
            ln_.debug("Got request from %s for %s, args=%s" % (request.getClientIP(), request.uri, request.args))
            request.setHeader("content-type", "application/json")
            request.setHeader('Access-Control-Allow-Origin', '*')
            request.setHeader('Access-Control-Allow-Methods', 'GET')
            return render_func(self, request)
        return wrapped_render
    return apiRequest_


def ensureRequestArgs(arg_names):
    """
    return a dectorator for twisted request handlers that ensures args are present
    """
    def ensureArgsDecorator(render):
        def wrapped_render(self, request):
            for arg_name in arg_names:
                try:
                    _ = request.args[arg_name]
                except KeyError:
                    request.setResponseCode(400)
                    ln.error("Couldn't parse request arg %s." % arg_name)
                    return "Couldn't parse request arg %s." % arg_name
                return render(self, request)
        return wrapped_render
    return ensureArgsDecorator