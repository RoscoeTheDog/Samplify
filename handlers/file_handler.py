import platform
import os
from datetime import datetime
import mimetypes
import structlog

from handlers import av_handler, image_handler

logger = structlog.getLogger('Samplify.log')


class NewHandler:

    def __init__(self, template_manager, process_manager, db_manager):
        # Required handlers for parsing/processing info.
        self.template_manager = template_manager
        self.process_manager = process_manager
        self.db_manager = db_manager
        # Active Template Dict.
        self.template = self.template_manager.return_dict()

    # Method validates the output tree. Creates required folders if not exists.
    def validate_output_directories(self):

        for keys in self.template.keys():
            if keys == 'outputDirectories':
                for directory in self.template.get('outputDirectories'):
                    path = directory.get('path')

                    try:
                        if not os.path.exists(path):
                            try:
                                os.mkdir(path)
                                logger.info('user_message', msg=f'Created new output directory {path}')
                            except Exception as e:
                                logger.error('user_message', msg='Could not create new directory in output', exc_info=e)
                    except Exception as e:
                        logger.error('user_message', msg=f'{path} is not a valid path', exc_info=e)

    # Searches input directories, determines type, and inserts to corresponding DB Tables.
    def scan_libraries(self):
        root = self.template_manager.return_dict()

        for keys in root.keys():

            if keys == 'libraries':

                for directory in root.get('libraries'):
                    path = directory

                    try:
                        os.chdir(path)
                        if os.path.isdir(path):
                            # log current working directory
                            logger.info('user_message', msg='Scanning folder', path=path)

                            if os.path.isdir(path):
                                # iterate through and decode files
                                for root, directory, files in os.walk(path):
                                    for f in files:
                                        # merge our strings
                                        path = os.path.join(root, f)

                                        # add the scan task to process_manager for parallel processing
                                        self.process_manager.add_task(self.scan_file(path))
                                        ## or run on main thread for single-thread performance.
                                        # self.decode_file(path)

                    except Exception as e:
                        logger.warning('admin_message',
                                       msg='Could not change the working directory. Does this path exist?',
                                       path=path, exc_info=f'{e}')

    # Decodes file using various modules (PILL, FFmpeg, PyAV).
    def scan_file(self, path):

        try:
            # Read file header
            type, extension = self.get_mtype(path)  # returns tuple of guessed file type and it's extension.

            # Clean string of delimiters
            if type is not None:
                type = type.split('/')[0]

            # Normalize any \to_path\ backslashes/
            path = os.path.abspath(path)

            # Isolate name from path (/dirs/to/file/name.txt -> 'name')
            _basename = os.path.basename(path)

            # log the working file for debugging
            logger.debug('admin_message', msg=f'Working file: {path}')

            # create a metadata dict to hold file info.
            file_meta = \
                {
                    "file_path": path,
                    "file_name": os.path.splitext(_basename)[0],
                    "extension": os.path.splitext(_basename)[1],
                    "date_created": self.creation_date(path),

                    'v_stream': False,
                    'v_width': '',
                    'v_height': '',
                    'v_duration': '',
                    'nb_frames': '',
                    'v_frame_rate': '',
                    'v_pix_format': '',

                    'a_stream': False,
                    'a_sample_rate': '',
                    'a_bit_depth': '',
                    'a_sample_fmt': '',
                    'a_bit_rate': '',
                    'a_channels': '',
                    'a_channel_layout': '',

                    'i_stream': False,
                    'i_fmt': '',
                    'i_frames': '',
                    'i_width': '',
                    'i_height': '',
                    'i_alpha': '',
                    'i_mode': '',
                }

            # Enforce check that type is not Null from mtypes.
            if not type is None:

                # IMAGES
                if type == 'image':
                    # Decode Image (Pill)
                    img_meta = image_handler.decode_image(input=path)
                    file_meta.update(img_meta)

                    # Insert to Table
                    if file_meta['i_stream'] is True:
                        self.db_manager.insert_image(file_meta)

                # AUDIO
                if type == 'audio':
                    # Decode Audio (PyAV)
                    logger.info('admin_message', msg='Dispatching to PyAV')

                    av_meta = av_handler.pyav_decode(path)
                    file_meta.update(av_meta)

                    # validation to check that there is no video in the encoded file.
                    if file_meta['v_stream'] is False and file_meta['a_stream'] is True:
                        self.db_manager.insert_audio(file_meta)

                # VIDEO
                if type == 'video':
                    # Decode Video (FFprobe)
                    logger.info('admin_message', msg='Dispatching to FFprobe')

                    stdout, stderr = av_handler.ffprobe(path)
                    ffprobe_meta = av_handler.parse_ffprobe(stdout, stderr)  # returns dictionary of parsed metadata
                    file_meta.update(ffprobe_meta)

                    # Insert to Table (video)
                    if file_meta['v_stream'] is True:
                        self.db_manager.insert_video(file_meta)

            # Insert all elements to 'Files' table.
            self.db_manager.insert_other(file_meta)

            # Write everything to database
            self.db_manager.session.commit()

        except Exception as e:
            logger.warning('admin_message', 'Could not change current working directory. Is path a file or exist?',
                           path=path, exception=e)

    # Fast Method that returns the type of file (audio/video/image etc).
    @staticmethod
    def get_mtype(path):
        # Validate if path is file.
        if os.path.isfile(path):
            _types = mimetypes.guess_type(path)  # Guess the file type.
            return _types  # Returns tuple (type, extension).

        else:
            logger.error("admin_message", msg="Cannot get mtype: path is not valid")

    @staticmethod
    def creation_date(path_to_file):
        """
        Try to get the date when a file was created, falling back to when it was
        last modified if that unavailable.
        http://stackoverflow.com/a/39501288/1709587 for further details.
        """

        # TODO: Test this code on other platforms (OS X/Linux)

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

    @staticmethod
    def get_parents_in_hierarchy(hierarchy):

        new_hierarchy = hierarchy.copy()

        # check position first-last
        for path_x in hierarchy:

            # compare against all other positions first-last
            for path_y in hierarchy:

                # remove any child paths
                if path_x in path_y and path_x is not path_y:
                    new_hierarchy.remove(path_y)

        return new_hierarchy
