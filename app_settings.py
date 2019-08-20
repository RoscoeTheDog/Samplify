import threading
import os

database_name = 'database.db'

# important paths (determine what computer we're working on)
if os.path.exists('C:/Users/Admin/Desktop/Input'):
    input_path = 'C:/Users/Admin/Desktop/Input'
    output_path = 'C:/Users/Admin/Desktop/Output'

else:
    input_path = 'C:/Users/Aspen/Desktop/Input'
    output_path = 'C:/Users/Aspen/Desktop/Output'


gpu_vendor = ''

validate_audio = True
validate_video = True

exception_counter = 0

config_path = 'C:/Users/Admin/Desktop/'

default_name_searchby_directory = False

input_cache = []
output_cache = []

num_threads = 1
thread_exec_instances = []
master_thread_list = []

exclusions = []
exclusion_set = []
exclusion_iter = 0

keywords = []
keyword_iter = 0

input_path_contents = []
input_path_contents_basename = []
output_path_contents = []
output_path_contents_basename = []

ext_type = '.wav'
conv_type = 'wav'
bit_depth = 3  # 1-4. 1=8 2=16 3=24 4=32
target_dbfs = 0

debug_timer = 1.5
file_check_timer = .10

printUserEnabled = False
printDebuggerEnabled = True

printUser = str
printDebug = str

try:
    from local_settings import *
except ImportError:
    pass