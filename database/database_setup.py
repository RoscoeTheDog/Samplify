import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from datetime import datetime

import app.settings

# Base for Table/class inheritance.
Base = declarative_base()

# Engine for connecting to db.
engine = create_engine(app.settings.database_path)


def drop_tables():
    # For development, just drop all table meta.
    Base.metadata.drop_all(bind=engine)


def create_tables():
    # Create all table meta-data.
    Base.metadata.create_all(engine)


# Create our session (Connection to db).
session = sqlalchemy.orm.sessionmaker(bind=engine)

session = session()

# event override for sqlite default setting where 'like' comparison operator is non-case sensitive .
@event.listens_for(Engine, "connect")
def _set_sqlite_case_insensitive_pragma(dbapi_con, connection_record):
    cursor = dbapi_con.cursor()
    cursor.execute("PRAGMA case_sensitive_like=ON;")
    cursor.close()

class OutputDirectories(Base):
    __tablename__ = 'outputDirectories'

    id = Column(Integer, primary_key=True)
    folder_path = Column(String)
    extension = Column(String)
    video_only = Column(Boolean, default=False)
    audio_only = Column(Boolean, default=False)
    image_only = Column(Boolean, default=False)
    a_sample_rate = Column(String)
    a_bit_rate = Column(String)
    a_sample_fmt = Column(String)
    a_channels = Column(String, default='default')
    a_normalize = Column(Boolean, default=False)
    a_strip_silence = Column(Boolean, default=False)
    a_silence_threshold = Column(String, default='-80')
    reduce = Column(Boolean, default=True)
    i_fmt = Column(String, default='default')


class SupportedExtensions(Base):
    __tablename__ = 'supportedExtensions'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    v_format = Column(String)
    v_codec = Column(String)
    a_format = Column(String)
    a_codec = Column(String)
    sample_rate = Column(Integer)
    channel_size = Column(Integer)
    bit_depth = Column(String)


class UnsupportedExtensions(Base):
    __tablename__ = 'unsupportedExtensions'

    id = Column(Integer, primary_key=True)
    name = Column(String)



class SearchTerms(Base):
    __tablename__ = 'searchTerms'

    id = Column(Integer, primary_key=True)
    folder_id = Column(Integer)
    name = Column(String)


class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    file_name = Column(String)
    extension = Column(String)
    creation_date = Column(String)
    v_stream = Column(Boolean, default=False)
    a_stream = Column(Boolean, default=False)
    i_stream = Column(Boolean, default=False)


class FilesVideo(Base):
    __tablename__ = 'filesVideo'

    id = Column(Integer, primary_key=True)

    file_path = Column(String)
    file_name = Column(String)
    extension = Column(String)
    creation_date = Column(String)

    v_stream = Column(Boolean, default=False)
    v_width = Column(String)
    v_height = Column(String)
    v_duration = Column(String)
    nb_frames = Column(String)
    v_frame_rate = Column(String)
    v_pix_format = Column(String)

    a_stream = Column(Boolean, default=False)
    a_sample_rate = Column(String)
    a_bit_depth = Column(String)
    a_sample_fmt = Column(String)
    a_bit_rate = Column(String)
    a_channels = Column(String)
    a_channel_layout = Column(String)

    i_stream = Column(Boolean, default=False)


class FilesAudio(Base):
    __tablename__ = 'filesAudio'

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    file_name = Column(String)
    extension = Column(String)
    creation_date = Column(String)
    v_stream = Column(Boolean, default=False)
    a_stream = Column(Boolean, default=False)
    i_stream = Column(Boolean, default=False)
    a_sample_rate = Column(String)
    a_bit_depth = Column(String)
    a_sample_fmt = Column(String)
    a_bit_rate = Column(String)
    a_channels = Column(String)
    a_channel_layout = Column(String)


class FilesImage(Base):
    __tablename__ = 'filesImage'

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    file_name = Column(String)
    extension = Column(String)
    creation_date = Column(String)
    i_stream = Column(String)
    i_fmt = Column(String)
    i_frames = Column(String)
    i_width = Column(String)
    i_height = Column(String)
    i_alpha = Column(Boolean)
    i_mode =  Column(String)

    # frame_rate = Column(Integer)
    # bit_depth = Column(String)
    # sample_fmt = Column(String)
    # bit_rate = Column(Integer)
    # channel_layout = Column(Integer)


class InputDirectories(Base):
    __tablename__ = 'inputDirectories'

    id = Column(Integer, primary_key=True)
    folder_path = Column(String)
    monitor = Column(Boolean, default=True)

class InputMonitoringExclusions(Base):
    __tablename__ = 'inputMonitoringExclusions'

    id = Column(Integer, primary_key=True)
    folder_path = Column(String)

class SearchByDate(Base):
    __tablename__ = 'searchByDate'

    id = Column(Integer, primary_key=True)
    folder_id = Column(Integer)
    start_by_date = Column(String, default=datetime.min)
    end_by_date = Column(String, default=datetime.max)


