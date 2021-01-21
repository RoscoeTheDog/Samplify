import database.database_setup as dbs
import os
import time
import shutil
import threading
import subprocess
import re
import platform
from datetime import datetime
from app import settings
from handlers import av_handler, image_handler, file_handler
import structlog
import queue
import multiprocessing

# call our logger locally
logger = structlog.get_logger('samplify.log')


class NewHandler:

    def __init__(self, mp):
        self.session = dbs.session
        self.process_manager = mp
        self.get_files_lock = threading.Lock()
        self.get_audio_lock = threading.Lock()
        self.thread_list = []

    # def consumer(self):
    #
    #     while True:
    #
    #         if not self.file_queue.full():
    #             pass

    def return_current_session(self):
        return self.session

    # TODO: cleanup deprecated method
    # Insert temporary data for testing behavior
    def insert_template(self):

        # INPUT FOLDERS
        # entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Desktop/Input/4-HiHat')
        # self.session.add(entry)
        # entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Desktop/Input/1-Kick')
        # self.session.add(entry)
        # entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Desktop/Input/1-Kick/Acoustic')
        # self.session.add(entry)
        # entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Desktop/Input/1-Kick/Basics')
        # self.session.add(entry)

        # entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Pictures')
        # self.session.add(entry)
        #
        # entry = dbs.InputMonitoringExclusions(folder_path='C:/Users/Aspen/Desktop/Input/1-Kick/Dubstep')
        # self.session.add(entry)

        # entry = dbs.InputDirectories(folder_path='C:/')
        # self.session.add(entry)
        entry = dbs.InputDirectories(folder_path='D:/MOVIES & SHOWS')
        self.session.add(entry)
        # entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Pictures')
        # self.session.add(entry)

        # laptop test directories
        entry = dbs.InputDirectories(folder_path='C:/Users/Aspen/Desktop/Input/')
        self.session.add(entry)
        # entry = dbs.InputDirectories(folder_path='C:/Users/Admin/Desktop/Input/Sample Videos')
        # self.session.add(entry)

        # OUTPUT FOLDERS
        entry = dbs.OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/photos', extension='.png', i_fmt='PNG',
                                  a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='default',
                                  image_only=True, a_normalize=False)
        self.session.add(entry)

        entry = dbs.OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/kick', extension='default', a_channels='1',
                                  audio_only=True, a_normalize=False, a_strip_silence=False, a_silence_threshold='-80',
                                  reduce=False)
        self.session.add(entry)

        entry = dbs.OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/hat', extension='default',
                                  a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='1',
                                  audio_only=True, a_normalize=False, a_strip_silence=False, a_silence_threshold='-80',
                                  reduce=False)
        self.session.add(entry)

        entry = dbs.OutputDirectories(folder_path='C:/Users/Aspen/Desktop/Output/dragon ball', extension='.mp4',
                                  a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='default',
                                  video_only=True, reduce=False)
        self.session.add(entry)

        # # laptop test outputs
        # entry = dbs.OutputDirectories(folder_path='C:/Users/Admin/Desktop/Output/photos', extension='.png', i_fmt='PNG',
        #                           a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='default',
        #                           image_only=True, a_normalize=False)
        # self.session.add(entry)
        #
        # entry = dbs.OutputDirectories(folder_path='C:/Users/Admin/Desktop/Output/hat', extension='default',
        #                           a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='1',
        #                           audio_only=True, a_normalize=False, a_strip_silence=False, a_silence_threshold='-80',
        #                           reduce=False)
        # self.session.add(entry)
        #
        # entry = dbs.OutputDirectories(folder_path='C:/Users/Admin/Desktop/Output/dragon ball', extension='.mp4',
        #                           a_sample_rate='default', a_bit_rate='', a_sample_fmt='default', a_channels='default',
        #                           video_only=True, reduce=False)
        # self.session.add(entry)

        # FILTER BY SEARCH TERMS
        entry = dbs.SearchTerms(folder_id=1, name=r'.')
        self.session.add(entry)
        entry = dbs.SearchTerms(folder_id=2, name=r'(hat)(?i)')
        self.session.add(entry)
        entry = dbs.SearchTerms(folder_id=3, name=r'(dragon)(?i)')
        self.session.add(entry)

        # laptop filter by search terms
        entry = dbs.SearchTerms(folder_id=4, name=r'.')
        self.session.add(entry)
        entry = dbs.SearchTerms(folder_id=5, name=r'(hat)(?i)')
        self.session.add(entry)
        entry = dbs.SearchTerms(folder_id=6, name=r'(dragon)(?i)')
        self.session.add(entry)

        # DEFAULT TO MIN/MAX SEARCH-DATE VALUES UNLESS SPECIFIED
        for directory_entry in self.session.query(dbs.OutputDirectories):
            entry = dbs.SearchByDate(folder_id=directory_entry.id)
            self.session.add(entry)

        # # MANUALLY UPDATE SPECIFIC DATE IF DESIRED
        # for search_entry in self.session.query(dbs.SearchByDate).filter(dbs.SearchByDate.folder_id == 3):
        #
        #     if str(search_entry.start_by_date) == str(datetime.min) and str(search_entry.end_by_date) == str(datetime.max):
        #
        #         self.session.query(dbs.SearchByDate).filter(dbs.SearchByDate.id == search_entry.id).update(
        #         {'start_by_date': '2019-05-20'})
        #
        #         self.session.query(dbs.SearchByDate).filter(dbs.SearchByDate.id == search_entry.id).update(
        #         {'end_by_date': '2019-06-30'})

        # FILTER BY DATES CREATED
        # entry = dbs.SearchByDate(folder_id=1)
        # self.session.add(entry)
        # entry = dbs.SearchByDate(folder_id=2)
        # self.session.add(entry)
        # entry = dbs.SearchByDate(folder_id=3, start_by_date='01/05/2019', end_by_date='06/27/2019')  # if nothing is specified, min/max used
        # self.session.add(entry)
        # entry = dbs.SearchByDate(folder_id=4)

        # insert all preferences into database
        self.session.commit()

    def create_directories(self):

        for directory_entry in self.session.query(dbs.OutputDirectories):
            path = directory_entry.folder_path

            if not os.path.exists(path):
                logger.warning(f'admin_message', f'path does not exist', path=path)

                try:
                    os.mkdir(path)
                    logger.info(f'admin_message', f'new directory created', path=path)

                except Exception as e:
                    logger.error(f'admin_message', f'path is not a valid directory', path=path, exc_info=e)

    def validate_outputs(self):

        logger.info('user_message', msg=f'Validating output structure')

        for directory_entry in self.session.query(dbs.OutputDirectories):

            path = directory_entry.folder_path

            if not os.path.exists(path):
                logger.warning(f'admin_message', msg=f'output directory does not exist', path=path)

                try:
                    os.mkdir(path)
                    logger.info(f'admin_message', msg=f'new output directory created', path=path)

                except Exception as e:
                    logger.error(f'admin_message', msg='path is not a valid directory location', exc_info=e)

    def filter_children_directories(self):

        # filter out children from hierarchy first.
        hierarchy = []

        # create a list of folder paths
        for folder_entry in self.session.query(dbs.InputDirectories):
            hierarchy.append(folder_entry.folder_path)

        # call function to filter out child paths from parents.
        parent_list = file_handler.get_parents_in_hierarchy(hierarchy)

        return parent_list

    # def update_directory_search_by_name(self):
    #
    #     # default behavior for directory search by name
    #     if settings.default_name_searchby_directory is True:
    #
    #         for d, s in self.session.query(dbs.OutputDirectories, dbs.SearchTerms):
    #             print(d, s)
    #             dir_name = os.path.basename(d.folder_path)
    #
    #             print(dir_name, s.name)
    #
    #             if dir_name != s.name:
    #                 entry = dbs.SearchTerms(folder_id=d.id, name=dir_name)
    #                 self.session.add(entry)
    #
    #     else:
    #         for d, s in self.session.query(dbs.OutputDirectories, dbs.SearchTerms):
    #             dir_name = os.path.basename(d.folder_path)
    #
    #             if dir_name == s.name:
    #                 self.session.query(dbs.SearchTerms).filter(dbs.SearchTerms.name.like(f"&{dir_name}&")).delete(synchronize_self.session=False)
    #                 logger.info(f"Event: Term removed {dir_name}")
    #
    #     self.session.commit()

    def start_program(self):

        t = threading.Thread(target=self.samplify())
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
    # def get_rules_threaded(self):
    #
    #     # SORT BY RULES
    #     for directory_entry, search_terms in self.handler.session.query(dbs.OutputDirectories, dbs.SearchTerms).filter(
    #             dbs.OutputDirectories.id == dbs.SearchTerms.folder_id).all():
    #         logger.info('user_message', msg=f"syncing folder",
    #                     path=directory_entry.folder_path,
    #                     folder_id=directory_entry.id,
    #                     term_id=search_terms.id,
    #                     term=search_terms.name)

    def get_entries_Files(self):
        file_list = []

        for file_entry in self.session.query(dbs.Files):
            file_list.append(file_entry)

        return file_list


    def get_files_threaded(self):
        self.file_queue = []

        def consumer():
            self.get_files_lock.acquire()
            for file_entry in self.session.query(dbs.Files):
                logger.info(f'admin_message', f'working file path', path=file_entry.file_path)

                if len(self.file_queue) < multiprocessing.cpu_count():
                    self.file_queue.append(file_entry)
                else:
                    for task in self.file_queue:
                        print(task.file_path)
                    print('blocking get_files_threaded')
                    self.get_files_lock.acquire()

        def create_thread():
            tasker = threading.Thread(target=consumer(),)
            tasker.isDaemon()
            tasker.start()
            self.thread_list.append(tasker)

        create_thread();

    def get_audio_threaded(self):
        self.audio_queue = []

        def consumer():
            self.get_audio_lock.acquire()

            for file_entry in self.file_queue:

                for audio_entry in self.session.query(dbs.FilesAudio).filter(
                        dbs.FilesAudio.file_path == file_entry.file_path):

                    if len(self.audio_queue) < multiprocessing.cpu_count():
                        self.audio_queue.append(file_entry)
                    else:
                        for task in self.audio_queue:
                            print(task.file_path)
                        print('blocking get_audio_threaded')
                        self.get_files_lock.release()

        def create_thread():
            tasker = threading.Thread(target=consumer(), )
            tasker.isDaemon()
            tasker.start()
            self.thread_list.append(tasker)

        create_thread()

    def samplify(self):

        # FILTER BY SEARCH-TERMS
        for directory_entry, search_terms in self.session.query(dbs.OutputDirectories, dbs.SearchTerms).filter(
                dbs.OutputDirectories.id == dbs.SearchTerms.folder_id).all():

            logger.info('user_message', msg=f"syncing folder",
                        path=directory_entry.folder_path,
                        folder_id=directory_entry.id,
                        term_id=search_terms.id,
                        term=search_terms.name)

            # print(f"Directory Path: {directory_entry.folder_path}, "
            #       f"Folder ID: {search_terms.folder_id}, "
            #       f"Term ID: {search_terms.id}, "
            #       f"Term: {search_terms.name} "
            #       )

            for file_entry in self.session.query(dbs.Files):
                logger.info(f'admin_message', f'working file path', path=file_entry.file_path)

                # TODO: AUDIO CONVERSION
                if directory_entry.audio_only is True:

                    if file_entry.v_stream is False and file_entry.a_stream is True:

                        for audio_entry in self.session.query(dbs.FilesAudio).filter(
                                dbs.FilesAudio.file_path == file_entry.file_path):

                            pattern = re.compile(search_terms.name)
                            name_search = pattern.finditer(audio_entry.file_name)

                            for match in name_search:

                                # IS BETWEEN DATES?
                                for date_entry in self.session.query(dbs.SearchByDate).filter(
                                        dbs.SearchByDate.folder_id == directory_entry.id):
                                    logger.info('admin_message', f'Checking file_date',
                                                file_date=audio_entry.creation_date)

                                    if self.check_date(audio_entry.creation_date, date_entry.start_by_date,
                                                       date_entry.end_by_date) is True:

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
                                        output = os.path.abspath(
                                            f"{directory_entry.folder_path}/{file_name}{extension}")

                                        # OTHER
                                        normalize = directory_entry.a_normalize
                                        strip_silence = directory_entry.a_strip_silence
                                        silence_threshold = directory_entry.a_silence_threshold
                                        reduce = directory_entry.reduce

                                        # NO CHANGE; SIMPLE COPY
                                        if extension == audio_entry.extension and sample_rate == audio_entry.a_sample_rate and sample_fmt == audio_entry.a_sample_fmt and channels == audio_entry.a_channels and normalize is False and strip_silence is False:
                                            logger.info('admin_message', msg='copy file',
                                                        file_name=audio_entry.file_name,
                                                        path=directory_entry.folder_path)
                                            self.copy(audio_entry.file_path, directory_entry.folder_path)

                                        # NORMALIZATION or STRIP SILENCE (FFMPEG)
                                        elif normalize or strip_silence is True:
                                            logger.info('admin_message', msg='filters required, using FFmpeg')
                                            logger.info('admin_message', msg='file output settings',
                                                        input=input,
                                                        sample_rate=sample_rate,
                                                        sample_fmt=sample_fmt,
                                                        channels=channels,
                                                        normalize=normalize,
                                                        strip_silence=strip_silence)

                                            # TODO: convert configure_args to pass a dict instead?
                                            ff_args = av_handler.configure_args(
                                                input=input,
                                                output=output,
                                                gpu_vendor=settings.gpu_vendor,
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
                                        elif bool(self.session.query(dbs.SupportedExtensions).filter(
                                                dbs.SupportedExtensions.name == extension).first()) is True:

                                            for config in self.session.query(dbs.SupportedExtensions).filter(
                                                    dbs.SupportedExtensions.name == extension):
                                                logger.info('admin_message', msg='vanilla transcoding, using PyAV')
                                                logger.info('admin_message', msg='file output settings',
                                                            file_name=audio_entry.file_name + audio_entry.extension,
                                                            a_codec=config.a_codec,
                                                            sample_rate=config.sample_rate,
                                                            bit_depth=bit_depth,
                                                            sample_fmt=sample_fmt,
                                                            channel_layout=channels)

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
                                            logger.info('admin_message', msg='codec type not yet known, using FFmpeg')

                                            ff_args = av_handler.configure_args(
                                                input=input,
                                                output=output,
                                                gpu_vendor=settings.gpu_vendor,
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
                                            logger.info('admin_message', msg='ffmpeg args', ff_args=ff_args)

                                            # dispatch to FFmpeg
                                            stdout, stderr = av_handler.convert_ffmpeg(ff_args)

                                            # parse FFmpeg output
                                            v_format, v_codec, a_format, a_codec = av_handler.parse_ffmpeg(stdout,
                                                                                                           stderr)[1:]

                                            # insert new metadata into database
                                            self.store_codec_config(extension, v_format, v_codec, a_format, a_codec,
                                                                    sample_rate, channels)

                                break  # break search-pattern after processing

                # TODO: VIDEO CONVERSION
                elif directory_entry.video_only is True:

                    if file_entry.v_stream is True:

                        for video_entry in self.session.query(dbs.FilesVideo).filter(
                                dbs.FilesVideo.file_path == file_entry.file_path):

                            pattern = re.compile(search_terms.name)
                            name_search = pattern.finditer(video_entry.file_name)

                            for match in name_search:

                                # IS BETWEEN DATES?
                                for date_entry in self.session.query(dbs.SearchByDate).filter(
                                        dbs.SearchByDate.folder_id == directory_entry.id):
                                    logger.info(
                                        f'Event: Check file creation date {video_entry.file_path} {video_entry.creation_date}')

                                    if self.check_date(video_entry.creation_date, date_entry.start_by_date,
                                                       date_entry.end_by_date) is True:

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
                                        output = os.path.abspath(
                                            f"{directory_entry.folder_path}/{file_name}{extension}")

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
                                                                            gpu_vendor=settings.gpu_vendor,
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

                    for image_entry in self.session.query(dbs.FilesImage).filter(
                            dbs.FilesImage.file_path == file_entry.file_path):

                        pattern = re.compile(search_terms.name)
                        name_search = pattern.finditer(image_entry.file_name)

                        for match in name_search:

                            # IS BETWEEN DATES?
                            for date_entry in self.session.query(dbs.SearchByDate).filter(
                                    dbs.SearchByDate.folder_id == directory_entry.id):

                                logger.info(
                                    f'Event: Checking file date {image_entry.file_path} {image_entry.creation_date}')

                                if self.check_date(image_entry.creation_date, date_entry.start_by_date,
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

                                    if extension == image_entry.extension:
                                        print('trying Copy Method...')
                                        self.copy(input, directory_entry.folder_path)

                                    else:
                                        print('trying Pillow Method...')
                                        image_handler.convert_image(input, output, directory_entry.i_fmt)

                            break  # avoid re-iterations for multiple actions on same file

    # TODO: break this function into smaller functions, perhaps into a separate script.
    class Samplify:

        def __init__(self, NewHandler):
            self.handler = NewHandler

        def do_something(self):

            # FILTER BY SEARCH-TERMS
            for directory_entry, search_terms in self.handler.session.query(dbs.OutputDirectories, dbs.SearchTerms).filter(
                    dbs.OutputDirectories.id == dbs.SearchTerms.folder_id).all():

                logger.info('user_message', msg=f"syncing folder",
                            path=directory_entry.folder_path,
                            folder_id=directory_entry.id,
                            term_id=search_terms.id,
                            term=search_terms.name)

                # print(f"Directory Path: {directory_entry.folder_path}, "
                #       f"Folder ID: {search_terms.folder_id}, "
                #       f"Term ID: {search_terms.id}, "
                #       f"Term: {search_terms.name} "
                #       )

                for file_entry in self.session.query(dbs.Files):
                    logger.info(f'admin_message', f'working file path', path=file_entry.file_path)

                    # TODO: AUDIO CONVERSION
                    if directory_entry.audio_only is True:

                        if file_entry.v_stream is False and file_entry.a_stream is True:

                            for audio_entry in self.session.query(dbs.FilesAudio).filter(
                                    dbs.FilesAudio.file_path == file_entry.file_path):

                                pattern = re.compile(search_terms.name)
                                name_search = pattern.finditer(audio_entry.file_name)

                                for match in name_search:

                                    # IS BETWEEN DATES?
                                    for date_entry in self.session.query(dbs.SearchByDate).filter(
                                            dbs.SearchByDate.folder_id == directory_entry.id):
                                        logger.info('admin_message', f'Checking file_date',
                                                    file_date=audio_entry.creation_date)

                                        if self.check_date(audio_entry.creation_date, date_entry.start_by_date,
                                                           date_entry.end_by_date) is True:

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
                                            output = os.path.abspath(
                                                f"{directory_entry.folder_path}/{file_name}{extension}")

                                            # OTHER
                                            normalize = directory_entry.a_normalize
                                            strip_silence = directory_entry.a_strip_silence
                                            silence_threshold = directory_entry.a_silence_threshold
                                            reduce = directory_entry.reduce

                                            # NO CHANGE; SIMPLE COPY
                                            if extension == audio_entry.extension and sample_rate == audio_entry.a_sample_rate and sample_fmt == audio_entry.a_sample_fmt and channels == audio_entry.a_channels and normalize is False and strip_silence is False:
                                                logger.info('admin_message', msg='copy file',
                                                            file_name=audio_entry.file_name,
                                                            path=directory_entry.folder_path)
                                                self.copy(audio_entry.file_path, directory_entry.folder_path)

                                            # NORMALIZATION or STRIP SILENCE (FFMPEG)
                                            elif normalize or strip_silence is True:
                                                logger.info('admin_message', msg='filters required, using FFmpeg')
                                                logger.info('admin_message', msg='file output settings',
                                                            input=input,
                                                            sample_rate=sample_rate,
                                                            sample_fmt=sample_fmt,
                                                            channels=channels,
                                                            normalize=normalize,
                                                            strip_silence=strip_silence)

                                                # TODO: convert configure_args to pass a dict instead?
                                                ff_args = av_handler.configure_args(
                                                    input=input,
                                                    output=output,
                                                    gpu_vendor=settings.gpu_vendor,
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
                                            elif bool(self.session.query(dbs.SupportedExtensions).filter(
                                                    dbs.SupportedExtensions.name == extension).first()) is True:

                                                for config in self.session.query(dbs.SupportedExtensions).filter(
                                                        dbs.SupportedExtensions.name == extension):
                                                    logger.info('admin_message', msg='vanilla transcoding, using PyAV')
                                                    logger.info('admin_message', msg='file output settings',
                                                                file_name=audio_entry.file_name + audio_entry.extension,
                                                                a_codec=config.a_codec,
                                                                sample_rate=config.sample_rate,
                                                                bit_depth=bit_depth,
                                                                sample_fmt=sample_fmt,
                                                                channel_layout=channels)

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
                                                logger.info('admin_message', msg='codec type not yet known, using FFmpeg')

                                                ff_args = av_handler.configure_args(
                                                    input=input,
                                                    output=output,
                                                    gpu_vendor=settings.gpu_vendor,
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
                                                logger.info('admin_message', msg='ffmpeg args', ff_args=ff_args)

                                                # dispatch to FFmpeg
                                                stdout, stderr = av_handler.convert_ffmpeg(ff_args)

                                                # parse FFmpeg output
                                                v_format, v_codec, a_format, a_codec = av_handler.parse_ffmpeg(stdout,
                                                                                                               stderr)[1:]

                                                # insert new metadata into database
                                                self.store_codec_config(extension, v_format, v_codec, a_format, a_codec,
                                                                        sample_rate, channels)

                                    break  # break search-pattern after processing

                    # TODO: VIDEO CONVERSION
                    elif directory_entry.video_only is True:

                        if file_entry.v_stream is True:

                            for video_entry in self.session.query(dbs.FilesVideo).filter(
                                    dbs.FilesVideo.file_path == file_entry.file_path):

                                pattern = re.compile(search_terms.name)
                                name_search = pattern.finditer(video_entry.file_name)

                                for match in name_search:

                                    # IS BETWEEN DATES?
                                    for date_entry in self.session.query(dbs.SearchByDate).filter(
                                            dbs.SearchByDate.folder_id == directory_entry.id):
                                        logger.info(
                                            f'Event: Check file creation date {video_entry.file_path} {video_entry.creation_date}')

                                        if self.check_date(video_entry.creation_date, date_entry.start_by_date,
                                                           date_entry.end_by_date) is True:

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
                                            output = os.path.abspath(
                                                f"{directory_entry.folder_path}/{file_name}{extension}")

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
                                                                                gpu_vendor=settings.gpu_vendor,
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

                        for image_entry in self.session.query(dbs.FilesImage).filter(
                                dbs.FilesImage.file_path == file_entry.file_path):

                            pattern = re.compile(search_terms.name)
                            name_search = pattern.finditer(image_entry.file_name)

                            for match in name_search:

                                # IS BETWEEN DATES?
                                for date_entry in self.session.query(dbs.SearchByDate).filter(
                                        dbs.SearchByDate.folder_id == directory_entry.id):

                                    logger.info(
                                        f'Event: Checking file date {image_entry.file_path} {image_entry.creation_date}')

                                    if self.check_date(image_entry.creation_date, date_entry.start_by_date,
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

                                        if extension == image_entry.extension:
                                            print('trying Copy Method...')
                                            self.copy(input, directory_entry.folder_path)

                                        else:
                                            print('trying Pillow Method...')
                                            image_handler.convert_image(input, output, directory_entry.i_fmt)

                                break  # avoid re-iterations for multiple actions on same file

        def check_date(self, current, date_start, date_end):

            if date_start <= current <= date_end:
                return True

            else:
                return False

        def creation_date(self, path_to_file):
            """
            Try to get the date that a file was created, falling back to when it was
            last modified if that isn't possible.
            See http://stackoverflow.com/a/39501288/1709587 for explanation.
            """

            # TODO: Test this code block on other platforms (OS X/Linux)

            if platform.system() == 'Windows':
                date = datetime.fromtimestamp(os.path.getctime(path_to_file)).strftime('%Y-%m-%d')
                return date

            else:
                stat = os.stat(path_to_file)

                try:
                    return stat.st_birthtime

                except AttributeError:
                    # We're probably on Linux. No easy way to get creation dates here,
                    # so we'll settle for when its content was last modified.
                    return stat.st_mtime

        def learn_extension(self, file):
            extension = os.path.splitext(file)[1]

            process = subprocess.Popen(['ffprobe', '-i', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True)
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

                entry = bool(self.session.query(dbs.SupportedExtensions).filter(dbs.SupportedExtensions.name == extension).first())

                if not entry is True:
                    entry = dbs.SupportedExtensions(name=extension)
                    self.session.add(entry)
                    self.session.commit()

            if is_valid is False:
                print(extension, 'is unsupported!')

                entry = bool(
                    self.session.query(dbs.UnsupportedExtensions).filter(dbs.UnsupportedExtensions.name == extension).first())

                if not entry is True:
                    entry = dbs.UnsupportedExtensions(name=extension)
                    self.session.add(entry)
                    self.session.commit()

        def store_codec_config(self, extension_type, v_format, v_codec, a_format, a_codec, sample_rate, channel_size):

            print(extension_type, v_format, v_codec, a_format, a_codec)

            entry = dbs.SupportedExtensions(name=extension_type, v_format=v_format, v_codec=v_codec, a_format=a_format,
                                        a_codec=a_codec, sample_rate=sample_rate, channel_size=channel_size)

            entry_exist = bool(self.session.query(dbs.SupportedExtensions).filter(dbs.SupportedExtensions.name == extension_type,
                                                                              dbs.SupportedExtensions.v_format == v_format,
                                                                              dbs.SupportedExtensions.v_codec == v_codec,
                                                                              dbs.SupportedExtensions.a_format == a_format,
                                                                              dbs.SupportedExtensions.a_codec == a_codec,
                                                                              dbs.SupportedExtensions.sample_rate,
                                                                              dbs.SupportedExtensions.channel_size).first())

            if not entry_exist is True:
                self.session.add(entry)
                self.session.commit()

        def is_video_extension(self, extension: str):
            """
            :param extension: checks existing video table to see if exists
            :return: boolean: True or False (exists or not)
            """

            return bool(self.session.query(dbs.FilesVideo).filter(dbs.FilesVideo.extension == extension).first())

        def is_image_extension(self, extension: str):
            """
            :param extension: checks existing image table to see if exists
            :return: boolean: True or False (exists or not)
            """

            return bool(self.session.query(dbs.FilesImage).filter(dbs.FilesImage.extension == extension).first())

        def copy(self, input, output):

            _basename = os.path.basename(input)

            output = os.path.join(output, _basename)
            output = os.path.abspath(output)

            # check to see if copied already
            if not os.path.exists(output):
                logger.info(f"Event: File copied from {input} to {output}")
                shutil.copy(input, output)

            else:
                logger.info(f"Event: File already exists {output}")

    # def db_print():
    #
    #     table_meta.reflect(engine)
    #
    #     for table in table_meta.tables.values():
    #         print('Table Info: ' + f'{table}')
    #         for row in self.session.query(table):
    #             print(row)
    #
    #     self.session.close_all()

    def scan_files(self):

        logger.info('scan_files')
        time.sleep(2)

        for row in self.session.query(dbs.InputDirectories):
            path = row.folder_path
            self.decode_directory(path)

    def decode_directory(self, path):
        """

            This helper function recursively checks for files in a root directory and attempts to decode each one.
            When successful, it will insert the file metadata into a local SQLite database.

        :param path: root to directory.
        :return: void
        """

        # check if path is a valid directory
        try:
            os.chdir(path)

            if os.path.isdir(path):
                # log current working directory
                logger.info('decode_directory', msg='Scanning folder', path=path)

                if os.path.isdir(path):

                    # iterate through and decode files
                    for root, directory, files in os.walk(path):

                        for f in files:
                            # merge our strings
                            path = os.path.join(root, f)

                            # multi-threading speed test.
                            self.process_manager.add_task(self.decode_file(path))

                            ## single threaded performance test.
                            # self.decode_file(path)

        except Exception as e:
            logger.warning('admin_message', msg='Could not change the working directory. Does path exist?',
                           path=path, exc_info=f'{e}')

    def decode_file(self, path):

        try:

            # read file header
            mtype = file_handler.get_mtype(path)
            type, extension = mtype

            if type is not None:
                type = type.split('/')[0]

            # normalize any \to_path\ backslashes
            path = os.path.abspath(path)

            # remove /dirs/to/file/name.txt
            _basename = os.path.basename(path)

            # log the working file
            logger.info('user_message', msg='Working file', path=path)

            file_meta = \
                {
                    "file_path": path,
                    "file_name": os.path.splitext(_basename)[0],
                    "extension": os.path.splitext(_basename)[1],
                    "date_created": self.creation_date(path),
                    "i_stream": False,
                    "v_stream": False,
                    'a_stream': False,
                }

            if not type is None:

                if type == 'image':
                    # Decode Image (Pill)
                    img_meta = image_handler.decode_image(input=path)
                    file_meta.update(img_meta)

                    # Insert to Table
                    if file_meta['i_stream'] is True:
                        self.insert_image(file_meta)

                if type == 'audio':
                    # Decode Audio (PyAV)
                    logger.info('admin_message', msg='Dispatching to PyAV')

                    av_meta = av_handler.pyav_decode(path)
                    file_meta.update(av_meta)

                    if file_meta['v_stream'] is False and file_meta['a_stream'] is True:
                        self.insert_audio(file_meta)

                if type == 'video':
                    # Decode Video (FFprobe)
                    logger.info('admin_message', msg='Dispatching to FFprobe')

                    stdout, stderr = av_handler.ffprobe(path)
                    ffprobe_meta = av_handler.parse_ffprobe(stdout, stderr)  # returns dictionary of parsed metadata
                    file_meta.update(ffprobe_meta)

                    # Insert to Table (video)
                    if file_meta['v_stream'] is True:
                        self.insert_video(file_meta)

            # Insert to Table ('other', ie: Everything (all files) )
            self.insert_other(file_meta)

            # Write everything to database
            self.session.commit()

            # # create/clear dictionary
            # file_meta = {}
            #
            # # # merge our strings
            # # path = os.path.join(root, f)
            #
            # # normalize backslashes
            # path = os.path.abspath(path)
            #
            # # remove /paths/
            # _basename = os.path.basename(path)
            #
            # # log the working file
            # logger.info('user_message', msg='Working file', path=path)
            #
            # # create a new dict
            # file_meta['file_path'] = path
            #
            # # file_name
            # file_meta["file_name"] = os.path.splitext(_basename)[0]
            #
            # # .extension
            # file_meta["extension"] = os.path.splitext(_basename)[1]
            #
            # # creation date
            # file_meta["date_created"] = self.creation_date(path)
            #
            # # Decode Image (Pill)
            # logger.info('admin_message', msg='Dispatching to Pill')
            #
            # img_meta = image_handler.decode_image(input=path)
            # file_meta.update(img_meta)
            #
            # # Insert to Table
            # if file_meta['i_stream'] is True:
            #     self.insert_image(file_meta)
            #
            # else:
            #     # Decode Audio (PyAV)
            #     logger.info('admin_message', msg='Dispatching to PyAV')
            #
            #     av_meta = av_handler.pyav_decode(path)
            #     file_meta.update(av_meta)
            #
            #     # Decode Video (FFprobe)
            #     if file_meta['succeeded'] is False:  # check for flag
            #         logger.info('admin_message', msg='Dispatching to FFprobe')
            #
            #         stdout, stderr = av_handler.ffprobe(path)
            #         ffprobe_meta = av_handler.parse_ffprobe(stdout, stderr)  # returns dictionary of parsed metadata
            #         file_meta.update(ffprobe_meta)
            #
            #     # Insert to Table (video)
            #     if file_meta['v_stream'] is True:
            #         self.insert_video(file_meta)
            #
            #     # OR
            #
            #     # Insert to Table (audio)
            #     if file_meta['v_stream'] is False and file_meta['a_stream'] is True:
            #         self.insert_audio(file_meta)
            #
            # # Insert to Table ('other', ie: Everything (all files) )
            # self.insert_other(file_meta)
            #
            # # Write everything to database
            # self.session.commit()

        except Exception as e:
            logger.warning('admin_message', 'Could not change current working directory. Is path a file or exist?',
                           path=path, exception=e)

    def sort_to_table(self, metadata: dict):

        # VIDEO TABLE
        if metadata['v_stream'] is True:
            self.insert_video(metadata)

        # AUDIO TABLE
        elif metadata['v_stream'] is False and metadata['a_stream'] is True:
            self.insert_audio(metadata)

        # IMG TABLE
        elif metadata['v_stream'] is False and metadata['a_stream'] is False or metadata['i_stream'] is True:
            self.insert_image(metadata)

        # OTHER TABLE
        self.insert_other(metadata)

        # write to db
        self.session.commit()

    def insert_other(self, metadata):

        # add entry with basic file information
        entry = dbs.Files(
            file_path=metadata['file_path'],
            file_name=metadata['file_name'],
            extension=metadata['extension'],
            creation_date=metadata['date_created'],

            v_stream=metadata['v_stream'],
            v_width=metadata['v_width'],
            v_height=metadata['v_height'],
            v_duration=metadata['v_duration'],
            nb_frames=metadata['nb_frames'],
            v_frame_rate=metadata['v_frame_rate'],
            v_pix_format=metadata['v_pix_format'],

            a_stream=metadata['a_stream'],
            a_sample_rate=metadata['a_sample_rate'],
            a_bit_depth=metadata['a_bit_depth'],
            a_sample_fmt=metadata['a_sample_fmt'],
            a_bit_rate=metadata['a_bit_rate'],
            a_channels=metadata['a_channels'],
            a_channel_layout=metadata['a_channel_layout'],

            i_stream=metadata['i_stream'],
            i_fmt=metadata['i_fmt'],
            i_frames=metadata['i_frames'],
            i_width=metadata['i_width'],
            i_height=metadata['i_height'],
            i_alpha=metadata['i_alpha'],
            i_mode=metadata['i_mode'],
        )
        self.session.add(entry)

    def insert_image(self, metadata):

        # add entry with file image information
        entry = dbs.FilesImage(
            file_path=metadata['file_path'],
            file_name=metadata['file_name'],
            extension=metadata['extension'],
            creation_date=metadata['date_created'],
            i_stream=metadata['i_stream'],
            i_fmt=metadata['i_fmt'],
            i_width=metadata['i_width'],
            i_height=metadata['i_height'],
            i_frames=metadata['nb_frames'],
            i_alpha=metadata['alpha_channel'],
            i_mode=metadata['i_mode']
        )
        self.session.add(entry)

    def insert_audio(self, metadata):

        # add entry with file audio information
        entry = dbs.FilesAudio(
            file_path=metadata['file_path'],
            file_name=metadata['file_name'],
            extension=metadata['extension'],
            creation_date=metadata['date_created'],
            v_stream=metadata['v_stream'],
            a_stream=metadata['a_stream'],
            i_stream=metadata['i_stream'],
            a_sample_rate=metadata['a_sample_rate'],
            a_bit_depth=metadata['a_bit_depth'],
            a_sample_fmt=metadata['a_sample_fmt'],
            a_bit_rate=metadata['a_bit_rate'],
            a_channels=metadata['channels'],
            a_channel_layout=metadata['channel_layout']
        )
        self.session.add(entry)

    def insert_video(self, metadata):

        # add entry with file video information
        entry = dbs.FilesVideo(
            file_path=metadata['file_path'],
            file_name=metadata['file_name'],
            extension=metadata['extension'],
            creation_date=metadata['date_created'],
            v_stream=metadata['v_stream'],
            v_width=metadata['v_width'],
            v_height=metadata['v_height'],
            v_duration=metadata['v_duration'],
            # nb_frames=metadata['nb_frames'],
            v_frame_rate=metadata['v_frame_rate'],
            v_pix_format=metadata['v_pix_fmt'],
        )
        self.session.add(entry)

        # then check if audio exists and update entry
        # - avoids exceptions for files with video only
        if metadata['a_stream'] is True:
            self.session.query(dbs.FilesVideo). \
                filter(dbs.FilesVideo.file_path == metadata['file_path']). \
                update(
                {
                    'a_stream': metadata['a_stream'],
                    'a_sample_rate': metadata['a_sample_rate'],
                    'a_bit_depth': metadata['a_bit_depth'],
                    'a_sample_fmt': metadata['a_sample_fmt'],
                    # 'a_bit_rate': metadata['a_bit_rate'],
                    'a_channels': metadata['channels'],
                    'a_channel_layout': metadata['channel_layout']
                }
            )

    def get_root_output(self, path):

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
                entry = dbs.OutputDirectories(folder_path=path)

                # add object to self.session
                self.session.add(entry)

                # log event
                logger.info(F"Event: Folder added {path}")

                # flush buffer to get primary id
                self.session.flush()

                # if settings.default_name_searchby_directory is True:
                #
                #     # create new entry for default search terms.
                #     entry = dbs.SearchTerms(folder_id=entry.id, name=name)
                #     self.session.add(entry)

        # write everything to database
        self.session.commit()

    def monitor_mode(self):

        custom_monitoring = False

        for folder in self.session.query(dbs.InputDirectories):

            if folder.monitor is False:
                custom_monitoring = True

        if custom_monitoring is True:
            logger.info('user_message', msg="Monitor Inputs: Custom")

        else:

            if settings.monitor_all_inputs is True:
                logger.info(f'user_message', msg="Monitor Inputs: All")

            if settings.monitor_all_inputs is False:
                logger.info('user_message', msg="Monitor Inputs: None")

    def initialize_input_cache(self):

        # to avoid duplicates, completely rewrite cache each time
        settings.input_cache = []

        for folder in self.session.query(dbs.InputDirectories):

            if folder.monitor is True:

                for root, directory, files in os.walk(folder.folder_path):
                    # fix backslash extension
                    r = os.path.abspath(root)
                    # then add
                    settings.input_cache.append(r)

    def initialize_output_cache(self):

        # to avoid duplicates, completely rewrite cache each time
        settings.output_cache = []

        for folder in self.session.query(dbs.InputDirectories):

            if folder.monitor is True:

                for root, directory, files in os.walk(folder.folder_path):
                    # fix backslash issue
                    r = os.path.abspath(root)

                    # then add to list cache
                    settings.output_cache.append(r)

    def insert_input_folder(self, path):

        entry = dbs.Files(file_path=path)
        self.session.add(entry)

        self.session.commit()

    def remove_input_folder(self, path):

        pass
        # try:
        #     # filtering by the full path also allows us to also remove the children of the directory
        #     for entry in self.session.query(dbs.Files.file_path).filter(dbs.Files.file_path.like(f'%{path}%')):
        #         logger.info('admin_message', msg='File deleted', path=path)
        #
        #     # TODO:
        #     #       Query all tables for the filepath instead of just the 'dbs.Files' Table.
        #
        #     # synchronize self.session allows deletion OUTSIDE of the self.session 'cache'
        #     self.session.query(dbs.Files,
        #                        dbs.FilesImage,
        #                        dbs.FilesAudio,
        #                        dbs.FilesVideo
        #                        ) \
        #         .filter(dbs.Files.file_path.like(f'%{path}%')) \
        #         .filter(dbs.FilesImage.file_path.like(f'%{path}%')) \
        #         .filter(dbs.FilesVideo.file_path.like(f'%{path}%')) \
        #         .filter(dbs.FilesAudio.file_path.like(f'%{path}%')) \
        #         .all() \
        #         .delete(synchronize_session=False)
        #
        #     self.session.commit()
        #
        # except Exception as e:
        #     logger.error('admin_message', msg='Folder deletion failed', exc_info=e)

    def insert_output_folder(self, path):

        pass

        entry = dbs.OutputDirectories(folder_path=path)

        self.session.add(entry)

        # # Do we need to add default folder search terms?
        # if settings.default_name_searchby_directory is True:
        #
        #     # flush self.session to gain access to entry columns while in buffer
        #     self.session.flush()
        #
        #     entry = dbs.SearchTerms(folder_id=entry.id, name=os.path.basename(path))
        #
        #     self.session.add(entry)

        self.session.commit()

    def remove_output_folder(self, path):

        pass


    #     # filtering by the full path also allows us to also remove the child results from the directory
    #     for entry in self.session.query(dbs.OutputDirectories).filter(dbs.OutputDirectories.folder_path.like(f'%{path}%')):
    #         logger.info(f'Event: Folder deleted: {entry.folder_path} True')
    #
    #         self.session.query(dbs.SearchTerms).filter(entry.id == dbs.SearchTerms.folder_id).delete(synchronize_session=False)
    #
    #         self.session.query(dbs.OutputDirectories).filter(dbs.OutputDirectories.id == entry.id).delete(
    #             synchronize_session=False)
    #
    #     """
    #         Because output_cache cannot update fast enough in-between dispatched events,
    #         we need to check and delete the differences that are updated after the missed intervals
    #
    #     """
    #     for r in self.session.query(dbs.OutputDirectories).filter(dbs.OutputDirectories.folder_path):
    #         print(r.folder_path, settings.output_cache)
    #         if not r.folder_path in settings.output_cache:
    #             self.session.query(dbs.SearchTerms).filter(r.id == dbs.SearchTerms.folder_id).delete(synchronize_session=False)
    #             self.session.query(dbs.OutputDirectories).filter(r.folder_path).delete(synchronize_session=False)
    #
    #     self.session.commit()
    #
    # # deprecated
    #
    # # def insert_file(path, frame_rate, bit_depth, bit_rate):
    # #
    # #     entry = dbs.Files(file_path = f"{path}", frame_rate = f'{frame_rate}', bit_depth = f"{bit_depth}", bit_rate = f"{bit_rate}")
    # #
    # #     self.session.add(entry)
    # #
    # #     self.session.commit()

    def remove_file(self, path):

        self.session.query(dbs.Files).filter_by(file_path=path).delete()

        self.session.commit()

        # db_print()
