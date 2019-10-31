import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import os

# setup some basic config stuff
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

event_handler = LoggingEventHandler()

if __name__ == "__main__":

    folders = ['C:\\folder1', 'C:\\folder2']
    num = 0

    for f in folders:

        if not os.path.exists(f):

            try:
                os.mkdir(f)

            except:
                print('Error: could not make directory for some reason.')

        print(f'starting thread: {num}')

        observer = Observer()
        observer.schedule(event_handler, f, recursive=True)
        observer.start()
        # observer.join()

        num += 1

    try:
        while True:
            pass

    except KeyboardInterrupt:

        print('interrupted')

        observer = Observer()
        observer.unschedule_all()

        print('all threads killed')