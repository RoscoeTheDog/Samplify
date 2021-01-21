import xml.etree.ElementTree as ET
import xml.sax.saxutils as utils
from xml.dom import minidom as minidom
import app.settings
import os
import structlog
import re
import app.environment

logger = structlog.get_logger('samplify.log')


# Note: XML uses camelCase convection && we will be following that within this scope.
def create_default_template():

    # Create a root Element.
    template = ET.Element('samplify')

    # Add the root Element structure to an ElementTree (fileStructure).
    ET.ElementTree(template)

    # Add sub elements to the root Element.
    name = ET.SubElement(template, 'name')
    libraries = ET.SubElement(template, 'libraries')
    outputDirectories = ET.SubElement(template, 'outputDirectories')

    name.text = 'defaultTemplate'

    # TODO: Add Input Preferences (XML)
    # ET.SubElement(libraries, 'directory').set('path', 'D:/MOVIES & SHOWS')
    ET.SubElement(libraries, 'directory').set('path', app.environment.user_environment_input)
    # ET.SubElement(libraries, 'directory').set('path', 'F:\Music\Music')

    # images filter test
    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', app.environment.user_environment_output + '\\Images')
    rules = ET.SubElement(entry, 'rules')
    governor = ET.SubElement(entry, 'governor')
    ET.SubElement(governor, 'comparison').text = 'OR'
    ET.SubElement(rules, 'datetimeStart').text = '2020-01-01'
    ET.SubElement(rules, 'datetimeEnd').text = '2020-12-31'
    # ET.SubElement(rules, 'exportType').text = '.png'
    # ET.SubElement(rules, 'imageFormat').text = 'PNG'
    # ET.SubElement(rules, 'audioFormat').text = 'default'
    # ET.SubElement(rules, 'audioSampleRate').text = 'default'
    # ET.SubElement(rules, 'audioBitRate').text = ''
    # ET.SubElement(rules, 'audioChannels').text = 'default'
    # ET.SubElement(rules, 'audioNormalize').text = 'False'
    # ET.SubElement(rules, 'imageOnly').text = 'True'

    # audio filter test
    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', app.environment.user_environment_output + '\\kick')
    rules = ET.SubElement(entry, 'rules')
    governor = ET.SubElement(entry, 'governor')
    ET.SubElement(governor, 'comparison').text = 'AND'
    ET.SubElement(rules, 'expression').text = 'Kick'
    ET.SubElement(rules, 'extensions').text = '.wav'
    # ET.SubElement(rules, 'hasAudio').text = 'True'
    # ET.SubElement(rules, 'exportType').text = 'default'
    # ET.SubElement(rules, 'audioFormat').text = 'default'
    # ET.SubElement(rules, 'audioSampleRate').text = 'default'
    # ET.SubElement(rules, 'audioBitRate').text = ''
    # ET.SubElement(rules, 'audioChannels').text = '1'
    # ET.SubElement(rules, 'audioNormalize').text = 'True'
    # ET.SubElement(rules, 'audioPreserve').text = 'True'

    # extension filter test
    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', app.environment.user_environment_output + '\\extension test')
    rules = ET.SubElement(entry, 'rules')
    governor = ET.SubElement(entry, 'governor')
    ET.SubElement(governor, 'comparison').text = 'OR'
    ET.SubElement(rules, 'extensions').text = '.asd'
    # ET.SubElement(rules, 'exportType').text = 'default'
    # ET.SubElement(rules, 'audioFormat').text = 'default'
    # ET.SubElement(rules, 'audioSampleRate').text = 'default'
    # ET.SubElement(rules, 'audioBitRate').text = ''

    # parse our Tree root to string and enforce pretty formatting
    xmlstr = minidom.parseString(ET.tostring(template)).toprettyxml(indent="    ")

    # write to it to new xml file.
    with open(app.environment.user_environment_templates + "\\Default Template.xml", "w+") as f:
        f.write(xmlstr)
        f.close()


