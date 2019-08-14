import app_settings
import pydub as pd
import os
import logging
import os

logger = logging.getLogger('event_log')


def open_audio(output):
    logger.info(f"Event: File open {output}")
    audio = pd.AudioSegment.from_file(output)
    return audio


def get_bit_depth(file):

    bit_depth = file.sample_width  # 1-4. 1=8 2=16 3=24 4=32

    if bit_depth is 1:
        bit_depth = 8

    elif bit_depth is 2:
        bit_depth = 16

    elif bit_depth is 3:
        bit_depth = 24

    elif bit_depth is 4:
        bit_depth = 32

    logger.info(f"Event: File bit depth {bit_depth}")

    return bit_depth


def get_sample_rate(file):
    logger.info(f"Event: File sample rate {file.frame_rate}")
    sample_rate = file.frame_rate
    return sample_rate


def set_bit_depth(audio):

    print('INPUT BIT-DEPTH: ', audio.sample_width)

    # CHECK TO SEE IF BIT-DEPTH IS GREATER THAN SPECIFIED BIT-DEPTH
    if audio.sample_width > settings.bit_depth:
        print('CHANGING TO 24 OR HIGHER...')
        audio = audio.set_sample_width(settings.bit_depth)

    # IF 8 BIT CHANGE TO MINIMUM 16
    elif audio.sample_width == 1:
        audio = audio.set_sample_width(2)

    else:
        print('BIT-DEPTH LOWER THAN TARGET, SKIPPING...')

    print('OUTPUT BIT-DEPTH: ', audio.sample_width)
    print()
    return audio


def set_mono(audio):

    audio = audio.set_channels(1)
    print('CONVERTING TO MONO ')
    print()
    return audio


def normalize_rms(audio):

    # FILE'S AVERAGE RMS dBFS (-)
    loudness_db = audio.dBFS

    # CHECK TO SEE IF CLIPPED
    if loudness_db > 0:
        loudness_db = 0
    print('AVERAGE VOLUME (RMS): ', loudness_db)

    # FIND THE DIFFERENCE FROM CURRENT DB TO TARGET
    change_in_dbfs = settings.target_dbfs - loudness_db
    print('TRYING TO APPLY: ', change_in_dbfs)

    # FIND AUDIO'S PEAK DBFS (-)
    peak_amplitude = audio.max_dBFS
    print('CLIP PEAK VOLUME: ', peak_amplitude)

    # FIND THE TARGET'S TOTAL CEILING VALUE
    current_ceiling = peak_amplitude + change_in_dbfs
    print('CLIP PEAK POST VOLUME: ', current_ceiling)

    # NORMALIZATION CLIP PREVENTION
    if current_ceiling > 0.00:  # IF CEILING VALUE IS LARGER THAN 0
        audio = audio.apply_gain(change_in_dbfs + -current_ceiling - 0.03)  # REDUCE
        print('CLIPPING DETECTED, LOWERING: ', -current_ceiling)

    else:  # OTHERWISE, NORMALIZE TO TARGET RMS
        audio = audio.apply_gain(change_in_dbfs)

    print('ACHIEVED RMS VALUE (dBFS) ', audio.dBFS)
    print()

    return audio


def export(audio, output):

    # FILTER OUT PATH AND EXTENSION TYPE 'justfilename'
    _basename = os.path.basename(output)

    # TAKE OUT THE EXTENSION TYPE OF NAME
    if _basename.endswith(settings.ext_type):
        _basename = _basename[:-len(settings.ext_type)]

    for words in settings.keywords:
        os.chdir(settings.output_path)
        # CREATE SUBDIRECTORIES BASED ON KEYWORDS
        if not os.path.exists(words):
            os.mkdir(words)

        # GATHER SUBDIRECTORIES
        sub_directories = next(os.walk(settings.output_path))[1]
        if words.casefold() in output.casefold():

            # NEST IN SUBDIRECTORIES
            for directories in sub_directories:
                if directories.casefold() in output.casefold():
                    converted_output = directories + '\\' + _basename + '.' + settings.conv_type
                    audio.export(converted_output, format=settings.conv_type)

                    print('EXPORTED: ', output)
                    print()

                    return output