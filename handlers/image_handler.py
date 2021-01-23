from PIL import Image
import structlog

# Note: The Image library will attempt to send some debug info the log occasionally. Set the logger config accordingly.

# # call our logger locally
logger = structlog.get_logger('samplify.log')


def decode_image(input):

    meta_dict = {
        'v_stream': False,
        'a_stream': False,
        'i_stream': False,
        'i_fmt': '',
        'i_width': '',
        'i_height': '',
        'i_frames': '',
        'i_alpha': False,

        'succeeded': False,
    }

    try:
        with Image.open(input) as original:

            meta_dict['i_stream'] = True
            meta_dict['i_fmt'] = str(original.format)

            width, height = original.size
            meta_dict['i_width'] = str(width)
            meta_dict['i_height'] = str(height)
            meta_dict['i_mode'] = str(original.mode)

            try:
                if original.getchannel("A"):
                    meta_dict['i_alpha'] = True
            except Exception as e:
                # If failed, we know it has no alpha channel.
                meta_dict['i_alpha'] = False

            # Determine the number of frames for the file.
            nb_frames = 0
            try:
                while True:
                    original.seek(nb_frames)
                    nb_frames += 1
            except EOFError:
                pass

            meta_dict['i_frames'] = str(nb_frames)

            logger.info('admin_message', msg='Decode succeeded')

            return meta_dict

    except Exception as e:
        logger.error(f'admin_message', msg='Decode failed with Pill', exc_info=e)

        return meta_dict


def convert_image(input, output, format):

    image = Image.open(input)
    copy = image.copy()

    copy.save(output, format)

    #
    # with Image.open(input) as original:
    #     original.copy(output, format)