import os
import database

platform = 'unknown'
user_name = 'unknown'
gpu_vendor = 'unknown'

database_name = 'database.db'
database_path = 'sqlite:///' + os.path.dirname(database.__file__) + '/' + database_name

monitor_all_inputs = True

input_cache = []
output_cache = []

validate_audio = True
validate_video = True

exception_counter = 0