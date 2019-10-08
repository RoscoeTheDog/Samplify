import subprocess
import re
import platform
from app import settings
import structlog


# call our logger locally
logger = structlog.get_logger('samplify.log')


def hardware():

    # TODO: test code on multiple platforms

    v_name = 'not_known'

    if platform.system() == 'Windows':

        process = subprocess.Popen(['wmic', 'path', 'win32_VideoController', 'get', 'name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        stdout, stderr = process.communicate()

        _vendor = re.compile(r"(NVIDIA)|(AMD)|(INTEL)", re.IGNORECASE)
        find_vendor = _vendor.finditer(stdout)

        for m in find_vendor:
            v_name = stdout[m.start():m.end()]

    elif platform.system() == 'Linux':
        pass

    elif platform.system() == 'Java':
        pass

    logger.info(f'user_message', msg=f'GPU type identified as {v_name}')
    settings.gpu_vendor = v_name

    if settings.gpu_vendor.lower() == 'nvidia' or 'amd':
        logger.info(f'user_message', msg=f'Hardware acceleration enabled')

    elif settings.gpu_vendor.lower() == 'intel':
        logger.warning(f'user_message', msg=f'Hardware acceleration is not supported on this gpu')
