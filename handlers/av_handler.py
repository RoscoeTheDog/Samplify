import subprocess
import re
import av
import av.filter
import os
import pydub as pd
from app import settings
import time
import json
import structlog


# call our logger locally
logger = structlog.get_logger('samplify.log')
number = 0


def stream_info(path: str) -> dict:
    """
    :param path: :str: "path to file"
    :return: :dict: "dict of metadata from file"
    """

    # declare different types of streams (defaults to false)
    file_meta ={
            'v_stream': False,
            'a_stream': False,
            'i_stream': False,
        }

    try:
        # TODO: investigate why open() can take awhile to return in some cases
        container = av.open(path)



        """
        In this scope:
        
        *Values that == 0 mean not known or is a False Positive.
        
        *Decode audio channels first for efficiency (it has the highest probability to fail).
        """

        for frame in container.decode(audio=0):
            channels = frame.layout.channels  # returns (tupple[list]) of channels
            counter = 0
            for ch in channels:
                counter += 1
            if not counter == 0:
                file_meta['channels'] = counter
                file_meta['channel_layout'] = frame.layout.name
            break  # Do not decode all frames for audio channel info

        # decode file's bit-rate
        if not int(container.bit_rate / 1000) == 0:
            file_meta['a_bit_rate'] = container.bit_rate / 1000

        # decode file's streams
        for s in container.streams:

            """
                Certain properties from Images (such as stream type) can be mistaken as Video.
                Check the decoder's format name to determine if == image or video.
            """

            # IMAGE STREAMS
            file_meta['i_stream'] = is_image_stream(s.codec_context.format.name)

            if file_meta['i_stream'] is True:  # skip current working stream if == Image type
                continue

            # VIDEO STREAMS
            elif s.type == 'video':

                file_meta['v_stream'] = True

                """
                    - PyAV library does not always return v_duration reliably, but is the fastest method.
                    
                    - FFprobe is an alternative whenever v_duration is not returned.
                """

                file_meta['v_duration'] = s.metadata.get('DURATION', '')

                if file_meta['v_duration'] == '':
                    stdout, stderr = ffprobe(path)
                    file_meta = parse_ffprobe(stdout, stderr)
                    file_meta = validate_keys(file_meta)
                    break

                # decode video container's resolution
                if not s.width == 0:
                    file_meta['v_width'] = s.width
                if not s.height == 0:
                    file_meta['v_height'] = s.height

                # decode actual encoded resolution of video
                if not s.coded_width == 0:
                    file_meta['v_buffer_width'] = s.coded_width
                if not s.coded_height == 0:
                    file_meta['v_buffer_height'] = s.coded_height

                file_meta['nb_frames'] = s.frames

                if s.frames == 0:
                    file_meta['nb_frames'] = s.metadata.get('NUMBER_OF_FRAMES', '')

                # decode frame-rate (returned in fraction format)
                if not int(s.rate) == 0:
                    file_meta['v_frame_rate'] = float(s.rate)

                # decode video format
                if s.pix_fmt:
                    file_meta['v_pix_fmt'] = s.pix_fmt

            # AUDIO STREAMS
            elif s.type == 'audio':
                file_meta['a_stream'] = True

                # decode sample format
                if s.format.name:
                    file_meta['a_sample_fmt'] = s.format.name

                # decode sample rate
                if not int(s.sample_rate) == 0:
                    file_meta['a_sample_rate'] = s.sample_rate

                # decode bit depth (note: 24 bit will show as 32 -- check sample_fmt for pcm_s24le instead)
                if not int(s.format.bits) == 0:
                    file_meta['a_bit_depth'] = s.format.bits

        # check dict keys for missing entries or 0s -- minimize decoding false positives into database
        file_meta = validate_keys(file_meta)

    except Exception as e:
        logger.error(f'admin_message', msg='Decode failed using PyAV', exception=e)

        if file_meta['i_stream'] is False:
            stdout, stderr = ffprobe(path)
            file_meta = parse_ffprobe(stdout, stderr)

    return file_meta


def is_image_stream(stream_fmt: str):
    """
    :param stream_fmt: accepts string value of av_decode stream format
    :return: boolean value of image type
    """

    _stream = False

    if 'pipe' in stream_fmt:  # 'pipe' are typically image-type decoders
        _stream = True

    if stream_fmt in ['image2', 'tty', 'ico', 'gif']:  # list of some other image decoders
        _stream = True

    return _stream


