from watchdog.observers import Observer
from watchdog import events
import time

from handlers import av_handler, database_handler
from app import settings
import os

from database.database_setup import InputDirectories

import structlog

import threading

# call our logger locally
logger = structlog.get_logger('samplify.log')


# def schedule_watches():
#
#     monitor_id = 0
#
#     for folder_entry in session.query(InputDirectories):
#
#         monitor_id += 1
#
#         observer = InputMonitoring()
#
#         observer.schedule_watch(path=folder_entry.folder_path)


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

    db_handler = database_handler.NewHandler()

    def on_created(self, event):

        # db_session = self.db_handler()

        path = os.path.abspath(event.src_path) # fix backslash formatting

        if os.path.isdir(path):
            logger.info(f'admin_message', msg='Folder created', path=path)
            self.db_handler.insert_input_folder(path)

            # update our cache by ONE item!
            settings.input_cache.append(path)
            # logger.info(f'admin_message', msg='input cache updated', path=path)

        elif os.path.isfile(path):
            logger.info(f'admin_message', msg='File created', path=path)

            metadata = av_handler.decode_file(path)
            self.db_handler.sort_to_table(metadata)

    def on_deleted(self, event):

        path = os.path.abspath(event.src_path) # fix backslash formatting

        # if os.path.isdir(path):
        # database_handler.remove_input_folder(path)

        if path in settings.input_cache:
            logger.info(f'admin_message', msg='File deleted', path=path)
            self.db_handler.remove_input_folder(path)

            # update our cache by ONE item!
            settings.input_cache.remove(path)
            logger.info(f"Event: File removed from input cache {path}")

        # elif os.path.isfile(path):
        #     database_handler.remove_file(path)

        else:
            try:
                self.db_handler.remove_file(event.src_path)
                logger.info(f'admin_message', msg=event.event_type, path=path)

            except:
                logger.error(f'admin_message', msg='Entry not in database', path=path)



    # def schedule_watch(self, path):
    #
    #     logger.info('user_message', msg=f'Started monitoring folder', path=path)
    #
    #     try:
    #         observer = Observer()
    #         observer.schedule(InputMonitoring(), path=path, recursive=True)
    #         observer.isDaemon()
    #         observer.start()
    #
    #         # try:
    #         #     while True:
    #         #         time.sleep(0)
    #         # except KeyboardInterrupt:
    #         #     observer.stop()
    #
    #         observer.join()
    #
    #     except Exception as e:
    #         logger.error('admin_message', msg='Could not monitor input directory', exc_info=e)

    def schedule_watches(self):

        # rows = self.db_handler.return_rows('InputDirectories')

        # for folder_entry in rows:
        #

        session = self.db_handler.return_current_session()
        
        for folder_entry in session.query(InputDirectories):

            if folder_entry.monitor is True:

                try:
                    observer = Observer()
                    observer.schedule(InputMonitoring(), path=folder_entry.folder_path, recursive=True)
                    observer.isDaemon()
                    observer.start()
                    logger.info('user_message', msg=f'Started monitoring folder', path=folder_entry.folder_path)

                except Exception as e:
                    logger.error('admin_message', msg=f'Could not monitor input directory {folder_entry.folder_path}', exc_info=e)

        def interrupt_watch():

            while True:

                try:
                    while True:
                        time.sleep(1)

                except KeyboardInterrupt:
                    observer = Observer()
                    observer.unschedule_all()  # kill all watchdog threads
                    return
                    # thread = threading.current_thread()
                    # thread.join()  # kill current keyboard monitor thread

        monitor_thread = threading.Thread(target=interrupt_watch())
        monitor_thread.isDaemon()
        monitor_thread.start()

        print('the main thread is proceeding forward')
        time.sleep(2)







        # #TODO: get the monitor thread to work in a daemon like fashion
        #
        # id = 0
        #
        # for threads in range(2):
        #
        #     # if id == 0:
        #     #     main_thread = threading.Thread()
        #     #     main_thread.isDaemon()
        #     #     main_thread.start()
        #
        #     if id == 1:
        #
        #         monitor_thread = threading.Thread(target=interrupt_watch())
        #         # monitor_thread.isDaemon()
        #         monitor_thread.start()
        #
        #     id += 1






        # def stop_thread(monitor_thread, thread_stop):
        #     thread_stop.wait()
        #     monitor_thread.join()

        # start_thread()




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
