import xml.etree.ElementTree as ET

# Create the file structure.
root = ET.Element('root')

# Add a tree to the file structure.
data = ET.ElementTree(root)

# Add sub elements to the tree.
items = ET.SubElement(root, 'items')
item1 = ET.SubElement(items, 'item')
item2 = ET.SubElement(items, 'item')

# Add key/pair values to the sub elements.
item1.set('name','item1')
item2.set('name','item2')

# Add strings to sub elements.
item1.text = 'item1abc'
item2.text = 'item2abc'

# Create a new XML file and write the results to file.
myfile = open("template.xml", "w")
data.write(myfile, encoding='unicode')
myfile.close()


# PARSING XML FILES:
import os
# Find path of file.
path = os.path.dirname(__file__) + '/template.xml'
# Parse from path.
tree = ET.parse(path)
# Find root (Element from ElementTree)
template = tree.getroot()

# Iterate over SubElements from Element.
for child in template:
    # Each Element has a tag an attribute.
    print(child.tag, child.attrib)
    # We can also iterate through Sub trees
    for c in child:
        print(c.tag, c.attrib, c.text)

print()
# We can also iterate through recursively:
for child in template.iter('item'):
    print(child.tag, child.attrib, child.text)