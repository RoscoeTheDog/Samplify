from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, case, or_
from database.db_setup import *
from database import av_handler
import os
import time
import logging
import app_settings
import shutil
import threading
import subprocess
import re
import bin.pd_functions as pd
import platform
from datetime import datetime
import img_handler


# connect engine and bind engine to metadata
engine = create_engine('sqlite:///' + app_settings.database_name)
Base.metadata.bind = engine

# declare MetaData, so we can view it later
meta = MetaData()

# declare a new sessionmaker and connect to database 'engine'
session = sessionmaker(bind=engine)

# you must also instantiate the session before querying
session = session()

# call our logger locally
logger = logging.getLogger('event_log')


# temporary data to test behavior
def insert_template():

    # INPUT FOLDERS
    entry = InputDirectories(folder_path='C:/Users/Aspen/Desktop/Input')
    session.add(entry)
    entry = InputDirectories(folder_path='D:/MOVIES & SHOWS')
    session.add(entry)
    entry = InputDirectories(folder_path='C:/Users/Aspen/Pictures')
    session.add(entry)

    # OUTPUT FOLDERS
    entry = OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/photos', extension='.png', a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='default',
                              image_only=True, a_normalize=False)
    session.add(entry)
    entry = OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/hat', extension='default', a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='1',
                              audio_only=True, a_normalize=False, a_strip_silence=False, a_silence_threshold='-80', reduce=False)
    session.add(entry)
    entry = OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/dragon ball', extension='.mp4', a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='default',
                              video_only=True, reduce=False)
    session.add(entry)

    # FILTER BY SEARCH TERMS
    entry = SearchTerms(folder_id=1, name=r'.')
    session.add(entry)
    entry = SearchTerms(folder_id=2, name=r'(hat)(?i)')
    session.add(entry)
    entry = SearchTerms(folder_id=3, name=r'(dragon)(?i)')
    session.add(entry)

    # DEFAULT TO MIN/MAX SEARCH-DATE VALUES UNLESS SPECIFIED
    for directory_entry in session.query(OutputDirectories):
        entry = SearchByDate(folder_id=directory_entry.id)
        session.add(entry)

    # # MANUALLY UPDATE SPECIFIC DATE IF DESIRED
    # for search_entry in session.query(SearchByDate).filter(SearchByDate.folder_id == 3):
    #
    #     if str(search_entry.start_by_date) == str(datetime.min) and str(search_entry.end_by_date) == str(datetime.max):
    #
    #         session.query(SearchByDate).filter(SearchByDate.id == search_entry.id).update(
    #         {'start_by_date': '2019-05-20'})
    #
    #         session.query(SearchByDate).filter(SearchByDate.id == search_entry.id).update(
    #         {'end_by_date': '2019-06-30'})

    # FILTER BY DATES CREATED
    # entry = SearchByDate(folder_id=1)
    # session.add(entry)
    # entry = SearchByDate(folder_id=2)
    # session.add(entry)
    # entry = SearchByDate(folder_id=3, start_by_date='01/05/2019', end_by_date='06/27/2019')  # if nothing is specified, min/max used
    # session.add(entry)
    # entry = SearchByDate(folder_id=4)


    # ADD
    session.commit()


def create_out_dirs():

    for directory_entry in session.query(OutputDirectories):
        path = directory_entry.folder_path

        if not os.path.exists(path):
            logger.info(f'Event: {path} does not exist! Creating new directory...')

            try:
                os.mkdir(path)

            except:
                logger.info(f'{path} NOT A VALID DIRECTORY STRING')


def update_directory_search_by_name():

    # default behavior for directory search by name
    if app_settings.default_name_searchby_directory is True:

        for d, s in session.query(OutputDirectories, SearchTerms):
            print(d, s)
            dir_name = os.path.basename(d.folder_path)

            print(dir_name, s.name)

            if dir_name != s.name:
                entry = SearchTerms(folder_id=d.id, name=dir_name)
                session.add(entry)

    else:
        for d, s in session.query(OutputDirectories, SearchTerms):
            dir_name = os.path.basename(d.folder_path)

            if dir_name == s.name:
                session.query(SearchTerms).filter(SearchTerms.name.like(f"&{dir_name}&")).delete(synchronize_session=False)
                logger.info(f"Event: Term removed {dir_name}")

    session.commit()