def convert_pyav(input, output, file_name, extension, a_codec, v_codec, sample_rate, sample_fmt, channels):

    try:

        print('trying PyAV Method...')

        print('variables: ', input, output, file_name, extension, a_codec, v_codec, sample_rate, sample_fmt, channels)

        # I/O VARIABLES
        inp = av.open(input, 'r')
        out = av.open(output, 'w')
        # out_video_stream = out.add_stream(v_codec)
        out_audio_stream = out.add_stream(a_codec, rate=int(sample_rate))

        # RESAMPLER OBJECT (WARNING: ONLY SET RATE ON AUDIO-STREAM -- FORMATTING ISSUES)
        resampler = av.AudioResampler(
            format=sample_fmt,
            layout=channels,
        )


        """
            add_abuffer missing from filter.Graph(). Wait for stable release to implement. Use FFmpeg for now.
        """

        # graph = av.filter.Graph()
        #
        # fchain = []
        # iastrm = next(s for s in inp.streams if s.type == 'audio')
        #
        # frame_rate = str
        # sample_fmt = str
        # bit_depth = str
        # for s in inp.streams:
        #     if s.type == 'audio':
        #         sample_fmt = s.format.name
        #         frame_rate = s.sample_rate
        #
        #
        # channels = int
        # for frame in inp.decode(audio=0):
        #     channels = frame.layout.channels
        #
        # print(frame_rate, sample_fmt, channels)
        #
        # fchain.append(graph.add_abuffer(template=iastrm))
        # fchain.append(graph.add('silenceremove', 'stop_periods=-1:stop_duration=1:stop_threshold=-90dB'))
        # fchain[-2].link_to(fchain[-1])
        #
        # fchain.append(graph.add("buffersink"))  # graph must end with buffersink...?
        # fchain[-2].link_to(fchain[-1])
        #
        # for value, filter in enumerate(av.filter.filters_available):
        #     print(value, filter)



        # DECODING/ENCODING
        for frame in inp.decode(audio=0):
            frame.pts = None  # pts is presentation time-stamp. Not relevant here.

            frame = resampler.resample(frame)  # get current working frame and re-sample it for encode

            for packet in out_audio_stream.encode(frame):  # encode the re-sampled frame
                out.mux(packet)



            """
                wait for add_abuffer in next update for this...
            """

            # fchain[0].push(frame)
            # ofr = fchain[-1].pull()
            # ofr.pts = None

            # for p in out_audio_stream.encode(ofr):  # 'p' stands for packet
            #     out.mux(p)

        for packet in out_audio_stream.encode(None): # 'p' stands for packet
            out.mux(packet)

        out.close()

    except Exception as e:
        settings.exception_counter += 1
        logger.error('admin_message', msg='Could not convert the file', exc_info=e)


