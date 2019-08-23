from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
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

                # merge our strings
                path = os.path.join(root, f)
                path = os.path.abspath(path)  # cleans backslashes (Note: bug when nesting abspath and join-- [3.7] use seperately)
                _basename = os.path.basename(path)

                # create meta dict
                file_meta = {
                    'file_path': path,
                    'file_name': os.path.splitext(_basename)[0],
                    'extension': os.path.splitext(_basename)[1],
                    'date_created': date_handler.created(path)
                }

                # this particular file takes awhile to open -- good test file
                if path == 'D:\MOVIES & SHOWS\Tihoye.Mesto.2018.DUAL.BDRip.x264.-HELLYWOOD.mkv':
                    print()

                # av stream info
                av_meta = av_handler.stream_info(path)  # returns dict
                file_meta.update(av_meta)  # update file_meta







                # try:
                #     stdout, stderr = av_handler.ffprobe(path)
                #     parsed = av_handler.parse_ffprobe(stdout, stderr)
                #     updated = av_handler.validate_keys(parsed)
                #     file_meta.update(updated)
                #     # print(file_meta)
                #     # time.sleep(2)
                #
                # except Exception as e:
                #     logger.info(f'Warning: {e}')








                # insert into database
                if file_meta['v_stream'] is True:
                    database_handler.insert_video(file_meta)

                elif file_meta['v_stream'] is False and file_meta['a_stream'] is True:
                    database_handler.insert_audio(file_meta)

                elif file_meta['v_stream'] is False and file_meta['a_stream'] is False or file_meta['i_stream'] is True:

                    # If a video makes it to image_handler program will stall &
                    # large temp files will be created. AVOID AT ALL COSTS!

                    img_meta = image_handler.metadata(input=path)
                    file_meta.update(img_meta)

                    if file_meta['i_stream'] is True:
                        database_handler.insert_image(file_meta)

                database_handler.insert_file(file_meta)  # always insert file in FILES table

                # write everything to database
                session.commit()
