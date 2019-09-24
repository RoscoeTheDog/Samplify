from eliot import *
from eliot.parse import Parser
import eliot
import eliottree
import json

# declare our file path as a variable
log_path = 'C:\\Users\\Aspen\\Google Drive\\1. Software Engineering\\GitHub\\Samplify\\samplify.log'

# point to file path
to_file(open(log_path, 'w+'))

# write a basic log message
Message.log(key='test message')

# load messages. Takes logpath *after* it's been pointed to??
def load_messages(logfile_path):
   for line in open(logfile_path):
       yield json.loads(line)

# parse messages. Takes logpath as well?
def parse(logfile_path):
    for task in Parser.parse_stream(load_messages(logfile_path)):
        print("Root action type is", task.root().action_type)

# run the functions
load_messages(log_path)
parse(log_path)  # error thrown here