# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import MetaData
from samplify.database.db_setup import *
from samplify.handlers import database_handler
import logging
import os
import time
from samplify.handlers import av_handler, image_handler, date_handler

# call our logger locally
logger = logging.getLogger('event_log')


def scan_files():

    # event log
    logger.info(f"Event: Scan Inputs")
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
                logger.info(f"Event: File scan {path} {os.path.isdir(path)}")

                # setup our I/O strings
                path = os.path.join(root, f)
                path = os.path.abspath(path)
                _basename = os.path.basename(path)

                # was moved or modified during initial scan?
                if not os.path.exists(path):
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
                        logger.info(f'Warning: {e}')

                # if ext is image, then try wand
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
                        logger.info(f'Warning: {e}')

                # Fallback backend is PyAV => FFprobe => Wand (in that order)
                # Dict keys will also be checked for Null entries to minimize decoding false positives
                # - Audio is handled fastest by PyAV
                # - Video is handled more accurately by FFprobe
                # - Image is handled best when video not dispatched to Wand
                else:
                    av_meta = av_handler.stream_info(path)
                    file_meta.update(av_meta)

                # begin our inserts into database
                if file_meta['v_stream'] is True:
                    database_handler.insert_video(file_meta)

                elif file_meta['v_stream'] is False and file_meta['a_stream'] is True:
                    database_handler.insert_audio(file_meta)

                elif file_meta['v_stream'] is False and file_meta['a_stream'] is False or file_meta['i_stream'] is True:

                    # Note: video will stall program with large temp files if incidentally decoded with wand

                    img_meta = image_handler.metadata(input=path)
                    file_meta.update(img_meta)

                    if file_meta['i_stream'] is True:
                        database_handler.insert_image(file_meta)

                database_handler.insert_file(file_meta)  # always insert file in master 'Files' table

                # write everything to database
                session.commit()