def convert_ffmpeg(ff_args):

    process = subprocess.Popen(ff_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()

    return stdout, stderr


def convert_pydub(in_path, in_name, out_path, extension):

    audio = pd_open(in_path)
    # audio = pd.set_mono(audio)
    audio = pd_strip_silence(audio)
    # audio = pd.normalize_rms(audio)
    pd_export(audio, in_name, out_path, extension)
    time.sleep(4)


def configure_args(input, output, gpu_vendor, v_stream, a_stream, sample_rate, bit_depth, channels, normalize, strip_silence, silence_threshold, reduce):
    ff_args = ['ffmpeg', '-y', '-i', input]

    # TODO: detect for gpu type and turn off nvidia codec when unavailable
    #       add other -v args for more user end support

    # https://stackoverflow.com/questions/55687189/how-to-use-gpu-to-accelerate-the-processing-speed-of-ffmpeg-filter/55747785#55747785
    if gpu_vendor == 'NVIDIA':
        ff_args.append('-c:v')
        ff_args.append('hevc_nvenc')

    # https://askubuntu.com/questions/1107782/how-to-use-gpu-acceleration-in-ffmpeg-with-amd-radeon
    if gpu_vendor == 'AMD':
        ff_args.append('-c:v')
        ff_args.append('-hevc_amf')

    # if v_stream is True:
    #     pass

    if a_stream is True:

        if normalize is True:
            audio = pd.open_audio(input)
            rms_target = pd.get_rms_target(audio)

            ff_args.append('-af')
            ff_args.append(f'volume={rms_target}dB')

        if strip_silence is True:
            ff_args.append('-af')
            ff_args.append(f'silenceremove=1:0:{silence_threshold}dB')
            ff_args.append('-af')
            ff_args.append(f'silenceremove=stop_periods=-1:stop_duration=0:stop_threshold={silence_threshold}dB')


        # TODO: automatic file reduction/optimizations

        # if reduce is True:
        #     if int(sample_rate) > 44100:
        #         ff_args.append('44100')

            # if int(bit_depth) > 24:
            #     ff_args.append('-acodec')
            #     ff_args.append('pcm_s24le')

        ff_args.append('-ar')
        ff_args.append(sample_rate)
        ff_args.append('-ac')
        ff_args.append(channels)


    # always append output
    ff_args.append(os.path.abspath(output))

    return ff_args


def parse_ffmpeg(stdout, stderr):
    v_format = None
    v_codec = None
    a_format = None
    a_codec = None
    export = True


    """
        Parse Video Info
    """

    output_info = re.compile(r'(Output\s(.{,99999})\n)(((.{,99999})\n){,256})')
    find_output = output_info.finditer(stderr)

    for match in find_output:
        output_info = stderr[match.start():match.end()]

        video_stream = re.compile(r'(Video:\s.{,9999})' +
                                  r'((\n.{,9999}){,99}\sAudio:\s)')
        find_video = video_stream.finditer(output_info)

        for match in find_video:
            video_stream = output_info[match.start():match.end()]
            # print('video stream: ', video_stream)
            # print('')

            video_format = re.compile(r'Video:\s(([a-z|0-9]|[_]){,99}\s[(])')
            find_video_format = video_format.finditer(video_stream)

            for match in find_video_format:
                v_format = video_stream[match.start():match.end()][7:-2]
                # print('video format:', v_format)


                encoder_info = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})\s[^\n]{,9999}', re.IGNORECASE)
                find_encoder_info = encoder_info.finditer(video_stream)

                for match in find_encoder_info:
                    encoder = video_stream[match.start():match.end()]
                    # print('encoder string:', encoder)

                    video_codec = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})', re.IGNORECASE)
                    find_video_codec = video_codec.finditer(encoder)

                    for match in find_video_codec:
                        v_codec = encoder[match.end()+1:]
                        # print('video codec:', v_codec)

        # print('')

        """
            Parse Audio Info
        """

        audio_stream = re.compile(r'(Audio:\s.{,9999})' +
                                  r'(\n.{,9999}){,99}')
        find_audio = audio_stream.finditer(output_info)

        for match in find_audio:
            audio_stream = output_info[match.start():match.end()]
            # print('audio stream:', audio_stream)
            # print('')

            audio_format = re.compile(r'Audio:\s(([a-z|0-9]|[_]){,99}\s[(])')
            find_audio_format = audio_format.finditer(audio_stream)

            for match in find_audio_format:
                a_format = audio_stream[match.start():match.end()][7:-2]
                # print('audio format:', a_format)

            encoder_info = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})\s[^\n|;]{,9999}', re.IGNORECASE)
            find_encoder_info = encoder_info.finditer(audio_stream)

            for match in find_encoder_info:
                encoder = audio_stream[match.start():match.end()]
                # print('encoder string:', encoder)


                audio_codec = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})', re.IGNORECASE)
                find_audio_codec = audio_codec.finditer(encoder)

                # audio_codec = re.compile((f'{a_format}' + r'\s[(]([a-z|0-9]{,99})[)]'))
                # find_audio_codec = audio_codec.finditer(audio_stream)

                for match in find_audio_codec:
                    a_codec = encoder[match.end()+1:]
                    # print('audio codec:', a_codec)


    """
        Parse Other
    """

    failed = re.compile(r'(failed!)')
    check_status = failed.finditer(stderr)

    for m in check_status:
        export = False


    return export, v_format, v_codec, a_format, a_codec


def ffprobe(input):

    logger.info('admin_message', msg='Configuring FFprobe arguments', file=input)

    ff_args = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=format_name,duration,bit_rate', '-sexagesimal', '-of', 'default=noprint_wrappers=1', '-print_format', 'json', input, '-show_streams']

    process = subprocess.Popen(ff_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=9999999)
    stdout, stderr = process.communicate()

    return stdout, stderr


