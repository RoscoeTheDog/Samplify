from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from database.database_setup import *
from handlers import database_handler
import os
import structlog

"""
    Note:
        This module is deprecated. Any output checking should be done via the database, as it should be
        already inserted into a table and considered a database task to execute.
"""

# call our logger locally
logger = structlog.get_logger('samplify.log')

# connect engine and bind engine to metadata
engine = create_engine(settings.database_path)
Base.metadata.bind = engine

# declare MetaData, so we can view it later
table_meta = MetaData()

# declare a new session maker and connect to database 'engine'
session = sessionmaker(bind=engine)

# you must also instantiate the session before querying
session = session()


def validate_directories():

    logger.info('user_message', msg=f'Validating output structure')

    for directory_entry in session.query(OutputDirectories):

        path = directory_entry.folder_path

        if not os.path.exists(path):
            logger.warning(f'admin_message', msg=f'output directory does not exist', path=path)

            try:
                os.mkdir(path)
                logger.info(f'admin_message', msg=f'new output directory created', path=path)

            except Exception as e:
                logger.error(f'admin_message', msg='path is not a valid directory location', exc_info=e)
