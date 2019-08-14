from configparser import ConfigParser
import bin

# SETUP
config = ConfigParser()

template_new = bin.config_setup.template_write()
print(template_new)

def write_config():

    config['root_select'] = {
        'input_root': 'C:/Users/Admin/Desktop/Input',
        'output_root': 'C:/Users/Admin/Desktop/Output',
    }

    config['folders_master_list'] = {
        'parent1': 'child1'
    }

    config['thread_settings'] = {
        'num_threads': '4',
    }

    config['templates'] = {
        template_new
    }

    with open('./config.ini', 'w') as config_file:
        config.write(config_file)

read_config()