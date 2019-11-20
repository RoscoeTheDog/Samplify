from watchdog.observers import Observer
from watchdog import events
from app import settings
import os
from multiprocessing import Queue
import inspect

from database.database_setup import InputDirectories, InputMonitoringExclusions

import structlog

# call our logger locally
logger = structlog.get_logger('samplify.log')


signal_queue = Queue()


# Manages watchdog observer threads.
class NewHandler():

    def __init__(self, db_manager):
        self.db_manager = db_manager  # session object unpicklable

    # Pickling exclusions.
    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()

        # Remove the unpicklable entries
        del state['db_manager']
        return state

    def schedule_all_watches(self):

        # Filter out duplicate children paths to prevent re-occurring tasks from numerous threads
        parent_list = self.db_manager.filter_children_directories()

        # Query the InputDirectories Table.
        for folder_entry in self.db_manager.session.query(InputDirectories):
            # Check to see if folder-monitoring is enabled.
            if folder_entry.monitor is True:
                # Check if path is a parent, all child directories will be dropped (since monitoring recursively).
                if folder_entry.folder_path in parent_list:
                    self.schedule_watch(folder_entry.folder_path)

    def schedule_watch(self, path):

        # try to create a watch on the parent directory.
        try:
            observer = Observer()
            observer.schedule(InputMonitoring(), path=path, recursive=True)
            observer.setDaemon(True)
            observer.start()
            logger.info('user_message', msg=f'Started monitoring folder', path=path)

        except Exception as e:
            logger.error('admin_message', msg=f'Could not monitor input directory {path}',
                         exc_info=e)

    def watch_listener(self):
        logger.info("admin_message", msg="Started watch listener")

        while not signal_queue.empty():

            signal = signal_queue.get()

            path = os.path.abspath(signal.src_path)

            drop_list = []

            # TODO: Signal an update of the drop-list to consumer thread when user inserts field in db
            for row in self.db_manager.session.query(InputMonitoringExclusions):
                drop_list.append(os.path.abspath(row.folder_path))

            # check drop events
            for directory in drop_list:
                if directory not in path:

                    if signal.event_type == 'created':

                        if os.path.isdir(path):
                            logger.info(f'admin_message', msg='Folder created', path=path)

                            # update our cache file-tree with the item
                            settings.input_cache.append(path)

                        elif os.path.isfile(path):
                            logger.info(f'admin_message', msg='File created', path=path)
                            self.db_manager.decode_file(path)

                            # metadata = av_handler.decode_file(path)
                            # self.db_manager.sort_to_table(metadata)

                    if signal.event_type == 'modified':
                        pass

                    if signal.event_type == 'moved':
                        pass

                    if signal.event_type == 'deleted':

                        # Note: Check input_cache (list of directories) if path exists.
                        #       This checks to see if path is a folder

                        if path in settings.input_cache:
                            logger.info(f'admin_message', msg='Folder deleted', path=path)
                            self.db_manager.remove_input_folder(path)

                            # update the list-cache by the one item that was changed.
                            settings.input_cache.remove(path)

                        else:
                            try:
                                self.db_manager.remove_file(path)
                                logger.info(f'admin_message', msg='File deleted', path=path)

                            except Exception as e:
                                logger.error(f'admin_message', msg='Entry not in database', path=path, exc_info=e)



