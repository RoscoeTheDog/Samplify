import argparse
import os

# logging modules
import logging
import structlog
import structlog.stdlib
import structlog.processors
from app.logging import custom_processors
from app.logging import custom_console_renderer

# other modules
from handlers import database_handler, process_handler, watch_handler, xml_handler, file_handler, av_handler, \
    image_handler, thread_handler, rules
from app import platform, gpu, environment
from database import database_setup
import time
import pprint
import datetime

logger = structlog.get_logger('samplify.log')


class Application:

    def __init__(self):
        # initialize logging configuration
        self.logging_config()

        # initialize user environment
        environment.init_environment()

        # get graphics card info
        gpu.get_gpu()

        # wipe old database (use for debug/development testing)
        database_setup.drop_tables()
        database_setup.create_tables()

        # Initializes handler types
        self.template_manager = xml_handler.NewHandler()
        self.thread_manager = thread_handler.NewHandler(self.template_manager)
        self.process_manager = process_handler.NewHandler()
        self.db_manager = database_handler.NewHandler(self.process_manager)
        self.watch_manager = watch_handler.NewHandler(self.db_manager)
        self.file_manager = file_handler.NewHandler(self.template_manager, self.process_manager, self.db_manager)

        # TODO: invoke output validation upon parsing of template
        #  (currently creates default children in existing output directory).

        # validate default environment output structure & create directories as needed
        self.file_manager.validate_output_directories()

        # TODO: DEPRECATED: Insert a default template to Table (now handled in XML)
        # self.db_manager.insert_template()
        # self.db_manager.validate_outputs()

        # Initialize manual caching of input/output trees (for watchdog recursion events)
        self.db_manager.initialize_input_cache()
        self.db_manager.initialize_output_cache()

        # Initialize multiprocessing cores
        self.initialize_cores()

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

    @staticmethod
    def logging_config():
        """
        Structured logging configuration setup. With the correct configuration, we can also use this to
        pipe messages to user via GUI.

        https://www.structlog.org/en/stable/getting-started.html for more info.
        """

        # configure our *structlog* configuration with a processor chain
        structlog.configure(
            context_class=dict,
            wrapper_class=structlog.stdlib.BoundLogger,
            processors=[
                structlog.processors.TimeStamper(fmt='iso'),
                # format_exc_info,
                structlog.processors.StackInfoRenderer(),
                custom_processors.add_structlog_level,
                # order_keys,
                custom_processors.OrderKeys(),  # custom processor. orders keys so it is easier to visualize
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        # custom format renderer for the console output stream. Can change colors and styles if desired.
        stream_formatter = structlog.stdlib.ProcessorFormatter(
            processor=custom_console_renderer.ConsoleRenderer(),

            # Below is the default console renderer, as defined by the structlog devs.
            #
            #   Note: Had issues displaying and logging exception info.
            #       Took source and revised a custom version of it.
            #       Old configuration commented out for reference.

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

        # custom formatter for the log file
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

        # file handler. responsible for writing stuff to log
        file_handler = logging.FileHandler('samplify.log')

        # set formatter for file handler. responsible for formatting the log file (example: json output)
        file_handler.setFormatter(file_formatter)

        # stream handler. responsible for piping stuff to console.
        stream_handler = logging.StreamHandler()

        # set formatter for the stream handler. responsible for formatting the output stream (example: colors)
        stream_handler.setFormatter(stream_formatter)

        # create a standard logger from python module
        root_logger = logging.getLogger()

        # apply handlers to the standard logger
        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)

        # set a global log level
        root_logger.setLevel(logging.DEBUG)

        # set log level for stdout/stderr stream
        stream_handler.setLevel(logging.INFO)

        # wrap the standard logger from python lib for structlog lib use.
        structlog.wrap_logger(
            root_logger,
            processors=[
                structlog.processors.TimeStamper(fmt='iso'),
                # custom_processors.add_structlog_level,
                structlog.stdlib.add_log_level,
            ]
        )

    def initialize_cores(self):
        self.process_manager.schedule_workers()
        self.process_manager.schedule_listener()

    def run_once(self):

        operations = []

        output_libraries = self.template_manager.return_dict()
        files = self.db_manager.get_entries_Files()

        if files:  # check for null/empty library directory
            for file in files:

                for directory in output_libraries.get('outputDirectories'):
                    entry = {}

                    """
                        governor behavior:
                            user can choose between AND/OR for the output directory ruleset
                            
                            Rules set to AND will check to make sure all rules are true, then are added to the output Queue
                            Rules set to OR will check to make sure *any* rules are true, then are added to the output Queue
                    """

                    if directory.get('comparison') == 'AND':

                        """
                            Algorithm Notes:
                        
                            we assume that if the XML template only contains a rule if it needs to be computed for the output
                            otherwise, we can ignore adding that parameter to the operations list entirely.
                            
                            if an output parameter is not specified and is still needed for any conversion output, 
                            it will fallback to the input files parameters.
                        """

                        while True:  # Do not check for empty dict entry value! enforce all method calls

                            if directory.get('expression'):
                                temp = rules.contains_expression(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('extensions'):
                                temp = rules.contains_extensions(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('datetimeStart'):
                                temp = rules.between_datetime(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('containsAudio'):
                                temp = rules.contains_audio(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('containsVideo'):
                                temp = rules.contains_video(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('containsImage'):
                                temp = rules.contains_image(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('audioSampleRate'):
                                temp = rules.set_audio_sample_rate(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('audioFormat'):
                                temp = rules.set_audio_format(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('audioBitrate'):
                                temp = rules.set_audio_bit_rate(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('audioChannels'):
                                temp = rules.set_audio_channels(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('audioNormalize'):
                                temp = rules.set_audio_normalize(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('audioBitDepth'):
                                temp = rules.set_audio_bit_depth(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('videoOutputContainer'):
                                temp = rules.set_video_output_container(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('videoHeight'):
                                temp = rules.set_video_height(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('videoWidth'):
                                temp = rules.set_video_width(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('videoDuration'):
                                temp = rules.set_video_duration(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('videoFrameRate'):
                                temp = rules.set_video_frame_rate(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('videoPixFormat'):
                                temp = rules.set_video_frame_rate(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('imageFormat'):
                                temp = rules.set_image_format(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('imageHeight'):
                                temp = rules.set_image_height(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('imageWidth'):
                                temp = rules.set_image_width(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            if directory.get('imageMode'):
                                temp = rules.set_image_mode(file, directory)
                                if not temp:
                                    break
                                else:
                                    entry.update(temp)

                            # when done checking conditions, add the entry to the operations dictionary if not null
                            if entry:
                                operations.append(entry)

                            break

                    if directory.get('comparison') == 'OR':

                        if directory.get('expression'):
                            entry.update(rules.contains_expression(file, directory))

                        if directory.get('extensions'):
                            entry.update(rules.contains_extensions(file, directory))

                        if directory.get('datetimeStart'):
                            entry.update(rules.between_datetime(file, directory))

                        if directory.get('containsAudio'):
                            entry.update(rules.contains_audio(file, directory))

                        if directory.get('containsVideo'):
                            entry.update(rules.contains_video(file, directory))

                        if directory.get('containsImage'):
                            entry.update(rules.contains_image(file, directory))

                        if directory.get('audioSampleRate'):
                            entry.update(rules.set_audio_sample_rate(file, directory))

                        if directory.get('audioFormat'):
                            entry.update(rules.set_audio_format(file, directory))

                        if directory.get('audioBitRate'):
                            entry.update(rules.set_audio_bit_depth(file, directory))

                        if directory.get('audioChannels'):
                            entry.update(rules.set_audio_channels(file, directory))

                        if directory.get('audioNormalize'):
                            entry.update(rules.set_audio_normalize(file, directory))

                        if directory.get('audioBitDepth'):
                            entry.update(rules.set_audio_bit_depth(file, directory))

                        if directory.get('videoOutputContainer'):
                            entry.update(rules.set_video_output_container(file, directory))

                        if directory.get('videoHeight'):
                            entry.update(rules.set_video_height(file, directory))

                        if directory.get('videoWidth'):
                            entry.update(rules.set_video_width(file, directory))

                        if directory.get('videoDuration'):
                            entry.update(rules.set_video_duration(file, directory))

                        if directory.get('videoFrameRate'):
                            entry.update(rules.set_video_frame_rate(file, directory))

                        if directory.get('videoPixFormat'):
                            entry.update(rules.set_video_pix_format(file, directory))

                        if directory.get('imageFormat'):
                            entry.update(rules.set_image_format(file, directory))

                        if directory.get('imageHeight'):
                            entry.update(rules.set_image_height(file, directory))

                        if directory.get('imageWidth'):
                            entry.update(rules.set_image_width(file, directory))

                        if directory.get('imageMode'):
                            entry.update(rules.set_image_mode(file, directory))

                        # when done checking conditions, add the entry to the operations dictionary if not null
                        if entry:
                            operations.append(entry)

        print(pprint.pformat(operations, indent=4, width=200))

        # self.db_manager.samplify()


def main():
    # Start benchmark timer.
    timer = time.time()

    # Initialize the application.
    samplify = Application()

    samplify.file_manager.scan_libraries()
    samplify.run_once()

    # T1 = datetime.timedelta()
    # T2 = datetime.timedelta()

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