def start_program():

    t = threading.Thread(target=samplify())
    t.setDaemon(True)
    t.start()
    t.join()


    """
        Note: Keyboard Interrupt does not work *WITHIN* PyCharm!
    """

    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     print('interrupt detected')
    #     t.join()


def samplify():

    # FILTER BY SEARCH-TERMS
    for directory_entry, search_terms in session.query(OutputDirectories, SearchTerms).filter(OutputDirectories.id == SearchTerms.folder_id).all():

        print(f"Directory Path: {directory_entry.folder_path}, "
              f"Folder ID: {search_terms.folder_id}, "
              f"Term ID: {search_terms.id}, "
              f"Term: {search_terms.name} "
              )

        time.sleep(2)

        for file_entry in session.query(Files):
            logger.info(f'Event: Checking file: {file_entry.file_path}')


            # TODO: AUDIO CONVERSION
            if directory_entry.audio_only is True:

                if file_entry.v_stream is False and file_entry.a_stream is True:

                    for audio_entry in session.query(FilesAudio).filter(FilesAudio.file_path == file_entry.file_path):

                        pattern = re.compile(search_terms.name)
                        filename_search = pattern.finditer(audio_entry.file_name)

                        for match in filename_search:

                            # IS BETWEEN DATES?
                            for date_entry in session.query(SearchByDate).filter(SearchByDate.folder_id == directory_entry.id):
                                logger.info(f'Event: Checking file date {audio_entry.file_path} {audio_entry.creation_date}')

                                if check_date(audio_entry.creation_date, date_entry.start_by_date, date_entry.end_by_date) is True:

                                    """
                                        Local Variables
                                    """

                                    # METADATA
                                    extension = directory_entry.extension
                                    sample_rate = directory_entry.a_sample_rate
                                    bit_depth = audio_entry.a_bit_depth
                                    channels = directory_entry.a_channels
                                    sample_fmt = directory_entry.a_sample_fmt

                                    # check for term 'default'
                                    if extension == 'default':
                                        extension = audio_entry.extension
                                    if sample_rate == 'default':
                                        sample_rate = audio_entry.a_sample_rate
                                    if sample_fmt == 'default':
                                        sample_fmt = audio_entry.a_sample_fmt
                                    if channels == 'default':
                                        channels = audio_entry.a_channels

                                    # I/O
                                    file_name = audio_entry.file_name
                                    input = os.path.abspath(audio_entry.file_path)
                                    output = os.path.abspath(f"{directory_entry.folder_path}/{file_name}{extension}")

                                    # OTHER
                                    normalize = directory_entry.a_normalize
                                    strip_silence = directory_entry.a_strip_silence
                                    silence_threshold = directory_entry.a_silence_threshold
                                    reduce = directory_entry.reduce

                                    # NO CHANGE; SIMPLE COPY
                                    if extension == audio_entry.extension and sample_rate == audio_entry.a_sample_rate and sample_fmt == audio_entry.a_sample_fmt and channels == audio_entry.a_channels and normalize is False and strip_silence is False:
                                        print('trying Copy Method...')
                                        copy(audio_entry.file_path, directory_entry.folder_path)

                                    # NORMALIZATION or STRIP SILENCE (FFMPEG)
                                    elif normalize or strip_silence is True:
                                        print('trying FFmpeg Method...')
                                        logger.info(f'Event: File {input} {sample_rate} {sample_fmt} {channels} {normalize} {strip_silence}')


                                        # TODO: convert configure_args to pass a dict instead?
                                        ff_args = av_handler.configure_args(
                                            input=input,
                                            output=output,
                                            gpu_vendor=app_settings.gpu_vendor,
                                            v_stream=audio_entry.v_stream,
                                            a_stream=audio_entry.a_stream,
                                            sample_rate=sample_rate,
                                            bit_depth=bit_depth,
                                            channels=channels,
                                            normalize=normalize,
                                            strip_silence=strip_silence,
                                            silence_threshold=silence_threshold,
                                            reduce=reduce
                                        )

                                        av_handler.convert_ffmpeg(ff_args)


                                    # VANILLA TRANSCODING (PyAV [fastest])
                                    elif bool(session.query(SupportedExtensions).filter(SupportedExtensions.name == extension).first()) is True:

                                        for config in session.query(SupportedExtensions).filter(SupportedExtensions.name == extension):

                                            logger.info(f"Filename: {audio_entry.file_name}{audio_entry.extension}, "
                                                        f"a_codec: {config.a_codec} "
                                                        f"sample_rate: {sample_rate}, "
                                                        f"bit_depth: {bit_depth}, "
                                                        f"sample_fmt: {sample_fmt}, "
                                                        f"channel_layout: {channels}")

                                            av_handler.convert_pyav(input=input,
                                                               output=output,
                                                               file_name=file_name,
                                                               extension=extension,
                                                               a_codec=config.a_codec,
                                                               v_codec=config.v_codec,
                                                               channels=channels,
                                                               sample_rate=sample_rate,
                                                               sample_fmt=sample_fmt,
                                                               )

                                    # FFMPEG CONVERT (& STORE CODEC/EXTENSION INFO)
                                    else:
                                        print('Could not find codec!')
                                        print('starting ffmpeg...')

                                        ff_args = av_handler.configure_args(
                                            input=input,
                                            output=output,
                                            gpu_vendor=app_settings.gpu_vendor,
                                            v_stream=audio_entry.v_stream,
                                            a_stream=audio_entry.a_stream,
                                            sample_rate=sample_rate,
                                            bit_depth=bit_depth,
                                            channels=channels,
                                            normalize=normalize,
                                            strip_silence=strip_silence,
                                            silence_threshold=silence_threshold,
                                            reduce=reduce
                                        )

                                        # show args
                                        print(ff_args)

                                        # dispatch to FFmpeg
                                        stdout, stderr = av_handler.convert_ffmpeg(ff_args)

                                        # parse FFmpeg output
                                        v_format, v_codec, a_format, a_codec = av_handler.parse_ffmpeg(stdout, stderr)[1:]

                                        # insert new metadata into database
                                        store_codec_config(extension, v_format, v_codec, a_format, a_codec, sample_rate, channels)

                            break  # break search-pattern after processing



            # TODO: VIDEO CONVERSION
            elif directory_entry.video_only is True:

                if file_entry.v_stream is True:

                    for video_entry in session.query(FilesVideo).filter(FilesVideo.file_path == file_entry.file_path):

                        pattern = re.compile(search_terms.name)
                        filename_search = pattern.finditer(video_entry.file_name)

                        for match in filename_search:

                            # IS BETWEEN DATES?
                            for date_entry in session.query(SearchByDate).filter(SearchByDate.folder_id == directory_entry.id):
                                logger.info(f'Event: Check file creation date {video_entry.file_path} {video_entry.creation_date}')

                                if check_date(video_entry.creation_date, date_entry.start_by_date, date_entry.end_by_date) is True:

                                    # METADATA
                                    extension = directory_entry.extension
                                    sample_rate = directory_entry.a_sample_rate
                                    channels = directory_entry.a_channels
                                    sample_fmt = directory_entry.a_sample_fmt
                                    bit_depth = ''

                                    # check for default properties
                                    if extension == 'default':
                                        extension = video_entry.extension
                                    if sample_rate == 'default':
                                        sample_rate = video_entry.a_sample_rate
                                    if sample_fmt == 'default':
                                        sample_fmt = video_entry.a_sample_fmt
                                    if channels == 'default':
                                        channels = video_entry.a_channels

                                    # I/O
                                    file_name = video_entry.file_name
                                    input = os.path.abspath(video_entry.file_path)
                                    output = os.path.abspath(f"{directory_entry.folder_path}/{file_name}{extension}")

                                    # FFMPEG CONVERT (& STORE CODEC/EXTENSION INFO)
                                    # print('starting ffmpeg...')


                                    # TODO: CHANGE VIDEO ARGS SO IT CAN ACCEPT ADDITIONAL FILTERS
                                    normalize = False
                                    strip_silence = False
                                    silence_threshold = -80
                                    reduce = False

                                    logger.info(f"Filename: {video_entry.file_name}{video_entry.extension}, "
                                                # f"a_codec: {config.a_codec}"
                                                f"sample_rate: {sample_rate}, "
                                                # f"bit_depth: {bit_depth}, "
                                                f"sample_fmt: {sample_fmt}, "
                                                f"channels: {channels}")

                                    ff_args = av_handler.configure_args(input=input,
                                                                        output=output,
                                                                        gpu_vendor=app_settings.gpu_vendor,
                                                                        v_stream=video_entry.v_stream,
                                                                        a_stream=video_entry.a_stream,
                                                                        sample_rate=sample_rate,
                                                                        bit_depth=bit_depth,
                                                                        channels=channels,
                                                                        normalize=normalize,
                                                                        strip_silence=strip_silence,
                                                                        silence_threshold=silence_threshold,
                                                                        reduce=reduce
                                                                        )

                                    # show args
                                    # print(ff_args)

                                    # dispatch to FFmpeg
                                    stdout, stderr = av_handler.convert_ffmpeg(ff_args)

                                    # print(stderr)

                                    """
                                        Since ffmpeg prints to stderr instead of stdout, we cannot use a try/except.
                                        Instead, manually check for status of export to ensure we aren't skipping files.
                                    """

                                    # check file status
                                    export, *_ = av_handler.parse_ffmpeg(stdout, stderr)

                                    # disable gpu_codecs if failed
                                    if export is False:
                                        logger.warning('Warning: Export failed! Disabling hardware acceleration')

                                        logger.info(f"Filename: {video_entry.file_name}{video_entry.extension}, "
                                                    # f"a_codec: {config.a_codec}"
                                                    f"sample_rate: {sample_rate}, "
                                                    # f"bit_depth: {bit_depth}, "
                                                    f"sample_fmt: {sample_fmt}, "
                                                    f"channel_layout: {channels}")

                                        ff_args = av_handler.configure_args(input=input,
                                                                            output=output,
                                                                            gpu_vendor='',
                                                                            v_stream=video_entry.v_stream,
                                                                            a_stream=video_entry.a_stream,
                                                                            sample_rate=sample_rate,
                                                                            bit_depth=bit_depth,
                                                                            channels=channels,
                                                                            normalize=normalize,
                                                                            strip_silence=strip_silence,
                                                                            silence_threshold=silence_threshold,
                                                                            reduce=reduce
                                                                            )

                                        # show args
                                        # print(ff_args)

                                        # dispatch to FFmpeg
                                        stdout, stderr = av_handler.convert_ffmpeg(ff_args)

                                        # print(stderr)  # verbose enable (debugging)

                            break  # avoid re-iterations for multiple actions on same file



                # TODO: impliment some *other* file type handling
                else:
                    logger.warning(f'Warning: {file_entry.extension} is not valid file')


            # TODO: IMAGE CONVERSION
            elif directory_entry.image_only is True:

                for image_entry in session.query(FilesImage).filter(FilesImage.file_path == file_entry.file_path):

                    pattern = re.compile(search_terms.name)
                    filename_search = pattern.finditer(image_entry.file_name)

                    for match in filename_search:

                        # IS BETWEEN DATES?
                        for date_entry in session.query(SearchByDate).filter(SearchByDate.folder_id == directory_entry.id):

                            logger.info(f'Event: Checking file date {image_entry.file_path} {image_entry.creation_date}')

                            if check_date(image_entry.creation_date, date_entry.start_by_date,
                                          date_entry.end_by_date) is True:

                                """
                                    Local Variables
                                """

                                # METADATA
                                extension = directory_entry.extension

                                # check for term 'default'
                                if extension == 'default':
                                    extension = image_entry.extension

                                # I/O
                                file_name = image_entry.file_name
                                input = os.path.abspath(image_entry.file_path)
                                output = os.path.abspath(f"{directory_entry.folder_path}/{file_name}{extension}")

                                # OTHER

                                # NO CHANGE; SIMPLE COPY

                                # if extension == image_entry.extension:
                                print('trying Copy Method...')
                                copy(input, directory_entry.folder_path)

                        break  # avoid re-iterations for multiple actions on same file