def parse_ffprobe(stdout, stderr):

    """
        file_meta['i_stream'] is essentially treated as "image or other undesired format"
    """

    # print(stderr)
    # print(stdout)

    # try:
    file_meta = {
        'v_stream': False,

        'a_stream': False,


        'i_stream': False,

        'a_bit_depth': '',  # have this declared until we correctly parse bits_per_sample
    }

    try:

        data = json.loads(stdout)

        for sub_dict, dict_list in data.items():

            if 'format' in sub_dict:  # custom search variables are in 'format' dict
                for key, value in dict_list.items():  # 'format' is {}, NOT []

                    if 'pipe' in value:  # 'pipe' types are image decoders
                        file_meta['i_stream'] = True
                        break

                    if value in ['image2', 'tty', 'ico', 'gif']:  # list of some other image decoders
                        file_meta['i_stream'] = True
                        break

                    if key == 'duration':
                        file_meta['v_duration'] = value

                    if key == 'bit_rate':
                        file_meta['a_bit_rate'] = value

            else:
                # switches that avoid assigning wrong values to dict during multiple iterations
                is_video = False
                is_audio = False

                for count, dictionary in enumerate(dict_list):
                    # print('Stream:', count, dictionary)

                    for key, value in dictionary.items():
                        # print(key, value)

                        if key == 'codec_type' and value == 'video':
                            file_meta['v_stream'] = True
                            is_video = True
                            is_audio = False

                        if key == 'codec_type' and value == 'audio':
                            file_meta['a_stream'] = True
                            is_video = False
                            is_audio = True

                        if is_video is True:

                            if key == 'width':
                                if not int(value) == 0:
                                    file_meta['v_width'] = value

                            if key == 'height':
                                if not int(value) == 0:
                                    file_meta['v_height'] = value

                            if key == 'avg_frame_rate':
                                # convert string then divide
                                num, den = value.split('/')

                                if int(den):
                                    value = float(int(num)/int(den))

                                    if not int(value) == 0:
                                        file_meta['v_frame_rate'] = value

                            if key == 'pix_fmt':
                                file_meta['v_pix_fmt'] = value

                            # two methods of finding frame count:
                            if key == 'nb_frames':
                                if not int(value) == 0:
                                    file_meta['nb_frames'] = value

                            if key == 'tags':
                                for k, v in value.items():
                                    if k == 'NUMBER_OF_FRAMES':
                                        file_meta['nb_frames'] = v

                        if is_audio is True:

                            if key == 'sample_rate':
                                if not int(value) == 0:
                                    file_meta['a_sample_rate'] = value

                            if key == 'sample_fmt':
                                file_meta['a_sample_fmt'] = value

                            if key == 'bit_rate':
                                if not int(value) == 0:
                                    file_meta['a_bit_rate'] = value

                            if key == 'channels':
                                if not int(value) == 0:
                                    file_meta['channels'] = value

                            if key == 'channel_layout':
                                file_meta['channel_layout'] = value

    except Exception as e:
        logger.warning(f'Warning: {e}')

    # turn off v_stream if file is classified as image.
    if file_meta['i_stream'] is True:
        file_meta['v_stream'] = False

    # validate video/audio dictionary values to minimize false positives
    else:
        file_meta = validate_keys(file_meta)

    return file_meta


def validate_keys(file_meta: dict):

    """
        Note: we can reduce decoding false-positives by validating our dictionary entries
    """

    if settings.validate_audio is True:
        check_keys = ['a_sample_rate', 'a_sample_fmt', 'channels', 'channel_layout']

        for key in check_keys:
            if not key in file_meta:
                file_meta['a_stream'] = False

    if settings.validate_video is True:
        check_keys = ['v_width', 'v_height', 'v_frame_rate', 'v_pix_fmt', 'v_duration']

        for key in check_keys:
            if not key in file_meta:
                file_meta['v_stream'] = False

    return file_meta


