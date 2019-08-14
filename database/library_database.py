import os
import logging
import sqlite3
import app_settings

logger = logging.getLogger('event_log')


def create_database():

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    # MAKE SURE TO DROP ALL TABLES BEFORE STARTING PROGRAM
    cur.execute('DROP TABLE IF EXISTS OutputStructure')
    cur.execute('DROP TABLE IF EXISTS Files')

    # CREATE NEW TABLES
    cur.execute('CREATE TABLE OutputStructure'
                '(path TEXT)')
    cur.execute('CREATE TABLE Files'
                '(file_name TEXT, path TEXT, sample_rate TEXT, bit_rate TEXT, format TEXT)')

    conn.commit()


def get_table_info(table):

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    try:

        for row in cur.execute(f"SELECT * FROM {table}"):
            print(row)

        for row in cur.execute(f"pragma table_info('{table}')"):
            print(row)

        for row in cur.execute(f"SELECT COUNT (*) FROM ('{table}')"):
            print(row)

    except:
        print('could not fetch table data')


def get_files(path):

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    os.chdir(path)
    for root, directory, files in os.walk(path):

        for filename in files:
            path = os.path.abspath(filename)

            cur.execute(f'INSERT INTO Files ("path") VALUES (:path)',
                        {'path': path})

            logger.info(f"Event: initial scan {path} {os.path.isdir(path)}")


    for row in cur.execute(f'SELECT * FROM Files'):
        print(row)

    conn.commit()

    get_table_info('Files')


def insert_file(path):

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()


    cur.execute(f"INSERT INTO Files ('path') VALUES (:path)",
                {'path': path})

    conn.commit()

    get_table_info('Files')


def remove_files(path):

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT * FROM Files WHERE path LIKE '%{path}%'")
        for row in cur:
            logger.info(f"Event: File deleted {row} False")

        cur.execute(f"DELETE FROM Files WHERE path LIKE '%{path}%'")

    except:
        logger.info(f"ERROR could not remove files")

    conn.commit()
    get_table_info('Files')


def get_output_directories(path):
    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    os.chdir(path)

    for root, directory, files in os.walk(path):

        for dir in directory:

            _dir_path = os.path.abspath(dir)

            cur.execute(f'INSERT INTO OutputStructure ("path") VALUES (:path)',
                        {'path': _dir_path})

            logger.info(f"Event: initial scan {_dir_path} {os.path.isdir(_dir_path)}")

    conn.commit()

    get_table_info('OutputStructure')


def insert_output_directory(path):

    # path = input('please insert directory name: ')

    if not os.path.exists(path):
        os.mkdir(path)

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    cur.execute(f"DELETE FROM OutputStructure WHERE path = '{path}'")

    cur.execute(f"INSERT INTO OutputStructure ('path') VALUES (:path)",
                {'path': path})

    conn.commit()

    get_table_info('OutputStructure')


def remove_output_directory(path):

    conn = sqlite3.connect(app_settings.database_path)
    cur = conn.cursor()

    cur.execute(f"DELETE FROM OutputStructure WHERE path LIKE '%{path}%'")
    conn.commit()

    get_table_info('OutputStructure')




# TO DO
# def insert_directory(path):
#
#     conn = sqlite3.connect(App_Settings.database_path)
#     cur = conn.cursor()
#
#     number = 1
#     for root, directory, files in os.walk(settings.input_path):
#         print(root, directory, files)
#
#         # add a new Child column for each directory
#         if root:
#             # print('indexing directory', root)
#             # print('adding new column: #', number)
#
#             cur.execute(f'ALTER TABLE Directories ADD COLUMN Child{number} TEXT')
#
#             cur.execute(f'INSERT INTO Directories (Child{number}) VALUES (:root)',
#                         {'root': root})
#
#             number = number + 1
#
#     """This is where we last left off. We need to figure out how to print off each row"""
#
#     print()
#     print(cur.execute("pragma table_info('Directories')").fetchall())
#
#     cur.execute('SELECT * FROM Directories')
#     for row in cur.fetchall():
#         print(row)
#     #
#     #
#     # for row in conn.execute("pragma table_info('Directories')").fetchall():
#     #     print(row)