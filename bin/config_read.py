from configparser import ConfigParser

parser = ConfigParser()

def read_config():
    parser.read('config.ini')

    print(parser.sections())
    print(parser.options('templates'))