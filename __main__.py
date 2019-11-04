import argparse
import os
import logging
import time
import structlog
from structlog.stdlib import *
from structlog.processors import *
from pythonjsonlogger import jsonlogger
import sys

from handlers import database_handler, filewatch_handler
from app import input, output, settings, gpu, custom_processors

logger = structlog.get_logger('samplify.log')


class Samplify():

    def __init__(self):
        self.db_manager = database_handler.NewHandler()
        self.filewatch_manager = filewatch_handler.NewHandler(self.db_manager)

        # insert default template
        self.db_manager.insert_template()

        # initialize input/output cache (for watchdog)
        self.db_manager.start_input_cache()
        self.db_manager.start_output_cache()

    @staticmethod
    def logging_config():

        # declare a custom formatter for our dev stream log
        stream_formatter = structlog.stdlib.ProcessorFormatter(
            #TODO: Create custom ConsoleRenderer that pops() in desired order
            # and formats in corresponding colors.
            processor=structlog.dev.ConsoleRenderer(
            #     level_styles=
            # {
            #     'info:': '\033[31m',
            #     # colorama ANSI sequences
            #     # print(structlog.dev.ConsoleRenderer.get_default_level_styles()) for further example
            # }
            ),
            foreign_pre_chain=
            [
                TimeStamper(fmt='iso'),
                # custom_processors.OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'path', 'exc_info']),
                # format_exc_info,
                # add_structlog_level,
                # order_keys,
                # OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'exc_info']),
                # structlog.stdlib.ProcessorFormatter.wrap_for_formatter,

            ],
            # keep_exc_info=True,
            # keep_stack_info=True,
        )

        # declare a custom formatter for our log file
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(sort_keys=False),
            foreign_pre_chain=
            [
                TimeStamper(fmt='iso'),
                structlog.stdlib.add_log_level,
                # custom_processors.OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'path', 'exc_info'])
            ],
        )

        # declare our file handler
        file_handler = logging.FileHandler('samplify.log')

        # set our custom formatter for the log file
        file_handler.setFormatter(file_formatter)  # In theory, jsonlogger.JsonFormatter() could be used with custom override methods which may allow us to re-order keys

        # declare our stream handler
        stream_handler = logging.StreamHandler()
        # set our custom formatter for the stream
        stream_handler.setFormatter(stream_formatter)

        # get a standard logger
        root_logger = logging.getLogger()
        # add handlers to standard logger
        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)

        # set global log level
        root_logger.setLevel(logging.DEBUG)
        # set log level for stdout/stderr stream
        stream_handler.setLevel(logging.DEBUG)

        # basic structlog configuration with processor chain
        structlog.configure(
            context_class=dict,
            wrapper_class=structlog.stdlib.BoundLogger,
            processors=[
                TimeStamper(fmt='iso'),
                # format_exc_info,
                custom_processors.add_structlog_level,
                # order_keys,
                custom_processors.OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'path', 'exc_info']),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        structlog.wrap_logger(
            root_logger,
            processors=[
                TimeStamper(fmt='iso'),
                structlog.stdlib.add_log_level,
            ]
        )


        # print(structlog.dev.ConsoleRenderer.get_default_level_styles())

    @staticmethod
    def args_configure():

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

    @staticmethod
    def validate_directories():
        output.validate_directories()

    def start_watchdog(self):
        self.filewatch_manager.schedule_all_observers()
        self.filewatch_manager.start_db_threaded()





def main():

    # class instance
    samplify = Samplify()

    # start logging
    samplify.logging_config()

    # configure args
    # samplify.args_configure()

    # configure hardware
    gpu.hardware()

    # validate output folders
    samplify.validate_directories()

    # run a manual scan on input directories.
    samplify.db_manager.scan_files()

    # start watchdog threading
    samplify.start_watchdog()

    # start benchmark (input)
    timer = time.time()

    # # run a manual scan on input directories.
    # samplify.db_manager.scan_files()

    # end benchmark (output)
    bench_input = time.time() - timer

    # print benchmark
    print('input scan: ', bench_input)


    # db_startup.start_input_cache()

    # initialize file monitor cache
    # database_handler.start_input_cache()
    # database_handler.start_output_cache()

    # # start benchmark (input)
    # timer = time.time()

    # # scan all input folders
    # input.scan_files()
    # time.sleep(2)

    # stdout, stderr = av_handler.ffprobe('C:\\OpenCV 4.1.0\\opencv\\sources\\doc\\acircles_pattern.png')
    # print(stdout)
    # av_handler.parse_ffprobe(stdout, stderr)

    # end benchmark (input)
    # bench_input = time.time() - timer

    # start benchmark (output)
    # timer = time.time()

    # SAMPLIFY!
    # database_handler.samplify()

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

    print('number of skipped files: ', settings.exception_counter)


if __name__ == '__main__':
    main()