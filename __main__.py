# sys modules
import threading
import argparse
import os

# logging modules
import logging
import structlog
import structlog.stdlib
import structlog.processors
from app.logging import custom_processors
from app.logging import CustomConsoleRenderer

# other modules
from handlers import database_handler, process_handler, filewatch_handler, xml_handler, file_handler, av_handler, image_handler, thread_handler
from app import settings, gpu
from database import database_setup
import time

logger = structlog.get_logger('samplify.log')

class Samplify:

    def __init__(self):
        # Reset database (for testing)
        database_setup.drop_tables()
        database_setup.create_tables()

        # Setup logging config.
        self.logging_config()

        # Gather Hardware Info/ID's.
        gpu.hardware()

        # Create our new handler types.
        self.xml_manager = xml_handler.NewHandler()
        self.thread_manager = thread_handler.NewHandler(self.xml_manager)
        self.process_manager = process_handler.NewHandler()
        self.db_manager = database_handler.NewHandler(self.process_manager)
        self.watch_manager = filewatch_handler.NewHandler(self.db_manager)
        self.file_manager = file_handler.NewHandler(self.xml_manager, self.process_manager, self.db_manager)

        # validate output directories
        self.file_manager.validate_output_tree()

        # TODO: DEPRECATED: Insert a default template.
        # self.db_manager.insert_template()
        # self.db_manager.validate_outputs()

        # Initialize manual caching of input/output trees (for watchdog recursion events).
        self.db_manager.start_input_cache()
        self.db_manager.start_output_cache()

        # Initialize multiprocessing cores.
        self.initialize_cores()

    @staticmethod
    def logging_config():

        # declare a custom formatter for our dev stream log
        stream_formatter = structlog.stdlib.ProcessorFormatter(
            processor=CustomConsoleRenderer.ConsoleRenderer(),
            # structlog.dev.ConsoleRenderer(
            # #     level_styles=
            # # {
            # #     'info:': '\033[31m',
            # #     # colorama ANSI sequences
            # #     # print(structlog.dev.ConsoleRenderer.get_default_level_styles()) for further example
            # # }
            # ),
            # foreign_pre_chain=
            # [
            #     # structlog.processors.TimeStamper(fmt='iso'),
            #     # custom_processors.OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'path', 'exc_info']),
            #     # format_exc_info,
            #     # custom_processors.add_structlog_level,
            #     # structlog.stdlib.add_log_level,
            #     # order_keys,
            #     # OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'exc_info']),
            #     structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            #
            # ],
            # keep_exc_info=True,
            # keep_stack_info=True,
        )

        # declare a custom formatter for our log file
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(sort_keys=False),
            foreign_pre_chain=
            [
                structlog.processors.TimeStamper(fmt='iso'),
                structlog.stdlib.add_log_level,
                custom_processors.OrderKeys()
                # custom_processors.OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'path', 'exc_info'])
            ],
        )

        # declare our file handler
        file_handler = logging.FileHandler('samplify.log')

        # set our custom formatter for the log file
        file_handler.setFormatter(file_formatter)

        # declare our stream handler
        stream_handler = logging.StreamHandler()
        # set our custom formatter for the stream
        stream_handler.setFormatter(stream_formatter)

        # get a standard logger
        root_logger = logging.getLogger()
        # add handlers to the standard logger
        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)

        # set the global log level
        root_logger.setLevel(logging.DEBUG)
        # set log level for stdout/stderr stream
        stream_handler.setLevel(logging.DEBUG)

        # basic structlog configuration with processor chain
        structlog.configure(
            context_class=dict,
            wrapper_class=structlog.stdlib.BoundLogger,
            processors=[
                structlog.processors.TimeStamper(fmt='iso'),
                # format_exc_info,
                structlog.processors.StackInfoRenderer(),
                custom_processors.add_structlog_level,
                # order_keys,
                custom_processors.OrderKeys(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        structlog.wrap_logger(
            root_logger,
            processors=[
                structlog.processors.TimeStamper(fmt='iso'),
                # custom_processors.add_structlog_level,
                structlog.stdlib.add_log_level,
            ]
        )

        # print(structlog.dev.ConsoleRenderer.get_default_level_styles())

    @staticmethod
    def argument_config():

        # create a parser
        parser = argparse.ArgumentParser()

        # give positional arguments
        parser.add_argument("source", help="input directory path to convert", type=str)
        parser.add_argument("destination", help="output directory path to export ", type=str)
        parser.add_argument("--search", "-s", help="words in files to search for", type=str)
        parser.add_argument("--ignore", "-i", help="words in files to ignore from search", type=str)
        parser.add_argument("--verbose", "-v", help="enable detailed verbose reports", type=str)

        # create args from parser
        args = parser.parse_args()

        if not os.path.exists(args.source):
            logger.warning('source destination invalid')

        else:
            logger.info('source: ' + args.source)

        if not os.path.exists(args.destination):
            logger.info('destination does not exist! creating new directory')
            os.mkdir(args.destination)

        else:
            logger.info('destination: ' + args.destination)

    def initialize_cores(self):
        self.process_manager.schedule_workers()
        self.process_manager.schedule_listener()

    def parse_template(self, path):
        self.xml_manager.from_path(path)

    def calculate_file_rules(self):

        self.file_operation_schedule = {}

        files = self.db_manager.get_entries_Files()

        for file in files:
            self.thread_manager.spawn_new_thread(file, self.file_operation_schedule)

        # self.db_manager.samplify()
        # self.db_manager.get_files_threaded()
        # self.db_manager.get_audio_threaded()

def main():

    # Start benchmark timer.
    timer = time.time()

    # Initialize the application.
    samplify = Samplify()

    samplify.file_manager.scan_libraries()
    samplify.calculate_file_rules()


















    # samplify.db_manager.scan_files()

    # samplify.db_manager.samplify()

    # Run a manual scan on input directories.
    # samplify.db_manager.scan_files()


    # collect all files/folders from output
    # db_handler.get_root_output(App_Settings.output_path)

    # end benchmark (output)
    # bench_output = time.time() - timer

    # print('input scan: ', bench_input)
    # print('output scan: ', bench_output)

    # filewatch_handler.schedule_watches()


    # start monitoring thread for input events
    # input_monitor = filewatch_handler.InputMonitoring()
    # input_monitor.schedule_watches()

    # start monitoring thread for output events
    # output_monitor = filewatch_handler.OutputMonitoring()
    # output_monitor.start_observer()





    # db.insert_directory(path=str)


    # args_configure()

    # bin.task_service.MyHandler()
    # bin.task_service.MyLogger()

    # bin.Samplify.create_input()
    # bin.Samplify.create_output()
    #
    # bin.create_terms.get_keywords()
    # bin.threading.start_threads()

    # except Exception as e:
    #     logger.exception(e)

    # print('number of skipped files: ', settings.exception_counter)

    print("runtime: ", time.time() - timer)

    print(time.time() - timer)

if __name__ == '__main__':
    main()