class NewHandler:

    def __init__(self):
        # Create a default template if none is specified.
        create_default_template()

        self.dict = {}
        self.path = app.environment.user_environment_templates + '\\Default Template.xml'
        self.template = ET.parse(self.path)
        self.root = self.template.getroot()

        self.libraries()
        self.output_tree()

    def from_path(self, path):
        if os.path.isfile(path):
            self.path = path
        try:
            self.template = ET.parse(self.path)
            self.root = self.template.getroot()
        except Exception as e:
            logger.error('user_message', msg='Could not open document. Is it an XML file?', exc_info=e)

    def libraries(self):
        dict = {}
        for parent in self.root.iter('libraries'):
            for directory in parent:
                # Unpack attrib (dict) items.
                packed = directory.attrib
                try:
                    for k in packed.keys():
                        k = utils.unescape(packed.get(k))   # Unescape any special characters from the string.
                        dict[k] = packed.get(k)     # add key:value terms back into a modified dictionary
                except Exception as e:
                    logger.error('user_message', msg='Could not read structure from XML. Is it a Samplify Template?', exc_info=e)

                for rules in directory:
                    dict[rules.child] = rules.text  # Returns 'None' if no rules are found.

        # Update the dictionary.
        self.dict['libraries'] = dict

    def output_tree(self):

        dict_list = []

        for parent in self.root.iter('outputDirectories'):

            for directory in parent:
                dir = {}

                # unpack the dictionary attributes
                packed = directory.attrib

                try:
                    for keys in packed.keys():
                        value = utils.unescape(packed.get(keys))  # Unescape any special characters from the string.
                        dir[keys] = value  # add key:value terms back into a modified dictionary
                except Exception as e:
                    logger.error('getOutputDirectories', msg='Could not parse outputDirectories from XML', exc_info=e)

                # add preferences to dictionary
                for rules in directory:
                    for child in rules:
                        dir[child.tag] = child.text

                dict_list.append(dir)

        # Update the dictionary
        self.dict['outputDirectories'] = dict_list

    def return_dict(self):
        return self.dict

    def printDict(self):
        print(self.dict)

    def compare_rule(self, file, directory, rule):
        return rule(file, directory)

    def rule_has_expression(self, file, directory):

        exp = directory.get('expression')

        if exp:
            pattern = re.compile(exp)
            search = pattern.finditer(file.file_name)

            for match in search:
                return True

        return False

    def rule_has_dates(self, file, directory):

        created_before = directory.get('createdBefore')
        created_after = directory.get('createdAfter')

        #TODO: check date-time and validate.

    def rule_has_extension(self, file, directory):

        has_extension = directory.get('hasExtension')

        for extension in has_extension.split(','):
            if file.extension.lower() in extension.lower():
                return True
        return False

    def rule_has_video(self, file, directory):

        has_video = directory.get('hasVideo')

        if has_video == 'True':
            if file.v_stream:
                return True

        return False

    def rule_has_audio(self, file, directory):

        has_audio = directory.get('hasAudio')

        if has_audio == 'True':
            if file.a_stream:
                return True

        return False

    def rule_has_image(self, file, directory):

        has_image = directory.get('hasImage')

        if has_image == 'True':
            if file.i_stream:
                return True

        return False

# class Parser:
#
#     def __init__(self):
#         # Create a default template if none is specified.
#         create_default_template()
#
#         self.dict = {}
#         self.path = os.path.dirname(__file__) + '/template.xml'
#         self.template = ET.parse(self.path)
#         self.root = self.template.getroot()
#
#         self.libraries()
#         self.output_tree()
#         self.printDict()
#
#     def from_path(self, path):
#         if os.path.isfile(path):
#             self.path = path
#         try:
#             self.template = ET.parse(self.path)
#             self.root = self.template.getroot()
#         except Exception as e:
#             logger.error('fromPath', msg='Could not open XML file', exc_info=e)
#
#     def libraries(self):
#         dict = {}
#         for parent in self.root.iter('libraries'):
#             for directory in parent:
#                 # Unpack attrib (dict) items.
#                 packed = directory.attrib
#                 try:
#                     for k in packed.keys():
#                         k = utils.unescape(packed.get(k))   # Unescape any special characters from the string.
#                         dict[k] = packed.get(k)     # add key:value terms back into a modified dictionary
#                 except Exception as e:
#                     logger.error('libraries', msg='Could not parse libraries from XML', exc_info=e)
#
#                 for rules in directory:
#                     dict[rules.child] = rules.text  # Returns 'None' if no rules are found.
#
#         # Update the dictionary.
#         self.dict['libraries'] = dict
#
#     def output_tree(self):
#
#         dict_list = []
#
#         for parent in self.root.iter('outputDirectories'):
#
#             for directory in parent:
#                 dir = {}
#
#                 # unpack the dictionary attributes
#                 packed = directory.attrib
#                 try:
#                     for keys in packed.keys():
#                         value = utils.unescape(packed.get(keys))  # Unescape any special characters from the string.
#                         dir[keys] = value  # add key:value terms back into a modified dictionary
#                 except Exception as e:
#                     logger.error('getOutputDirectories', msg='Could not parse outputDirectories from XML', exc_info=e)
#
#                 # add preferences to dictionary
#                 for rules in directory:
#                     for child in rules:
#                         dir[child.tag] = child.text
#
#                 dict_list.append(dir)
#
#         # Update the dictionary
#         self.dict['outputDirectories'] = dict_list
#
#     def return_dict(self):
#         return self.dict
#
#     def printDict(self):
#         print(self.dict)

    # def rule_is_audio(self):



# template_manager = Parser()