import structlog
from structlog.stdlib import *
from structlog.processors import *
from pythonjsonlogger import jsonlogger

import sys
import logging

# declare our logger using structlog (basic logging does not allow args other than message)
logger = structlog.get_logger('samplify.log')


def configure_logging():

    # declare a custom formatter for our stream
    stream_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(level_styles=
            {
                'info:': '\033[31m',  # colorama ANSI sequences    # print(structlog.dev.ConsoleRenderer.get_default_level_styles()) for example
            }
        ),
    )

    # declare a custom formatter for our log file
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(sort_keys=False),
    )

    # declare our file handler
    file_handler = logging.FileHandler('samplify.log')
    # set our custom formatter for the log file
    file_handler.setFormatter(file_formatter)   # In theory, jsonlogger.JsonFormatter() could be used with custom override methods that allow us to re-order keys

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
        processors=[
            # filter_by_level,
            # add_log_level,
            # PositionalArgumentsFormatter(),
            TimeStamper(fmt='iso'),
            ExceptionPrettyPrinter(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

configure_logging()

# log something to file!
logger.info('this is an event message!',
            dict_entry={'somekey': 'value', 'other key': 'value2'},
            string_entry='string',
            int_entry=10,
            bool_entry=True)














# log = structlog.wrap_logger(
#     structlog.get_logger('samplify.log'),
#     processors=[
#         filter_by_level,
#         add_log_level,
#         PositionalArgumentsFormatter(),
#
#         TimeStamper(fmt='iso'),
#         StackInfoRenderer(),
#         ExceptionPrettyPrinter(),
#         # JSONRenderer(indent=1),
#         KeyValueRenderer(key_order=['event', 'level', 'timestamp']),
#     ]
# )

# log = structlog.wrap_logger(
#     logging.getLogger('samplify.log'),
#     processors=[
#         filter_by_level,
#         add_log_level,
#         PositionalArgumentsFormatter(),
#
#         TimeStamper(fmt='iso'),
#         StackInfoRenderer(),
#         ExceptionPrettyPrinter(),
#         # JSONRenderer(indent=1),
#         KeyValueRenderer(key_order=['event', 'level', 'timestamp']),
#     ]
# )

# log.info('testing info message',
#          some_dict={'somekey': 'value', 'other key': 'value2'},
#          other_dict={'key': 'value'},
#          test1='string',
#          test2=10,
#          test3=True)




# log = structlog.getLogger()

# structlog.configure(
    # processors=[
    # filter_by_level,
    # add_log_level,
    # PositionalArgumentsFormatter(),
    # TimeStamper(fmt='iso'),
    # StackInfoRenderer(),
    # ExceptionPrettyPrinter(),
    # JSONRenderer(indent=1, sort_keys=True),
    # # KeyValueRenderer(),
    # ]
# )













# structlog.configure(
#     processors=[
#         structlog.stdlib.filter_by_level,
#         structlog.stdlib.add_logger_name,
#         structlog.stdlib.add_log_level,
#         structlog.stdlib.PositionalArgumentsFormatter(),
#         structlog.processors.StackInfoRenderer(),
#         structlog.processors.format_exc_info,
#         structlog.processors.UnicodeDecoder(),
#         structlog.stdlib.render_to_log_kwargs,
#     ],
#     context_class=dict,
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
# )

# log = structlog.getLogger(sys.stdout)

# log.msg("struct_log test", location=__file__, type=str)
# log.debug("debug test")
# log.info("info test")
# log.warning("warning test")
# log.error("error test")
# log.critical("critical test")