def _parse_ffprobe(stdout, stderr):  # old method

    _meta = {
        'succeeded': False,

        'v_stream': False,
        'v_width': '',
        'v_height': '',
        'v_frame_rate': '',
        'v_pix_fmt': '',
        'v_is_rgb': '',

        'a_stream': False,
        'a_sample_fmt': '',
        'a_sample_rate': '',
        'a_bit_rate': '',
        'a_bit_depth': '',
        'channels': '',
        'channel_layout': '',

        'i_stream': False,
    }

    # print(stderr)
    # print('')

    input_pattern = re.compile(r'(Input\s(.{,99999})\n)(((.{,99999})\n){,256})')
    find_input_stream = input_pattern.finditer(stderr)

    for match in find_input_stream:
        input_info = stderr[match.start():match.end()]

        v_stream_pattern = re.compile(r'(Video:\s.{,9999})' +
                                  r'((\n.{,9999}){,99}\sAudio:\s)')

        find_v_stream = v_stream_pattern.finditer(input_info)

        for match in find_v_stream:
            v_stream = input_info[match.start():match.end()]
            # print('video stream: ', v_stream)
            # print('')

            _meta['v_stream'] = True

            v_width_pattern = re.compile(r',\s[\d]{,4}x')
            find_v_width = v_width_pattern.finditer(v_stream)



            for match in find_v_width:
                v_width = v_stream[match.start():match.end()][2:-1]
                _meta['v_width'] = v_width

                # print(v_width)

            v_height_pattern = re.compile(r'x[\d]{,4}\s\[')
            find_v_height = v_height_pattern.finditer(v_stream)

            for match in find_v_height:
                v_height = v_stream[match.start():match.end()][1:-2]
                _meta['v_height'] = v_height

                # print(v_height)

            v_fmt_pattern = re.compile(r'Video:\s(([a-z|0-9]|[_]){,99}\s[(])')
            find_v_fmt = v_fmt_pattern.finditer(v_stream)

            for match in find_v_fmt:
                v_format = v_stream[match.start():match.end()][7:-2]
                # print('video format:', v_format)

                encoder_info = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})\s[^\n]{,9999}', re.IGNORECASE)
                find_encoder_info = encoder_info.finditer(v_stream)

                for match in find_encoder_info:
                    v_encoder = v_stream[match.start():match.end()]
                    # print('encoder string:', v_encoder)

                    v_codec_pattern = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})', re.IGNORECASE)
                    find_v_codec = v_codec_pattern.finditer(v_encoder)

                    for match in find_v_codec:
                        v_codec = v_encoder[match.end() + 1:]
                        # print('video codec:', v_codec)

        # print('')

        a_fmt = ''

        """
            Parse Audio Info
        """

        a_stream_pattern = re.compile(r'(Audio:\s.{,9999})' +
                                  r'(\n.{,9999}){,99}')
        find_a_stream = a_stream_pattern.finditer(input_info)

        for match in find_a_stream:
            a_stream = input_info[match.start():match.end()]
            _meta['a_stream'] = True

            # print('audio stream:', a_stream)
            # print('')

            a_sample_rate_pattern = re.compile(r'[\d]{,8}\sHz')
            find_a_sample_rate = a_sample_rate_pattern.finditer(a_stream)

            for match in find_a_sample_rate:
                unformated_a_sample_rate = a_stream[match.start():match.end()]
                a_sample_rate = a_stream[match.start():match.end()][:-3]
                _meta['a_sample_rate'] = a_sample_rate

                # print(a_sample_rate)




                channel_layout_pattern = re.compile(unformated_a_sample_rate + r',\s([^,]{,10}),')
                find_channel_layout = channel_layout_pattern.finditer(a_stream)

                for match in find_channel_layout:
                    unformated_channel_layout = a_stream[match.start():match.end()]
                    # print(unformated_channel_layout)

                    channel_layout = a_stream[match.start():match.end()][len(unformated_a_sample_rate)+2:-1]
                    _meta['channel_layout'] = channel_layout

                    # print(channel_layout)

                    a_fmt_pattern = re.compile(unformated_channel_layout + r'\s([^,]{,10}),')
                    find_a_fmt = a_fmt_pattern.finditer(a_stream)

                    for match in find_a_fmt:
                        a_fmt = a_stream[match.start():match.end()][len(unformated_channel_layout)+1:-1]
                        _meta['a_sample_fmt'] = a_fmt




            # a_format = re.compile(r'Audio:\s(([a-z|0-9]|[_]){,99}\s[(])')
            # find_a_format = a_format.finditer(a_stream)
            #
            # for match in find_a_format:
            #     a_fmt = a_stream[match.start():match.end()][7:-2]
            #     print('audio format:', a_fmt)
            #     time.sleep(2)

            encoder_info = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})\s[^\n|;]{,9999}', re.IGNORECASE)
            find_encoder_info = encoder_info.finditer(a_stream)

            for match in find_encoder_info:
                a_encoder = a_stream[match.start():match.end()]
                # print('encoder string:', a_encoder)

                a_codec_pattern = re.compile(r'(\s{6})encoder(\s{9}):\s(([^\s]){,99})', re.IGNORECASE)
                find_a_codec = a_codec_pattern.finditer(a_encoder)

                audio_codec = re.compile((f'{a_fmt}' + r'\s[(]([a-z|0-9]{,99})[)]'))
                find_a_codec = audio_codec.finditer(a_stream)

                for match in find_a_codec:
                    a_codec = a_encoder[match.end() + 1:]
                    # print('audio codec:', a_codec)

    return _meta


