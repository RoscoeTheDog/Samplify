import argparse
import os
import logging
import time

from samplify.handlers import database_handler
from samplify.app import input, output, settings, gpu

logger = logging.getLogger('event_log')


def logging_config():

    # determines what will be logged
    logger.setLevel(logging.DEBUG)

    # formatting for the different handlers
    format_log = logging.Formatter('%(pathname)s:%(asctime)s:%(levelname)s: %(message)s')
    format_stream = logging.Formatter('%(message)s')

    # file handlers read/write log files
    file_handler = logging.FileHandler('Samplify.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(format_log)

    # stream handlers show the messages as they are logged in real time
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(format_stream)

    # attach handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


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


def main():

    # start logging
    logging_config()

    # configure hardware
    gpu.hardware()

    # add temporary template
    database_handler.insert_template()

    # create outputs
    output.create_directories()

    # initialize file monitor cache
    # database.start_input_cache()
    # database.start_output_cache()

    # start benchmark (input)
    timer = time.time()

    # scan all input folders
    input.scan_files()
    print('scan complete!')
    time.sleep(2)

    # stdout, stderr = av_handler.ffprobe('C:\\OpenCV 4.1.0\\opencv\\sources\\doc\\acircles_pattern.png')
    # print(stdout)
    # av_handler.parse_ffprobe(stdout, stderr)

    # end benchmark (input)
    bench_input = time.time() - timer

    # start benchmark (output)
    timer = time.time()

    # SAMPLIFY!
    database_handler.start_program()

    # collect all files/folders from output
    # db_handler.get_root_output(App_Settings.output_path)

    # end benchmark (output)
    bench_output = time.time() - timer

    print('input scan: ', bench_input)
    print('output scan: ', bench_output)

    # start monitoring thread for input events
    # input_monitor = bin.monitor_events.InputMonitoring()
    # input_monitor.start_observer()

    # start monitoring thread for output events
    # output_monitor = bin.monitor_events.OutputMonitoring()
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