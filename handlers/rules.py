import re
import inspect
import itertools
import structlog
import datetime

logger = structlog.get_logger('Samplify.log')


def has_expression(file, output):
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


def has_extensions(file, output):
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


def rule_has_video(file, directory):
    has_video = directory.get('hasVideo')

    if has_video == 'True':
        if file.v_stream:
            return True

    return False


def rule_has_audio(file, directory):
    has_audio = directory.get('hasAudio')

    if has_audio == 'True':
        if file.a_stream:
            return True

    return False


def rule_has_image(file, directory):
    has_image = directory.get('hasImage')

    if has_image == 'True':
        if file.i_stream:
            return True

    return False






































