from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from samplify.database.db_setup import *
from samplify.handlers import database_handler
import logging
import os

# connect engine and bind engine to metadata
engine = create_engine(settings.database_path)
Base.metadata.bind = engine

# declare MetaData, so we can view it later
table_meta = MetaData()

# declare a new session maker and connect to database 'engine'
session = sessionmaker(bind=engine)

# you must also instantiate the session before querying
session = session()

# call our logger locally
logger = logging.getLogger('event_log')


def create_directories():

    for directory_entry in session.query(OutputDirectories):
        path = directory_entry.folder_path

        if not os.path.exists(path):
            logger.info(f'Event: {path} does not exist! Creating new directory...')

            try:
                os.mkdir(path)

            except:
                logger.info(f'{path} NOT A VALID DIRECTORY STRING')