updateLogMaxWaitTime = 10
logFilename = "log/%s_holistserver%s.log"
logNameLength = 18
logFormat = '%(asctime)s %(levelname)-8s %(name)-18s: %(message)s'

showDebugLogs = True

### COLLECT
collectNodeIP = "localhost"
collectNodePort = 12137
data_source_update_timeout = 30  # seconds
memorize_all_documents = True

collect_update_wait_time = 10  # seconds


### CORE
update_new_documents_threshold = 25
update_minimum_wait_time = 60 * 3
annotators_chunk_size = 1000
core_update_wait_time = 10  # seconds

### APPLICATION



### DATABASE
dblocation = "localhost"
dbport = 27017
dbname = "holist"

### ELASTICSEARCH
eslocation = "localhost"
esport = "9200"
