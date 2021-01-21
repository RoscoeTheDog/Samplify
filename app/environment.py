import os
import database
import structlog

logger = structlog.getLogger('Samplify.log')

# TODO: Change the user_enviroment configuration to XML.

platform = 'unknown'
user_name = 'unknown'
gpu_vendor = 'unknown'

install_path = 'C:\\Program Files\\Samplify'

# TODO: When able to create an installable package, change db path to install_path
database_name = 'database.db'
database_path = 'sqlite:///' + os.path.dirname(database.__file__) + '/' + database_name

user_environment = os.environ['USERPROFILE'] + '\\Documents\\Samplify'
user_environment_templates = user_environment + '\\Templates'
user_environment_input = user_environment + '\\Input'
user_environment_output = user_environment + '\\Output'


# setup new environment if not used before
def init_environment():

    try:
        if not os.path.exists(user_environment):
            os.mkdir(user_environment)

        if not os.path.exists(user_environment_input):
            os.mkdir(user_environment_input)

        if not os.path.exists(user_environment_output):
            os.mkdir(user_environment_output)

        if not os.path.exists(user_environment_templates):
            os.mkdir(user_environment_templates)

    except Exception as e:
        logger.error('admin_message', msg='Could not create environment', exc_info=e)