def check_date(file_date, start, end):

    # date = datetime.strptime(file_date, '%m/%d/%Y')
    # start = datetime.strptime(start, '%m/%d/%Y')
    # end = datetime.strptime(end, '%m/%d/%Y')

    # print('date_created', file_date)
    # print('start', start)
    # print('end', end)

    if start <= file_date <= end:
        return True

    else:
        return False




def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """

    if platform.system() == 'Windows':
        date = datetime.fromtimestamp(os.path.getctime(path_to_file)).strftime('%Y-%m-%d')
        return date

    # TODO: Test this code block on other platforms (OS X/Linux)

    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def learn_extension(file):
    extension = os.path.splitext(file)[1]

    process = subprocess.Popen(['ffprobe', '-i', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    # print(stdout, stderr)

    stream = re.compile(r'(Audio:\s|Video:\s)')
    find_stream = stream.finditer(stderr)

    is_valid = False

    for match in find_stream:
        print('Found stream', f'"{stderr[match.start():match.end()]}"')
        is_valid = True


    if is_valid is True:
        print(extension, 'is supported!')

        entry = bool(session.query(SupportedExtensions).filter(SupportedExtensions.name == extension).first())

        if not entry is True:
            entry = SupportedExtensions(name=extension)
            session.add(entry)
            session.commit()


    if is_valid is False:
        print(extension, 'is unsupported!')

        entry = bool(session.query(UnsupportedExtensions).filter(UnsupportedExtensions.name == extension).first())

        if not entry is True:
            entry = UnsupportedExtensions(name=extension)
            session.add(entry)
            session.commit()





def store_codec_config(extension_type, v_format, v_codec, a_format, a_codec, sample_rate, channel_size):

    print(extension_type, v_format, v_codec, a_format, a_codec)

    entry = SupportedExtensions(name=extension_type, v_format=v_format, v_codec=v_codec, a_format=a_format, a_codec=a_codec, sample_rate=sample_rate, channel_size=channel_size)

    entry_exist = bool(session.query(SupportedExtensions).filter(SupportedExtensions.name == extension_type,
                                                            SupportedExtensions.v_format == v_format,
                                                            SupportedExtensions.v_codec == v_codec,
                                                            SupportedExtensions.a_format == a_format,
                                                            SupportedExtensions.a_codec == a_codec,
                                                            SupportedExtensions.sample_rate,
                                                            SupportedExtensions.channel_size).first())

    if not entry_exist is True:
        session.add(entry)
        session.commit()




def copy(input, output):

    _basename = os.path.basename(input)

    output = os.path.join(output, _basename)
    output = os.path.abspath(output)

    # check to see if copied already
    if not os.path.exists(output):
        logger.info(f"Event: File copied from {input} to {output}")
        shutil.copy(input, output)

    else:
        logger.info(f"Event: File already exists {output}")


def db_print():

    meta.reflect(engine)

    for table in meta.tables.values():
        print('Table Info: ' + f'{table}')
        for row in session.query(table):
            print(row)

    session.close_all()


def scan_files():

    # event log
    logger.info(f"Event: Start input Scan")
    time.sleep(2)

    for row in session.query(InputDirectories):
        # local vars
        path = row.folder_path

        # working os. directory
        os.chdir(path)

        # event log
        logger.info(f"Event: Folder scan {path} {os.path.isdir(path)}")

        for root, directory, files in os.walk(path):

            for f in files:
                # merge our strings
                path = os.path.join(root, f)
                path = os.path.abspath(path)  # cleanup backslashes (Note: bug when nesting abspath and join-- use seperately)

                # log the event
                logger.info(f"Event: File scan {path} {os.path.isdir(path)}")

                # remove /paths/ from string
                _basename = os.path.basename(path)

                # isolate file_name string
                file_name = os.path.splitext(_basename)[0]

                # isolate .ext string
                extension_name = os.path.splitext(_basename)[1]

                # get creation date
                date = creation_date(path)

                # collect meta-data from PyAV
                meta_dict = av_handler.meta_info(path)

                if meta_dict['succeeded'] is False:
                    stdout, stderr = av_handler.meta_ffprobe(path)
                    meta_dict = av_handler.parse_ffprobe(stdout, stderr)
                    print(meta_dict)

                    # time.sleep(10)

                # VIDEO TABLE
                if meta_dict['v_stream'] is True:

                    entry = FilesVideo(
                        file_path=path,
                        file_name=file_name,
                        extension=extension_name,
                        creation_date=date,
                        v_stream=meta_dict['v_stream'],
                        v_width=meta_dict['v_width'],
                        v_height=meta_dict['v_height'],
                        v_frame_rate=meta_dict['v_frame_rate'],
                        v_pix_format=meta_dict['v_pix_fmt'],
                        v_is_rgb=meta_dict['v_is_rgb'],
                        a_stream=meta_dict['a_stream'],
                        a_sample_rate=meta_dict['a_sample_rate'],
                        a_bit_depth=meta_dict['a_bit_depth'],
                        a_sample_fmt=meta_dict['a_sample_fmt'],
                        a_bit_rate=meta_dict['a_bit_rate'],
                        a_channels=meta_dict['channels'],
                        a_channel_layout=meta_dict['channel_layout']
                    )

                    session.add(entry)

                # AUDIO TABLE
                elif meta_dict['v_stream'] is False and meta_dict['a_stream'] is True:

                    entry = FilesAudio(
                        file_path=path,
                        file_name=file_name,
                        extension=extension_name,
                        creation_date=date,
                        v_stream=meta_dict['v_stream'],
                        a_stream=meta_dict['a_stream'],
                        i_stream=meta_dict['i_stream'],
                        a_sample_rate=meta_dict['a_sample_rate'],
                        a_bit_depth=meta_dict['a_bit_depth'],
                        a_sample_fmt=meta_dict['a_sample_fmt'],
                        a_bit_rate=meta_dict['a_bit_rate'],
                        a_channels=meta_dict['channels'],
                        a_channel_layout=meta_dict['channel_layout']
                    )

                    session.add(entry)

                # IMG TABLE
                # TODO: troubleshoot img class and get meta-info into database
                if meta_dict['v_stream'] is False and meta_dict['a_stream'] is False:

                    try:
                        file = img_handler.ImageHandler()
                        img_meta = file.meta_info(input=path)

                        entry = FilesImage(
                            file_path=path,
                            file_name=file_name,
                            extension=extension_name,
                            creation_date=date,
                            i_stream=img_meta['i_stream'],
                            i_fmt=img_meta['format'],
                            i_frames=img_meta['frames'],
                            i_width=img_meta['width'],
                            i_height=img_meta['height'],
                            i_alpha=img_meta['alpha_channel']
                        )

                        session.add(entry)


                    except Exception as e:
                        logger.warning(f'Warning: {e}')


                # OTHER TABLE
                entry = Files(file_path=path, file_name=file_name, extension=extension_name, creation_date=date,
                              v_stream=meta_dict['v_stream'], a_stream=meta_dict['a_stream'], i_stream=meta_dict['i_stream'])

                session.add(entry)

            # write everything to database
            session.commit()


def get_root_output(path):

    os.chdir(path)
    for root, directory, files in os.walk(path):

        for folder_name in directory:
            # join to fix root/child-directory problem
            path = os.path.join(root, folder_name)
            # abspath to fix backslashes
            path = os.path.abspath(path)
            # basename for name of folder
            name = os.path.basename(path)

            # log the event
            logger.info(f"Event: Folder scan {path}")

            # create our object
            entry = OutputDirectories(folder_path=path)

            # add object to session
            session.add(entry)

            # log event
            logger.info(F"Event: Folder added {path}")

            # flush buffer to get primary id
            session.flush()

            if app_settings.default_name_searchby_directory is True:

                # create new entry for default search terms.
                entry = SearchTerms(folder_id=entry.id, name=name)
                session.add(entry)

    # write everything to database
    session.commit()


def start_input_cache():

    # to avoid duplicates, completely rewrite cache each time
    app_settings.input_cache = []

    for root, directory, files in os.walk(app_settings.input_path):
        # fix backslash extensionting
        r = os.path.abspath(root)
        # then add
        app_settings.input_cache.append(r)

    logger.info(f'Event: Start input monitor cache ')


def start_output_cache():

    # to avoid duplicates, completely rewrite cache each time
    app_settings.output_cache = []

    for root, directory, files in os.walk(app_settings.output_path):
        # fix backslash extensionting
        r = os.path.abspath(root)
        # then add
        app_settings.output_cache.append(r)

    logger.info(f'Event: Start output monitor cache ')


def insert_input_folder(path):

    entry = Files(file_path=path)
    session.add(entry)

    session.commit()


def remove_input_folder(path):

    # filtering by the full path also allows us to also remove the children of the directory
    for entry in session.query(Files.file_path).filter(Files.file_path.like(f'%{path}%')):
        logger.info(f'Event: Folder deleted: {entry} True')

    # synchronize session allows deletion OUTSIDE of the session cache
    session.query(Files.file_path).filter(Files.file_path.like(f'%{path}%')).delete(synchronize_session=False)

    session.commit()


def insert_output_folder(path):

    name = os.path.basename(path)

    entry = OutputDirectories(folder_path=path)

    session.add(entry)

    # Do we need to add default folder search terms?
    if app_settings.default_name_searchby_directory is True:

        # flush session to gain access to entry columns while in buffer
        session.flush()

        entry = SearchTerms(folder_id=entry.id, name=name)

        session.add(entry)

    session.commit()


def remove_output_folder(path):

    # filtering by the full path also allows us to also remove the child results from the directory
    for entry in session.query(OutputDirectories).filter(OutputDirectories.folder_path.like(f'%{path}%')):

        logger.info(f'Event: Folder deleted: {entry.folder_path} True')

        session.query(SearchTerms).filter(entry.id == SearchTerms.folder_id).delete(synchronize_session=False)

        session.query(OutputDirectories).filter(OutputDirectories.id == entry.id).delete(synchronize_session=False)



    """
        Because output_cache cannot update fast enough in-between dispatched events,
        we need to check and delete the differences that are updated after the missed intervals
        
    """
    for r in session.query(OutputDirectories).filter(OutputDirectories.folder_path):
        print(r.folder_path, app_settings.output_cache)
        if not r.folder_path in app_settings.output_cache:
            session.query(SearchTerms).filter(r.id == SearchTerms.folder_id).delete(synchronize_session=False)
            session.query(OutputDirectories).filter(r.folder_path).delete(synchronize_session=False)



    session.commit()


def insert_file(path, frame_rate, bit_depth, bit_rate):

    entry = Files(file_path = f"{path}", frame_rate = f'{frame_rate}', bit_depth = f"{bit_depth}", bit_rate = f"{bit_rate}")

    session.add(entry)

    session.commit()


def remove_file(path):

    session.query(Files).filter_by(file_path = f"{path}").delete()

    session.commit()

    db_print()