from samplify.app import settings
import pydub as pd
import logging

logger = logging.getLogger('event_log')


def open_audio(input):
    logger.info(f"Event: File open {input}")
    audio = pd.AudioSegment.from_file(input)
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
    print('SET_MONO() ')
    print()
    return audio


def normalize_rms(audio):

    print('NORMALIZE_RMS()')

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


def get_rms_target(audio):

    print('NORMALIZE_RMS()')

    # FILE'S AVERAGE RMS dBFS (-)
    loudness_db = audio.dBFS

    # CHECK TO SEE IF CLIPPED
    if loudness_db > 0:
        loudness_db = 0
    print('AVERAGE VOLUME (RMS): ', loudness_db)

    # FIND THE DIFFERENCE FROM CURRENT DB TO TARGET
    change_in_dbfs = settings.target_dbfs - loudness_db
    print('TRYING TO APPLY: ', change_in_dbfs)


    # FIND AVAILABLE DYNAMIC RANGE
    add_dbfs = change_in_dbfs + audio.max_dBFS # target (pos) + peak (neg)
    print('MAX DYNAMIC RANGE AVAILABLE: ', add_dbfs)

    if -add_dbfs < 0:
        add_dbfs = change_in_dbfs - add_dbfs - 0.03

    return add_dbfs









    #
    #
    # # FIND AUDIO'S PEAK DBFS (-)
    # peak_amplitude = audio.max_dBFS
    # print('PEAK THRESHOLD: ', peak_amplitude)
    #
    # # FIND THE TARGET'S TOTAL CEILING VALUE
    # current_ceiling = peak_amplitude + change_in_dbfs
    # print('CLIP PEAK POST VOLUME: ', current_ceiling)
    #
    #
    # # NORMALIZATION CLIP PREVENTION
    # if current_ceiling > 0:  # IF CEILING VALUE IS LARGER THAN -.03
    #     change_in_dbfs = change_in_dbfs + -current_ceiling - 0.03
    #     print('CLIPPING DETECTED, LOWERING: ', -change_in_dbfs)
    #
    # print('CHANGE IN DBFS: ', change_in_dbfs)
    #
    # return change_in_dbfs


def detect_leading_silence(audio, silence_threshold=-50.0, chunk_size=10):
    '''
    audio is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with audio
    '''

    trim_ms = 0 # in ms

    assert chunk_size > 0 # to avoid infinite loop

    # start indexing the whole file
    while audio[0:trim_ms + chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size
        print(audio[0:trim_ms + chunk_size].dBFS)
        print(trim_ms)

    return trim_ms


def strip_silence(audio):
    import time

    print('strip_silence()')

    # get length of file
    duration = len(audio)
    print('AUDIO DURATION (MS): ', duration)

    # find the silence from start
    start_trim = detect_leading_silence(audio)
    print('CUT STARTING INDEX (MS): ', start_trim)
    time.sleep(4)

    # & end
    # end_trim = detect_leading_silence(audio.reverse())
    # print('CUT ENDING INDEX (MS): ', duration - end_trim)
    # time.sleep(4)

    # slice from start to (length - silence end)
    stripped_audio = audio[start_trim::]
    print('STRIPPED AUDIO DURATION: ', len(stripped_audio))
    print()
    time.sleep(4)

    return stripped_audio


def export(audio, in_name, out_path, extension):

    # out_name = out_path + '/' + in_name + extension

    audio.export(out_path)

    print('EXPORTED: ', out_path)
    print()