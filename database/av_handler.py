import subprocess
import logging
import re
import json
import av
import av.filter
import os
from bin import pd_functions as pd
import glob
import app_settings
import time
from database import db_handler

logger = logging.getLogger('event_log')
number = 0


def meta_info(input):

    # declare dict so if fail, still inserts to DB
    meta_dict = {
        'succeeded': True,

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

    # need to filter out by extension type to avoid copy/move errors
    if not 'desktop.ini' in input:

        try:
            container = av.open(input)

            for frame in container.decode(audio=0):
                channels = frame.layout.channels  # verbose method

                meta_dict['channel_layout'] = frame.layout.name

                num = 0
                for ch in channels:  # numerical method
                    num = num + 1

                meta_dict['channels'] = num

                break  # we don't need to decode all frames to get metadata info

            for s in container.streams:

                meta_dict['a_bit_rate'] = container.bit_rate / 1000

                # do stuff with video stream
                if s.type == 'video':
                    meta_dict['v_stream'] = True

                    # container resolution
                    meta_dict['v_width'] = s.width
                    meta_dict['v_height'] = s.height

                    # actual encoded resolution
                    meta_dict['v_buffer_width'] = s.coded_width
                    meta_dict['v_buffer_height'] = s.coded_height



                    """
                        commented-out code shows some additional video API
                    """

                    # print('video resolution:', v_width, v_height)
                    # print('buffer dimensions:', v_buffer_width, v_buffer_height)

                    # v_frame_rate = float(s.rate)
                    # print(v_frame_rate)
                    #
                    # v_pix_fmt =s.pix_fmt
                    # print(v_pix_fmt)
                    #
                    # v_is_rgb = s.format.is_rgb
                    # print(v_is_rgb)

                    # b_frames = s.has_b_frames
                    # print(b_frames)

                    # gop_size = s.gop_size
                    # print(gop_size)

                # do stuff with audio stream
                if s.type == 'audio':
                    meta_dict['a_stream'] = True
                    meta_dict['a_sample_fmt'] = s.format.name
                    meta_dict['a_sample_rate'] = s.sample_rate
                    meta_dict['a_bit_depth'] = s.format.bits

            return meta_dict

        except Exception as e:
            logger.warning(f'Warning: {input} not an audio or video file!')
            meta_dict['succeeded'] = False

            return meta_dict

    else:
        logger.warning(f'Warning: desktop.ini not a modifiable file')

        return meta_dict


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
        app_settings.exception_counter = app_settings.exception_counter + 1
        logger.info('Could not convert the file:\n'
                    f'{e}')


def convert_ffmpeg(ff_args):

    process = subprocess.Popen(ff_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()

    return stdout, stderr


def convert_pydub(in_path, in_name, out_path, extension):

    audio = pd.open_audio(in_path)
    # audio = pd.set_mono(audio)
    audio = pd.strip_silence(audio)
    # audio = pd.normalize_rms(audio)
    pd.export(audio, in_name, out_path, extension)
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


def meta_ffprobe(input):

    ff_args = ['ffprobe', '-i', input]

    process = subprocess.Popen(ff_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()

    return stdout, stderr


def parse_ffprobe(stdout, stderr):

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

                print(a_sample_rate)




                channel_layout_pattern = re.compile(unformated_a_sample_rate + r',\s([^,]{,10}),')
                find_channel_layout = channel_layout_pattern.finditer(a_stream)

                for match in find_channel_layout:
                    unformated_channel_layout = a_stream[match.start():match.end()]
                    # print(unformated_channel_layout)

                    channel_layout = a_stream[match.start():match.end()][len(unformated_a_sample_rate)+2:-1]
                    _meta['channel_layout'] = channel_layout

                    print(channel_layout)

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
                    print('audio codec:', a_codec)

    return _meta






















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



    import time
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