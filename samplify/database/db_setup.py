from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from samplify.app import settings
from datetime import datetime
import os

Base = declarative_base()

# event override sqlite non-case sensitive defaults
@event.listens_for(Engine, "connect")
def _set_sqlite_case_insensitive_pragma(dbapi_con, connection_record):
    cursor = dbapi_con.cursor()
    cursor.execute("PRAGMA case_sensitive_like=ON;")
    cursor.close()


engine = create_engine(settings.database_path)


FilesOutputDirectories = Table('fileToFolder', Base.metadata,
                          Column('outputDirectories', Integer, ForeignKey('outputDirectories.id')),
                          Column('files', Integer, ForeignKey('files.id'))
                               )

class OutputDirectories(Base):
    __tablename__ = 'outputDirectories'

    # Association is to the ClassName, not the tableName
    files = relationship("Files",
                         secondary=FilesOutputDirectories)

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
    folder_id = Column(Integer, foreign_key=('outputDirectories.id'))
    name = Column(String)


class Files(Base):
    __tablename__ = 'files'

    # Association is to the ClassName, not the tableName
    outputDirectories = relationship('OutputDirectories',
                                     secondary=FilesOutputDirectories)

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

class SearchByDate(Base):
    __tablename__ = 'searchByDate'

    id = Column(Integer, primary_key=True)
    folder_id = Column(Integer, foreign_key=('outputDirectories.id'))
    start_by_date = Column(String, default=datetime.min)
    end_by_date = Column(String, default=datetime.max)


# for developer's sake, drop all table meta-data before starting
Base.metadata.drop_all(engine)

# creates all table meta-data info (columns, rows, keys, etc)
Base.metadata.create_all(engine)

# declare a new session maker and connect to database 'engine'
session = sessionmaker(bind=engine)

# you must also instantiate the session before querying
session = session()