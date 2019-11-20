import argparse
import os
import structlog
from structlog.stdlib import *
from structlog.processors import *
from handlers import database_handler, process_handler, filewatch_handler
from app import settings, gpu
from app.logging import custom_processors

logger = structlog.get_logger('samplify.log')


class Samplify:

    def __init__(self):
        # Create our new handler types.
        self.db_manager = database_handler.NewHandler()
        self.process_manager = process_handler.NewHandler()

        # Insert a default template.
        self.db_manager.insert_template()

        # Initialize input/output cache (for watchdog).
        self.db_manager.start_input_cache()
        self.db_manager.start_output_cache()

        # Here is where the exception is thrown.
        self.filewatch_manager = filewatch_handler.NewHandler(self.db_manager)


    @staticmethod
    def logging_config():

        # render_window = structlog.dev.ConsoleRenderer()
        #
        # render_window.__call__ = Samplify.test_call

        from app.logging import CustomConsoleRenderer

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
            foreign_pre_chain=
            [
                TimeStamper(fmt='iso'),
                # custom_processors.OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'path', 'exc_info']),
                # format_exc_info,
                # add_structlog_level,
                # order_keys,
                # OrderKeys(keys=['timestamp', 'level', 'event', 'msg', 'exc_info']),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,

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
                TimeStamper(fmt='iso'),
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

    def initialize_workers(self):
        self.process_manager.schedule_workers()
        self.process_manager.schedule_listener()


def main():

    # App instance.
    samplify = Samplify()

    # Start logging.
    samplify.logging_config()

    # TODO: (Re)configure args.
    # samplify.args_configure()

    # Get hardware type/ID.
    gpu.hardware()

    # Validate output folders.
    samplify.db_manager.validate_outputs()

    # Spawn multi-core worker processes.
    samplify.initialize_workers()

    # Start benchmark timer (input).
    timer = time.time()

    # Run a manual scan on input directories.
    samplify.db_manager.scan_files()

    time.sleep(30)









    # # Start watchdog threading.
    # samplify.initialize_filewatches()
    #
    # samplify.filewatch_manager.add_decoder_task(print('hello world'))
    #
    # # End input benchmark timer
    # print(time.time() - timer)













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


if __name__ == '__main__':
    main()