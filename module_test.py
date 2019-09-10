import logging
import structlog
import struct_log


logger = structlog.get_logger('samplify.log')

logger.info('testing across scripts', something='else')