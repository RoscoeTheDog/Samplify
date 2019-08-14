import os
import settings

def create_input():
    # Check to see if exists
    if not os.path.exists(settings.input_path):
        os.makedirs(settings.input_path)