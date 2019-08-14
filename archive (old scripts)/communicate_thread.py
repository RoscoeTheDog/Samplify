import subprocess
import ffmpy_thread
import logging
import threading
import sys

logger = logging.getLogger('event_log')

def start_thread():

    thread = threading.Thread(target=log_ffmpeg())
    thread.daemon = True
    thread.start()


def log_ffmpeg():
    p = subprocess.Popen(['python', 'ffmpy_test.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    """
        Commenting out the few lines below makes no difference to what is printed, it is outputed either way.
    """

    output = p.stdout.readline().strip()

    if output:
        logger.info(output)

def also_tried():
    with subprocess.Popen(["python", "ffmpy_test.py"], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            logger.info(line)

start_thread()

