import re
import inspect
import itertools
import structlog
import datetime

logger = structlog.get_logger('Samplify.log')


def contains_expression(file, output):
    output_directories = {}     # indicates where this file goes

    exp = output.get('expression')
    if exp:
        pattern = re.compile(exp)
        search = pattern.finditer(file.file_name)   # Look for expressions in file name

        for match in search:
            output_directories['output_directory'] = output.get('path')
            output_directories['file_name'] = file.file_name
            output_directories['file_path'] = file.file_path

    return output_directories


def contains_extensions(file, output):
    entry = {}

    extension = output.get('extensions')

    if extension:

        extension.translate({ord(c): None for c in extension})

        for e in extension.split(','):

            if file.extension.lower() in extension.lower():
                entry['output_directory'] = output.get('path')
                entry['file_name'] = file.file_name
                entry['file_path'] = file.file_path

    return entry


def between_datetime(file, output):
    output_directories = {}

    datetime_start = output.get('datetimeStart')
    datetime_end = output.get('datetimeEnd')

    if datetime_start:

        datetime_start = datetime.datetime.strptime(datetime_start, "%Y-%m-%d")
        datetime_end = datetime.datetime.strptime(datetime_end, "%Y-%m-%d")

        # time delta ( > 0 ) between start and end
        delta_t = datetime_end - datetime_start

        # If > 0, we know the thresholds are not inversed incidentally.
        if delta_t:

            # time delta between file creation date and end threshold.
            delta_f = datetime_end - datetime.datetime.strptime(file.creation_date, "%Y-%m-%d")

            # Time delta must be less than the users specified threshold delta.
            # Also: must validate positive values since would be neg if passed user end threshold.
            if delta_f and delta_f <= delta_t:
                output_directories['output_directory'] = output.get('path')
                output_directories['file_name'] = file.file_name
                output_directories['file_path'] = file.file_path

    return output_directories


def contains_video(file, output):
    output_directories = {}

    condition = output.get('containsVideo')

    if condition and file.v_stream:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path

    return output_directories


def contains_audio(file, output):
    output_directories = {}

    condition = output.get('containsAudio')

    if condition and file.a_stream:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path

    return output_directories


def contains_image(file, output):
    output_directories = {}

    condition = output.get('containsImage')

    if condition and file.i_stream:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path

    return output_directories


# Set the output file at a specified sample rate
def set_audio_sample_rate(file, output):
    output_directories = {}

    sr = output.get('audioSampleRate')

    if sr:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['sample_rate'] = sr

    return output_directories


def set_audio_format(file, output):
    output_directories = {}

    af = output.get('audioFormat')

    if af:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['audio_format'] = af


def set_audio_bit_rate(file, output):
    output_directories = {}

    br = output.get('audioBitRate')

    if br:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['audio_bitrate'] = br


def set_audio_channels(file, output):
    output_directories = {}

    ch = output.get('audioChannels')

    if ch:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['audio_channels'] = ch


def set_audio_normalize(file, output):
    output_directories = {}

    norm = output.get('audioNormalize')

    if norm:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['audio_normalize'] = norm


def set_audio_bit_depth(file, output):
    output_directories = {}

    bd = output.get('audioBitDepth')

    if bd:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['audio_bit_depth'] = bd


def set_video_output_container(file, output):
    output_directories = {}

    c = output.get('videoOutputContainer')

    if c:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['video_output_container'] = c

def set_video_height(file, output):
    output_directories = {}

    h = output.get('videoHeight')

    if h:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['video_height'] = h

    return output_directories


def set_video_width(file, output):
    output_directories = {}

    w = output.get('videoWidth')

    if w:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['video_width'] = w

    return output_directories


def set_video_duration(file, output):
    output_directories = {}

    d = output.get('videoDuration')

    if d:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['video_duration'] = d

    return output_directories


def set_video_frame_rate(file, output):
    output_directories = {}

    fr = output.get('videoFrameRate')

    if fr:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['video_frame_rate'] = fr

    return output_directories


def set_video_pix_format(file, output):
    output_directories = {}

    pf = output.get('videoPixFormat')

    if pf:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['video_pix_format'] = pf

    return output_directories


def set_image_format(file, output):
    output_directories = {}

    fmt = output.get('imageFormat')

    if fmt:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['image_format'] = fmt

    return output_directories


def set_image_height(file, output):
    output_directories = {}

    h = output.get('imageHeight')

    if h:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['image_height'] = h

    return output_directories


def set_image_width(file, output):
    output_directories = {}

    w = output.get('imageWidth')

    if w:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['image_width'] = w


def set_image_mode(file, output):
    output_directories = {}

    m = output.get('imageMode')

    if m:
        output_directories['output_directory'] = output.get('path')
        output_directories['file_name'] = file.file_name
        output_directories['file_path'] = file.file_path
        output_directories['image_mode'] = m

    return output_directories
