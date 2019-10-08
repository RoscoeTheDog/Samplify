# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import MetaData
from database.db_setup import *
from handlers import database_handler
# import logging
import os
import time
from handlers import av_handler, image_handler, date_handler
import structlog


# call our logger locally
logger = structlog.get_logger('samplify.log')


def scan_files():

    # event log
    logger.info(f'user_message ', msg=f'Manual input scan started')
    num_files, _ = total_file_count()
    num_scanned = 0
    time.sleep(2)

    for row in session.query(InputDirectories):
        # local vars
        path = row.folder_path

        try:
            logger.info(f'admin_message', msg=f'Changing working directory')
            os.chdir(path)
        except Exception as e:
            logger.error(f'admin_message', msg=f'Directory does not exist!', exc_info=e)
            continue

        # event log
        logger.info(f'user_message', msg=f'Collecting file metadata from libraries')

        for root, directory, files in os.walk(path):

            for f in files:
                logger.info(f'user_message', msg=f'Number of files scanned: {num_scanned}/{num_files}')
                logger.info(f'admin_message', msg=f'probing file from path', path=path)

                # setup our I/O strings
                path = os.path.join(root, f)
                path = os.path.abspath(path)
                _basename = os.path.basename(path)

                # was moved or modified during initial scan?
                if not os.path.exists(path):
                    logger.warning(f'admin_message', msg=f'Path does not exist', path=path)
                    continue

                # create dict for file metadata
                file_meta = {
                    'file_path': path,
                    'file_name': os.path.splitext(_basename)[0],
                    'extension': os.path.splitext(_basename)[1],
                    'date_created': date_handler.created(path),
                    'v_stream': False,
                    'a_stream': False,
                }

                # perform a file extension query to see if we already know how to handle the file
                is_video = database_handler.is_video_extension(file_meta['extension'])  # check if container is video
                is_image = database_handler.is_image_extension(file_meta['extension'])  # check if container is image

                # if ext is video, then try ffprobe
                if is_video:
                    try:
                        stdout, stderr = av_handler.ffprobe(path)
                        parsed = av_handler.parse_ffprobe(stdout, stderr)
                        updated = av_handler.validate_keys(parsed)
                        file_meta.update(updated)

                    except Exception as e:
                        logger.error(f'admin_message', msg='Error: Could not probe video type file', exc_info=e)

                # if ext is image, then use PIL library
                elif is_image:
                    try:
                        img_meta = image_handler.metadata(input=path)
                        file_meta.update(img_meta)

                        # insert to table(s)
                        if file_meta['i_stream'] is True:
                            database_handler.insert_image(file_meta)
                            database_handler.insert_file(file_meta)
                            continue

                    except Exception as e:
                        logger.error(f'admin_message',
                                     msg='Error: Could not probe image type file',
                                     exception=e)


                # If all else fails, fallback is PyAV => FFprobe => PIL (in that order)
                # Dict keys will also be checked for Null entries to minimize decoding false positives
                # - Audio is handled fastest by PyAV
                # - Video is handled more accurately by FFprobe
                # - Image is handled fastest by PIL
                else:
                    av_meta = av_handler.stream_info(path)
                    file_meta.update(av_meta)

                # begin our inserts into database
                if file_meta['v_stream'] is True:
                    database_handler.insert_video(file_meta)

                elif file_meta['v_stream'] is False and file_meta['a_stream'] is True:
                    database_handler.insert_audio(file_meta)

                elif file_meta['v_stream'] is False and file_meta['a_stream'] is False or file_meta['i_stream'] is True:

                    img_meta = image_handler.metadata(input=path)
                    file_meta.update(img_meta)

                    if file_meta['i_stream'] is True:
                        database_handler.insert_image(file_meta)

                else:
                    # **always** insert entries into 'Files' table
                    database_handler.insert_file(file_meta)

                num_scanned += 1

                # write everything to database
                session.commit()

    logger.info('user_message', msg='scan complete!')


def total_file_count():
    """
    returns total number of files from the input library.

    :return: file_count:: int:: "Quantity of all files from the given library directories.
    :return: library_size:: int:: "Total size of directory (in bytes)"
    """

    logger.info(f'admin_message', msg=f'Counting files from all libraries')

    file_count = 0
    library_size = 0
    for row in session.query(InputDirectories):
        path = row.folder_path

        try:
            os.chdir(path)
        except Exception as e:
            logger.error(f'admin_message', msg=f'Directory does not exist!', exception=e)
            continue

        for root, directory, files in os.walk(path):

            for f in files:
                path = os.path.join(root, f)
                file_count += 1

                if not os.path.islink(path):
                    library_size += os.path.getsize(path)

    logger.info(f'user_message', msg=f'Total quantity of files: {file_count}')
    logger.info(f'user_message', msg=f'Total size from all libraries: {library_size} bytes')

    return file_count, library_size
