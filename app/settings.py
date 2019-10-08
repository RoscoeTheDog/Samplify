import threading
import os
import database

database_name = 'database.db'
database_path = 'sqlite:///' + os.path.dirname(database.__file__) + '/' + database_name

gpu_vendor = 'not_known'

validate_audio = True
validate_video = True

input_cache = []
output_cache = []

exception_counter = 0