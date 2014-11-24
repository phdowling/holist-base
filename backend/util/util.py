import logging
from Queue import Queue, Empty
import datetime

from twisted.internet.threads import deferToThread
from backend.util import config
from backend.core.model.Document import Document
from pymongo import MongoClient


loggers = []
## Central queue for log statements. Needed for sync under windows.
logQueue = Queue()


keepLogging = False
logFrame = None

def getDatabaseConnection():
    client = MongoClient(config.dblocation, config.dbport)
    return client

def convertToDocument(bson):
    document = Document()
    document.__dict__ = bson
    #for strategyName in document.vectors:
    #    document.vectors[strategyName] = numpy.array(document.vectors[strategyName])
    return document

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

## Starts the logging thread.
def startLogging(name):
    global keepLogging
    if not keepLogging:
        keepLogging = True
        deferToThread(__refreshLog, name)

## Schedules the logging thread to stop.
def stopLogging():
    global keepLogging
    keepLogging = False

## This is a custom log handler assigned to all loggers, which writes log messages to a synchronized queue.
class QueueLogHandler(logging.Handler):
    def emit(self, record):
        global logQueue
        s = self.format(record) #+ '\n'
        #print s
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

ln = getModuleLogger(__name__)


def __refreshLog(name):
    global keepLogging
    #get log entry (blocking)
    todaysdate = datetime.date.today()
    logfile = open(config.logFilename % (name, todaysdate), "a")
    while keepLogging:
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
            #print logentry
            ## Write to file
            logfile.write(logentry+"\n")
    try:
        logfile.close()
    except:
        pass


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