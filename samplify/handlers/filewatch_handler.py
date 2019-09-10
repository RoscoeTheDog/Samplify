from watchdog.observers import Observer
from watchdog import events
import time
import logging
import os

from samplify.app import settings
from samplify.handlers import av_handler, database_handler

import structlog

# call our logger locally
logger = structlog.get_logger('samplify.log')


class InputMonitoring(events.PatternMatchingEventHandler):
    """"""

    """
    NOTES:

        Using a custom method, we can reference and use files by observing their attributes

            Possible attributes are:
                event.event_type: 'modified' | 'created' | 'moved' | 'deleted'
                event.is_directory: True | False
                event.src_path: path/to/observed/file

        We can override  events from the FileSystemEventHandler to trigger actions

            Events possible are:
                on_any_event: if defined, will be executed for any event
                on_created: Executed when a file or a directory is created
                on_modified: Executed when a file is modified or a directory renamed
                on_moved: Executed when a file or directory is moved
                on_deleted: Executed when a file or directory is deleted.
    """

    def on_created(self, event):
        # fix backslash formatting
        path = os.path.abspath(event.src_path)

        if os.path.isdir(path):
            logger.info(f"Event: Folder {event.event_type} {path} {event.is_directory}")
            database_handler.insert_input_folder(path)

            # update our cache by ONE item!
            settings.input_cache.append(path)
            logger.info(f"Event: File added to input cache {path}")

        elif os.path.isfile(event.src_path):
            logger.info(f"Event: File {event.event_type} {path} {event.is_directory}")

            ## PYDUB METHOD (depreciated)
            # file = pd.open_audio(path)
            # sample_rate = pd.get_sample_rate(file)
            # bit_depth = pd.get_bit_depth(file)

            # FFPROBE METHOD (depreciated)
            # string_handler.open_file(event.src_path)
            # frame_rate = string_handler.frame_rate(event.src_path)
            # bit_depth = string_handler.bit_depth(event.src_path)
            # bit_rate = string_handler.bit_rate(event.src_path)

            # PyAV METHOD
            sample_format, frame_rate, bit_depth = av_handler.get_info(path)
            bit_rate = None

            database_handler.insert_file(path, frame_rate, bit_depth, bit_rate)


    def on_deleted(self, event):

        # fix backslash formatting
        path = os.path.abspath(event.src_path)

        if path in settings.input_cache:
            logger.info(f"Event: Folder {event.event_type} {path} True")
            database_handler.remove_input_folder(path)

            # update our cache by ONE item!
            settings.input_cache.remove(path)
            logger.info(f"Event: File removed from input cache {path}")

        else:
            try:
                database_handler.remove_file(event.src_path)
                logger.info(f"Event: File {event.event_type} {event.src_path} {event.is_directory}")

            except:
                logger.error(f"Event: Entry not in database {event.src_path} {event.is_directory}")


    def start_observer(self):

        observer = Observer()
        observer.schedule(InputMonitoring(), path=settings.input_path, recursive=True)
        observer.isDaemon()
        observer.start()

        try:
            while True:
                time.sleep(0)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()


class OutputMonitoring(events.PatternMatchingEventHandler):
    """"""

    """
    NOTES:

        Using a custom method, we can reference and use files by observing their attributes

            Possible attributes are:
                event.event_type: 'modified' | 'created' | 'moved' | 'deleted'
                event.is_directory: True | False
                event.src_path: path/to/observed/file

        We can override  events from the FileSystemEventHandler to trigger actions

            Events possible are:
                on_any_event: if defined, will be executed for any event
                on_created: Executed when a file or a directory is created
                on_modified: Executed when a file is modified or a directory renamed
                on_moved: Executed when a file or directory is moved
                on_deleted: Executed when a file or directory is deleted.
    """

    def on_created(self, event):

        # fix backslash formatting
        path = os.path.abspath(event.src_path)

        if event.is_directory is True:
            logger.info(f"Event: {event.event_type} {path} {event.is_directory}")
            database_handler.insert_output_folder(path)

            # update our cache by ONE item!
            settings.output_cache.append(path)
            logger.info(f"Event: Folder added to output cache {path}")

    def on_deleted(self, event):

        # fix path formatting (backslashes)
        path = os.path.abspath(event.src_path)

        if path in settings.output_cache:
            logger.info(f"Event: Folder {event.event_type} {path} True")
            database_handler.remove_output_folder(path)

            # update our cache by ONE item!
            settings.output_cache.remove(path)
            logger.info(f"Event: Folder removed from output cache {path}")



    def start_observer(self):

        observer = Observer()
        observer.schedule(OutputMonitoring(), path=settings.output_path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(0)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
