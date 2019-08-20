import wand
from wand.image import Image
from wand.display import display
import logging

logger = logging.getLogger('event_log')


class ImageHandler:

    def __init__(self):
        # super(Image, display).__init__()

        self.img_format = 'png'
        self.scale = 'x100'  # resize scale in %

        """
            show file preview when gui is built here
        """

    def meta_info(self, input):

        meta_dict = {
            "i_stream": False,
            "i_format": '',
            "i_width": '',
            "i_height": '',
            "nb_frames": '',
            "alpha_channel": False,
        }

        try:
            with Image(filename=input) as original:

                meta_dict["i_stream"] = True
                meta_dict["i_format"] = original.format
                meta_dict["i_width"] = original.width
                meta_dict["i_height"] = original.height
                meta_dict["nb_frames"] = len(original.sequence)
                meta_dict["alpha_channel"] = original.alpha_channel

                return meta_dict

        except Exception as e:
            logger.warning(f'Warning: {input} not an image file')

            return meta_dict

    def convert_image(self, input, output, format):

        with Image(filename=input) as original:

            with original.convert(format='png') as copy:
                copy.save(filename=output.format(format))




    # def convert_image(self, input, output):
    #
    #     output = 'filename'
    #
    #     with Image(filename=input) as original:
    #
    #         with original.convert(format=self.img_format) as converted:
    #
    #             converted.sample(1920, 1024)  ## sample is faster but does not allow filter options
    #             # converted.resize(1920, 1024)
    #             # converted.liquid_rescale(1920, 1024)  # liquid rescale crops/resizes based on algorithm.
    #
    #             converted.save(filename=output + '.' + self.img_format.format(self.img_format))
    #
    #             print('format =', converted.format)
    #             print('width =', converted.width)
    #             print('height =', converted.height)
    #             print('alpha = ', converted.alpha_channel)



# def open_img(input, output):
#
#     output = 'filename'
#     img_format = 'png'
#
#     scale = 'x1000'  # resize in %
#
#
#     with Image(filename=input) as original:
#         print('format =', original.format)
#         print('frames =', len(original.sequence))
#         print('width =', original.width)
#         print('height =', original.height)
#         print('alpha = ', original.alpha_channel)
#         print()
#
#         with original.convert(img_format) as converted:
#             # converted.sample(50, 50)  ## sample is faster but does not allow filter options
#             # converted.resize(50, 50)
#
#
#             # converted.liquid_rescale(1920, 1024)
#             converted.resize(1920, 1024)
#             # converted.transform(resize=scale)
#
#             converted.save(filename=output + '.' + img_format.format(img_format))
#
#             print('format =', converted.format)
#             print('width =', converted.width)
#             print('height =', converted.height)
#             print('alpha = ', converted.alpha_channel)
#
#
# open_img('waterfalls.jpg', '')


# with Image(filename='mona-lisa.png') as img:
#     print(img.size)
#     for r in 1, 2, 3:
#
#         with img.clone() as i:
#             i.resize(int(i.width * r * 0.25), int(i.height * r * 0.25))  # resize takes (width, height) tuple values
#             i.rotate(90 * r)
#             i.save(filename='mona-lisa-{0}.png'.format(r))
#             display(i)