def pd_open(path):
    logger.info(f"Event: File open {path}")
    audio = pd.AudioSegment.from_file(path)
    return audio


def pd_bit_depth(audio):

    bit_depth = audio.sample_width  # 1-4. 1=8 2=16 3=24 4=32

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


def pd_sample_rate(audio):
    logger.info(f"Event: File sample rate {audio.frame_rate}")
    sample_rate = audio.frame_rate
    return sample_rate


# def pd_bit_depth(audio):
#
#     print('INPUT BIT-DEPTH: ', audio.sample_width)
#
#     # CHECK TO SEE IF BIT-DEPTH IS GREATER THAN SPECIFIED BIT-DEPTH
#     if audio.sample_width > settings.bit_depth:
#         print('CHANGING TO 24 OR HIGHER...')
#         audio = audio.set_sample_width(settings.bit_depth)
#
#     # IF 8 BIT CHANGE TO MINIMUM 16
#     elif audio.sample_width == 1:
#         audio = audio.set_sample_width(2)
#
#     else:
#         print('BIT-DEPTH LOWER THAN TARGET, SKIPPING...')
#
#     print('OUTPUT BIT-DEPTH: ', audio.sample_width)
#     print()
#     return audio


def pd_set_mono(audio):

    audio = audio.set_channels(1)
    print('SET_MONO() ')
    print()
    return audio


def pd_normalize_rms(audio):

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


def pd_gain_to_target(audio):

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


