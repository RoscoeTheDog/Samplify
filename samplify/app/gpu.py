import subprocess
import re
import platform
from samplify.app import settings
import structlog


# call our logger locally
logger = structlog.get_logger('samplify.log')


def hardware():

    # TODO: test code on multiple platforms

    v_name = str

    if platform.system() == 'Windows':

        process = subprocess.Popen(['wmic', 'path', 'win32_VideoController', 'get', 'name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        stdout, stderr = process.communicate()

        _vendor = re.compile(r"(NVIDIA)|(AMD)", re.IGNORECASE)
        find_vendor = _vendor.finditer(stdout)

        for m in find_vendor:
            v_name = stdout[m.start():m.end()]

    elif platform.system() == 'Linux':
        pass

    elif platform.system() == 'Java':
        pass

    logger.info(f'Event: GPU identified as type {v_name}')
    settings.gpu_vendor = v_name

    if v_name == 'NVIDIA' or 'AMD':
        logger.info(f'Event: Hardware acceleration enabled')

    else:
        logger.info(f'Event: Hardware acceleration disabled')