# manages watchdog event handling & signaling to threads
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

    # def __init__(self):
    #     super().__init__()
    #     self.drop_list = []
    #
    # def listener(self):
    #
    #     while True:
    #
    #         self.drop_list = []
    #
    #         update = drop_list_queue.get()
    #
    #         try:
    #             for directory in update:
    #                 self.drop_list.append(directory)
    #
    #         except Exception as e:
    #             logger.error('admin_message', msg='Could not receive from communicated thread', exc_info=e)

    # class Task(Enum):
    #
    #     def __init__(self, event):
    #         self.event = event
    #
    #         self.on_any_event = self.event.event_type
    #         self.on_created = object
    #         self.on_modified = object
    #         self.on_deleted = object

    def on_created(self, event):

        path = os.path.abspath(event.src_path)  # normalize backslash formatting

        # # get method name from within method (using inspect)
        # _name = inspect.currentframe().f_code.co_name
        #
        # # create a signal object (tuple)
        # signal = (_name, event)

        # send the task to the consumer thread
        signal_queue.put(event)

        # # for folder_entry in session.query(InputMonitoringExclusions):
        # #
        # #     if path in folder_entry:
        # #         drop_call = True
        # #
        # # if not self.drop_call:
        #
        #
        #
        #
        #
        #
        # if os.path.isdir(path):
        #     logger.info(f'admin_message', msg='Folder created', path=path)
        #
        #     # update our cache by ONE item!
        #     settings.input_cache.append(path)
        #
        #
        #
        #
        #
        #
        # elif os.path.isfile(path):
        #     logger.info(f'admin_message', msg='File created', path=path)
        #
        #     # metadata = av_handler.decode_file(path)
        #     # self.db_handler.sort_to_table(metadata)


    def on_deleted(self, event):

        path = os.path.abspath(event.src_path)  # normalize backslash formatting

        # get method name from within method (using inspect)
        _name = inspect.currentframe().f_code.co_name

        # create a signal object (tuple)
        signal = (_name, event)

        # send the task to the consumer thread
        signal_queue.put(event)

        # session = self.db_handler.return_current_session()

        # path = os.path.abspath(event.src_path) # fix backslash formatting
        #
        #
        #
        #
        #
        #
        # # for folder_entry in session.query(InputMonitoringExclusions):
        # #
        # #     if path in folder_entry:
        # #         drop_call = True
        # #
        # # if not self.drop_call:
        #
        #
        #
        #
        #
        #
        #
        # # if os.path.isdir(path):
        # # database_handler.remove_input_folder(path)
        #
        # if path in settings.input_cache:
        #     logger.info(f'admin_message', msg='File deleted', path=path)
        #     self.db_handler.remove_input_folder(path)
        #
        #     # update our cache by ONE item!
        #     settings.input_cache.remove(path)
        #     logger.info(f"Event: File removed from input cache {path}")
        #
        # # elif os.path.isfile(path):
        # #     database_handler.remove_file(path)
        #
        # else:
        #     try:
        #         self.db_handler.remove_file(event.src_path)
        #         logger.info(f'admin_message', msg=event.event_type, path=path)
        #
        #     except:
        #         logger.error(f'admin_message', msg='Entry not in database', path=path)


# class OutputMonitoring(events.PatternMatchingEventHandler):
#     """"""
#
#     """
#     NOTES:
#
#         Using a custom method, we can reference and use files by observing their attributes
#
#             Possible attributes are:
#                 event.event_type: 'modified' | 'created' | 'moved' | 'deleted'
#                 event.is_directory: True | False
#                 event.src_path: path/to/observed/file
#
#         We can override  events from the FileSystemEventHandler to trigger actions
#
#             Events possible are:
#                 on_any_event: if defined, will be executed for any event
#                 on_created: Executed when a file or a directory is created
#                 on_modified: Executed when a file is modified or a directory renamed
#                 on_moved: Executed when a file or directory is moved
#                 on_deleted: Executed when a file or directory is deleted.
#     """
#
#     def on_created(self, event):
#
#         # fix backslash formatting
#         path = os.path.abspath(event.src_path)
#
#         if event.is_directory is True:
#             logger.info(f"Event: {event.event_type} {path} {event.is_directory}")
#             database_handler.insert_output_folder(path)
#
#             # update our cache by ONE item!
#             settings.output_cache.append(path)
#             logger.info(f"Event: Folder added to output cache {path}")
#
#     def on_deleted(self, event):
#
#         # fix path formatting (backslashes)
#         path = os.path.abspath(event.src_path)
#
#         if path in settings.output_cache:
#             logger.info(f"Event: Folder {event.event_type} {path} True")
#             database_handler.remove_output_folder(path)
#
#             # update our cache by ONE item!
#             settings.output_cache.remove(path)
#             logger.info(f"Event: Folder removed from output cache {path}")
#
#
#
#     def start_observer(self):
#
#         observer = Observer()
#         observer.schedule(OutputMonitoring(), path=settings.output_path, recursive=True)
#         observer.start()
#
#         try:
#             while True:
#                 time.sleep(0)
#         except KeyboardInterrupt:
#             observer.stop()
#
#         observer.join()
