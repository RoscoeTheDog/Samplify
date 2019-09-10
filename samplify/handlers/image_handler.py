import logging
from logging import Logger
from logging import manager
from PIL import Image
import time
import structlog


logging.Logger.manager.loggerDict[__name__] = structlog.get_logger('samplify.log')

# # call our logger locally
logger = structlog.get_logger('samplify.log')


def metadata(input):

    meta_dict = {
        'v_stream': False,
        'a_stream': False,
        "i_stream": False,
        "i_format": '',
        "i_width": '',
        "i_height": '',
        "nb_frames": '',
        "alpha_channel": False,
    }

    try:
        with Image.open(input) as original:

            meta_dict["i_stream"] = True
            meta_dict["i_format"] = original.format

            width, height = original.size
            meta_dict["i_width"] = width
            meta_dict["i_height"] = height
            meta_dict['i_mode'] = original.mode

            return meta_dict

    except Exception as e:
        logger.warning(f'Error: {e}')

        return meta_dict


def convert_image(input, output, format):

    image = Image.open(input)
    copy = image.copy()

    copy.save(output, format)

    #
    # with Image.open(input) as original:
    #     original.copy(output, format)