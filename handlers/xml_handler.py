import xml.etree.ElementTree as ET
import xml.sax.saxutils as utils
import os
import structlog

logger = structlog.get_logger('samplify.log')

def doStuff():

    # Create a root Element.
    template = ET.Element('template')

    # Add the root Element structure to an ElementTree (fileStructure).
    tree = ET.ElementTree(template)

    # Add sub elements to the root Element.
    inputDirectories = ET.SubElement(template, 'inputDirectories')
    outputDirectories = ET.SubElement(template, 'outputDirectories')
    searchFor = ET.SubElement(template, 'searchFor')

    # TODO: Add Input Preferences (XML)
    ET.SubElement(inputDirectories, 'directory').set('path', 'D:/MOVIES & SHOWS')
    ET.SubElement(inputDirectories, 'directory').set('path', 'C:/Users/Admin/Desktop/Input')

    # TODO: Add output preferences (XML)
    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', 'C:/Users/admin/Desktop/Output/photos')
    properties = ET.SubElement(entry, 'properties')
    ET.SubElement(properties, 'exportType').text = '.png'
    ET.SubElement(properties, 'imageFormat').text = 'PNG'
    ET.SubElement(properties, 'audioFormat').text = 'default'
    ET.SubElement(properties, 'audioSampleRate').text = 'default'
    ET.SubElement(properties, 'audioBitRate').text = ''
    ET.SubElement(properties, 'audioChannels').text = 'default'
    ET.SubElement(properties, 'audioNormalize').text = 'False'
    ET.SubElement(properties, 'imageOnly').text = 'True'

    entry = ET.SubElement(outputDirectories, 'directory')
    entry.set('path', 'C:/Users/admin/Desktop/Output/kick')
    properties = ET.SubElement(entry, 'properties')
    ET.SubElement(properties, 'exportType').text = 'default'
    ET.SubElement(properties, 'audioFormat').text = 'default'
    ET.SubElement(properties, 'audioSampleRate').text = 'default'
    ET.SubElement(properties, 'audioBitRate').text = ''
    ET.SubElement(properties, 'audioChannels').text = '1'
    ET.SubElement(properties, 'audioNormalize').text = 'True'
    ET.SubElement(properties, 'audioPreserve').text = 'True'

    # create new XML file and write the contents to file.
    path = os.path.dirname(__file__) + '/template.xml'
    file = open(path, "w")
    tree.write(file, encoding='unicode')
    file.close()


class ParseTemplate:

    def __init__(self):
        self.dict = {}
        self.path = os.path.dirname(__file__) + '/template.xml'
        self.template = ET.parse(self.path)
        self.root = self.template.getroot()

    def from_path(self, path):

        if os.path.isfile(path):
            self.path = path

        try:
            self.template = ET.parse(self.path)
            self.root = self.template.getroot()
        except Exception as e:
            logger.error('fromPath', msg='Could not open XML file', exc_info=e)

    def input_directories(self):

        dict = {}

        for parent in self.root.iter('inputDirectories'):

            for directory in parent:
                # attributes = ET.tostring(directory, encoding='UTF-8')
                # directory = utils.unescape(attributes, "&lt; &amp; &gt;")

                # unpack dictionary
                packed = directory.attrib
                try:
                    for k in packed.keys():
                        # attributes = ET.tostring(directory, encoding='UTF-8')
                        # directory = utils.unescape(attributes, "&lt; &amp; &gt;")

                        # add it to modified dictionary
                        dict[k] = packed.get(k)
                except Exception as e:
                    logger.error('getInputDirectories', msg='Could not parse InputDirectories from XML', exc_info=e)

                # if any Input Directories are found, add them to the modified dictionary too.
                for properties in directory:
                    dict[properties.child] = properties.text

        self.dict['inputDirectories'] = dict

    def output_directories(self):

        dict = {}

        for parent in self.root.iter('outputDirectories'):

            for directory in parent:

                # unpack the dictionary attributes
                packed = directory.attrib
                try:
                    for k in packed.keys():
                        # add it to modified dictionary
                        dict[k] = packed.get(k)
                except Exception as e:
                    logger.error('getOutputDirectories', msg='Could not parse outputDirectories from XML', exc_info=e)

                # add preferences to dictionary
                for properties in directory:
                    for child in properties:
                        dict[child.tag] = child.text

        self.dict['outputDirectories'] = dict

    def return_dict(self):
        return self.dict

    def printDict(self):
        print(self.dict)

doStuff()
handler = ParseTemplate()
handler.input_directories()
handler.output_directories()
handler.printDict()

