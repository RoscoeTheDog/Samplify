import threading
import os
from samplify import database

database_name = 'database.db'
database_path = 'sqlite:///' + os.path.dirname(database.__file__) + '/' + database_name

gpu_vendor = str

validate_audio = True
validate_video = True

input_cache = []
output_cache = []

exception_counter = 0