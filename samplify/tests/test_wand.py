from wand.image import Image

input = 'C:\\Users\\Aspen\\Desktop\\New folder (2)\\835.psd'

with Image(filename=input) as original:

    with original.convert(format='png') as copy:
        copy.save(filename='C:\\Users\\Aspen\\Desktop\\pictest.png'.format('png'))