def pd_detect_leading_silence(audio, silence_threshold=-50.0, chunk_size=10):

    trim_ms = 0 # in ms

    assert chunk_size > 0 # to avoid infinite loop

    # start indexing the whole file
    while audio[0:trim_ms + chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size
        print(audio[0:trim_ms + chunk_size].dBFS)
        print(trim_ms)

    return trim_ms


def pd_strip_silence(audio):
    import time

    print('strip_silence()')

    # get length of file
    duration = len(audio)
    print('AUDIO DURATION (MS): ', duration)

    # find the silence from start
    start_trim = pd_detect_leading_silence(audio)
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


def pd_export(audio, in_name, out_path, extension):

    # out_name = out_path + '/' + in_name + extension

    audio.export(out_path)

    print('EXPORTED: ', out_path)
    print()

























# OLD METHOD: DISPATCH FFPROBE SUBPROCESS

"""
    We will run the ffmpeg console anytime a function is called, so we do not have to call it manually!
"""

console_cache = str
output = os.path.abspath('C:\\Users\\Aspen\\Desktop\\output.json')


def open_file(path):
    global console_cache

    path = os.path.abspath(path)


    # dumping to stder

    p = subprocess.Popen(['ffprobe', '-print_format', 'json', '-show_format', '-show_streams', path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1, universal_newlines=True)
    stdout, stderr = p.communicate()



    # dumping to log file

    # os.chdir('C:\\Users\\Aspen\\Desktop\\dump\\')
    # p = subprocess.Popen(['ffprobe', '-report', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1, universal_newlines=True)


    # starting a child and feeding it newlines

    # p = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1, universal_newlines=True)
    # p.stdin.write(f'ffprobe {path}\n')
    # p.stdin.flush()
    # print(p.stdout.readline())


    # dump JSON to file
    # p.stdin.write(f'ffprobe -print_format json -show_format -show_streams {path} > {output}')








    """
        Parse the JSON from string
    """

    metadata = json.loads(stdout)
    stream_count = metadata.get('streams')


    """
        Parse the JSON from file
    """

    # with open('C:\\Users\\Aspen\\Desktop\\output.json', 'r') as j:
    #     metadata = json.load(j)
    #     stream_count = metadata.get('streams')

    if not stream_count is None:

        for terms in stream_count:
            global sample_rate
            global bit_depth
            global bit_rate

            sample_rate = terms.get('sample_rate')
            bit_depth = terms.get('bits_per_sample')
            bit_rate = terms.get('bit_rate')

        print(sample_rate)
        print(bit_depth)
        print(bit_rate)
        print()

    # print(sample_rate)

    # metadata = json.loads('C:\\Users\\Aspen\\Desktop\\output.json')
    # print(metadata)

    # time.sleep(30)
    # logger.info(stderr)

    # console_cache = stderr
    # print(stdout, console_cache)

    # return console_cache


def frame_rate(path):

    index_frame_rate = re.compile(r'([0-9]{4,8})\sHz')
    find_frame_rate = index_frame_rate.finditer(console_cache)

    for m in find_frame_rate:
        start, end = m.span()  # match location

        frame_rate = console_cache[start:end]  # slice string

        f = frame_rate.find('Hz')  # clean up extension type
        frame_rate = int(frame_rate[:f])  # convert to int type

        return frame_rate


def bit_depth(path):

    index_bit_depth = re.compile(r'u8|s16|s32|flt|dbl|u8p|s16p|s32p|fltp|dblp|s64|s64p')
    find_bit_depth = index_bit_depth.finditer(console_cache)

    for m in find_bit_depth:
        start, end = m.span()

        sample_fmts = console_cache[start:end]

        dict = {
            8: ['u8', 'u8p'],
            16: ['s16', 's16p'],
            32: ['s32', 's32p', 'flt', 'fltp'],
            64: ['dbl', 'dblp', 's64', 's64p']
        }


        # if sample_fmts == 'u8' or 'u8p':
        #     bit_depth = 8
        #
        # if sample_fmts == 's16' or 's16p':
        #     bit_depth = 16
        #
        # if sample_fmts == 's32' or 's32p':
        #     bit_depth = 32
        #
        # if sample_fmts == 'flt' or 'fltp':
        #     bit_depth = 32
        #
        # # if sample_fmts == 'dbl' or 'dblp':
        # #     bit_depth = 64
        #
        # # if sample_fmts == 's64' or 's64p':
        # #     bit_depth = 64

        return sample_fmts



    # index_bit_depth = re.compile(r'\(([0-9]+)\sbit\)')
    # find_bit_depth = index_bit_depth.finditer(console_cache)
    #
    # for m in find_bit_depth:
    #     print(m)
    #     start, end = m.span()  # match location
    #
    #     bit_depth = console_cache[start+1:end-1]  # locate string
    #
    #     b = bit_depth.find('bit')  # clean up extension type
    #     bit_depth = int(bit_depth[:b])  # convert to int type
    #
    #     return bit_depth


def bit_rate(path):

    index_bit_rate = re.compile(r'bitrate:\s([0-9]{2,9})')
    find_bit_rate = index_bit_rate.finditer(console_cache)

    for m in find_bit_rate:
        start, end = m.span()  # match location

        bit_rate = console_cache[start:end]  # slice string

        bit_rate = bit_rate[9:]  # remove the first '9' for "bitrate: " **constant

        return bit_rate















    # fpinfo = json.loads(stderr)
    # print(json.dumps(fpinfo, indent=4))

    #
    # _possible_frames = ['8000','11025','16000','22050','32000','37800','44056','44100','47250','48000','50000','64000','88200','96000','176400','192000','3528000','2822400','5644800','11289600','22579200']
    # _possible_bit_depths = ['(8', '(16', '(24', '(32']
    # frame_rate = str
    # bit_depth = str
    #
    # for word in stderr.split():
    #     for frames in _possible_frames:
    #         if word == frames:
    #             frame_rate = frames
    #
    #     for depths in _possible_bit_depths:
    #         if word == depths:
    #             bit_depth = depths

    # logger.info(frame_rate)
    # logger.info(bit_depth)

    # print(stderr.split())
    # logger.info(stderr)

    # print(split)

    metadata = []
    # metadata.append(split)
    # print(metadata)


    # logger.info(stdout)
    # logger.info(stderr)



    # print(stderr.find('Hz'))


    # bitrate = stderr



    # while True:
        # logger.info(line)

    # if line:
    #     print(line)
    #     logger.info(line)