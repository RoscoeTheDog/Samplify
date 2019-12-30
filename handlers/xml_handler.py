import xml.etree.ElementTree as ET
import xml.sax.saxutils as utils
import xml
import os
import structlog

logger = structlog.get_logger('samplify.log')

def create_default_template():

    # Create a root Element.
    template = ET.Element('samplify')

    # Add the root Element structure to an ElementTree (fileStructure).
    tree = ET.ElementTree(template)

    # Add sub elements to the root Element.
    name = ET.SubElement(template, 'name')
    libraries = ET.SubElement(template, 'libraries')
    outputDirectories = ET.SubElement(template, 'outputDirectories')
    searchFor = ET.SubElement(template, 'searchFor')

    name.text = 'defaultTemplate'

    # TODO: Add Input Preferences (XML)
    ET.SubElement(libraries, 'directory').set('path', 'D:/MOVIES & SHOWS')
    ET.SubElement(libraries, 'directory').set('path', 'C:/Users/Admin/Desktop/Input')
    ET.SubElement(libraries, 'directory').set('path', 'F:\Music\Music')

    # TODO: Add output preferences (XML)
    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', 'C:/Users/admin/Desktop/Output/photos')
    rules = ET.SubElement(entry, 'rules')
    ET.SubElement(rules, 'exportType').text = '.png'
    ET.SubElement(rules, 'imageFormat').text = 'PNG'
    ET.SubElement(rules, 'audioFormat').text = 'default'
    ET.SubElement(rules, 'audioSampleRate').text = 'default'
    ET.SubElement(rules, 'audioBitRate').text = ''
    ET.SubElement(rules, 'audioChannels').text = 'default'
    ET.SubElement(rules, 'audioNormalize').text = 'False'
    ET.SubElement(rules, 'imageOnly').text = 'True'

    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', 'C:/Users/admin/Desktop/Output/kick')
    rules = ET.SubElement(entry, 'rules')
    ET.SubElement(rules, 'exportType').text = 'default'
    ET.SubElement(rules, 'audioFormat').text = 'default'
    ET.SubElement(rules, 'audioSampleRate').text = 'default'
    ET.SubElement(rules, 'audioBitRate').text = ''
    ET.SubElement(rules, 'audioChannels').text = '1'
    ET.SubElement(rules, 'audioNormalize').text = 'True'
    ET.SubElement(rules, 'audioPreserve').text = 'True'

    # create new XML file and write the contents to file.
    path = os.path.dirname(__file__) + '/template.xml'
    file = open(path, "w")
    tree.write(file, encoding='unicode')
    file.close()


class Parser:

    def __init__(self):
        # Create a default template if none is specified.
        create_default_template()

        self.dict = {}
        self.path = os.path.dirname(__file__) + '/template.xml'
        self.template = ET.parse(self.path)
        self.root = self.template.getroot()

        self.libraries()
        self.output_directories()
        self.printDict()

    def from_path(self, path):
        if os.path.isfile(path):
            self.path = path
        try:
            self.template = ET.parse(self.path)
            self.root = self.template.getroot()
        except Exception as e:
            logger.error('fromPath', msg='Could not open XML file', exc_info=e)

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
                    logger.error('libraries', msg='Could not parse libraries from XML', exc_info=e)

                for rules in directory:
                    dict[rules.child] = rules.text  # Returns 'None' if no rules are found.

        # Update the dictionary.
        self.dict['libraries'] = dict

    def output_directories(self):

        dict = {}

        for parent in self.root.iter('outputDirectories'):

            for directory in parent:

                # unpack the dictionary attributes
                packed = directory.attrib
                try:
                    for k in packed.keys():
                        k = utils.unescape(packed.get(k))  # Unescape any special characters from the string.
                        dict[k] = packed.get(k)  # add key:value terms back into a modified dictionary
                except Exception as e:
                    logger.error('getOutputDirectories', msg='Could not parse outputDirectories from XML', exc_info=e)

                # add preferences to dictionary
                for rules in directory:
                    for child in rules:
                        dict[child.tag] = child.text

        # Update the dictionary
        self.dict['outputDirectories'] = dict

    def return_dict(self):
        return self.dict

    def printDict(self):
        print(self.dict)

# template_manager = Parser()