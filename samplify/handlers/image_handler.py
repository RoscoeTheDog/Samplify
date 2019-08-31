# import wand
# from wand.image import Image
# from wand.display import display
from PIL import Image
import logging
import time

logger = logging.getLogger('event_log')


# def metadata(input):
#
#     meta_dict = {
#         'v_stream': False,
#         'a_stream': False,
#         "i_stream": False,
#         "i_format": '',
#         "i_width": '',
#         "i_height": '',
#         "nb_frames": '',
#         "alpha_channel": False,
#     }
#
#     try:
#         with Image(filename=input) as original:
#
#             meta_dict["i_stream"] = True
#             meta_dict["i_format"] = original.format
#             meta_dict["i_width"] = original.width
#             meta_dict["i_height"] = original.height
#             meta_dict["nb_frames"] = len(original.sequence)
#             meta_dict["alpha_channel"] = original.alpha_channel
#
#             return meta_dict
#
#     except Exception as e:
#         logger.warning(f'Error: {e}')
#
#         return meta_dict
#
# def convert_image(self, input, output, format):
#
#     with Image(filename=input) as original:
#
#         with original.convert(format='png') as copy:
#             copy.save(filename=output.format(format))


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