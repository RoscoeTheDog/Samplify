import subprocess
import re
import platform
import app_settings
import logging

logger = logging.getLogger('event_log')


def vendor():

    # TODO: test this code on multiple platforms

    logger.info('Event: Start GPU identification')

    if platform.system() == 'Windows':

        gpu_vendor = ''

        process = subprocess.Popen(['wmic', 'path', 'win32_VideoController', 'get', 'name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        stdout, stderr = process.communicate()

        _vendor = re.compile(r"(NVIDIA)|(AMD)", re.IGNORECASE)
        find_vendor = _vendor.finditer(stdout)

        for m in find_vendor:
            gpu_vendor = stdout[m.start():m.end()]

        return gpu_vendor

    elif platform.system() == 'Linux':
        pass

    elif platform.system() == 'Java':
        pass


def set_vendor(vendor_str):
    logger.info('Event: GPU config set to: ' + vendor_str)

    app_settings.gpu_vendor = vendor_str