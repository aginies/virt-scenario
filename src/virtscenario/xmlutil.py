# Authors: Antoine Ginies <aginies@suse.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
parse VM xml file
"""

import xml.etree.ElementTree as ET
import virtscenario.util

#Element.iter(‘tag’) -Iterates over all the child elements(Sub-tree elements)
#Element.findall(‘tag’) -Finds only elements with a tag which are direct children of
# current element
#Element.find(‘tag’) -Finds the first Child with the particular tag.
#Element.get(‘tag’) -Accesses the elements attributes.
#Element.text -Gives the text of the element.
#Element.attrib-returns all the attributes present.
#Element.tag-returns the element name.
# Modify
#Element.set(‘attrname’, ‘value’) – Modifying element attributes.
#Element.SubElement(parent, new_childtag) -creates a new child tag under the parent.
#Element.write(‘filename.xml’)-creates the tree of xml into another file.
#Element.pop() -delete a particular attribute.
#Element.remove() -to delete a complete tag.

def add_loader_nvram(file, loader_file, nvram_file):
    """
    add loader and nvram element in the Tree
    """
    tree = ET.parse(file)
    root = tree.getroot()

    osdef = root.find('os')

    # python >= 3.9
    #ET.indent(root, space='    ', level=0)
    # Create a new 'loader' element and set its properties
    loader = ET.SubElement(osdef, 'loader')
    # /usr/share/qemu/ovmf-x86_64-smm-opensuse-code.bin
    loader.text = loader_file
    loader.set("readonly", "yes")
    loader.set("type", "pflash")
    loader.tail = "\n    "
    # Create a new 'nvram' element and set its properties
    nvram = ET.SubElement(osdef, 'nvram')
    nvram.text = nvram_file
    nvram.tail = "\n  "
    # Write the modified XML tree back to the file
    ET.ElementTree(root).write(file)

def add_encryption(file, uuid):
    """
    add encryption data to disk
    """
    tree = ET.parse(file)
    root = tree.getroot()
    disk_elem = root.find('./devices/disk')

    if disk_elem is not None:
        source_elem = disk_elem.find("source")
        if source_elem is not None:
            source_elem.tail = "\n   "
            encryption_elem = ET.SubElement(source_elem, 'encryption')
            encryption_elem.set('format', 'luks')
            encryption_elem.tail = "\n     "
            secret_elem = ET.SubElement(encryption_elem, 'secret')
            secret_elem.set('type', 'passphrase')
            secret_elem.set('uuid', uuid)
            #element_string = ET.tostring(disk_elem, encoding='unicode')
            #print(element_string)

        tree.write(file, encoding='UTF-8', xml_declaration=True)

def add_attestation(file_path: str, dh_cert_path: str, session_path: str) -> None:
    """
    add attestation element in the Tree
    """
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Find the launchSecurity section
    ls_def = root.find('launchSecurity')
    # Remove previous attestation elements
    for attestation in ['dhCert', 'session']:
        element = ls_def.find(attestation)
        if element is not None:
            ls_def.remove(element)
    # Add new attestation elements
    dh_cert = ET.SubElement(ls_def, 'dhCert')
    with open(dh_cert_path, 'r') as fil:
        dh_cert.text = fil.read().strip()
    session = ET.SubElement(ls_def, 'session')
    with open(session_path, 'r') as fil:
        session.text = fil.read().strip()

    # Write the modified XML tree back to the file
    tree.write(file_path, encoding='UTF-8', xml_declaration=True)

def change_network_source(file_path: str, source_network: str) -> None:
    """
    Change virtual network name in the Tree
    """
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Find the 'interface' element within the 'devices' element
    interface_elem = root.find("./devices/interface")

    if interface_elem is not None:
        # Find the 'source' element within the 'interface' element
        source_elem = interface_elem.find("source")
        if source_elem is not None and 'network' in source_elem.attrib:
            # Set the value of the 'network' attribute to a new value
            source_elem.set("network", source_network)
        else:
            print("Lost in SPACE?")

    # Write the modified XML tree back to the file
    tree.write(file_path, encoding='UTF-8', xml_declaration=True)

def show_tag(root: ET.Element, child: str) -> None:
    """
    Print the tag, attributes, and text of a child element of the root element.
    """
    virtscenario.util.print_title(child.upper())
    data_child = root.find(child)
    if data_child is None:
        raise ValueError(f"Child element '{child}' not found in root element.")
    # show attrib is present
    if root.find(child).attrib:
        print(root.find(child).attrib)
    for options in data_child:
        show_attrib_text(options)

def show_attrib_text(dev):
    """
    show attrib and text
    """
    toprint = ""
    if dev.attrib != {}:
        toprint = str(dev.attrib)
    if dev.text != None:
        toprint += " "+str(dev.text)
    virtscenario.util.print_data(str(dev.tag), toprint)
    # parse all sub element
    for sube in dev:
        if sube.tag == "session" or sube.tag == "dhCert":
            virtscenario.util.print_data(str(sube.tag), "Confidential Data")
        else:
            show_attrib_text(sube)
        #for key, value in sube.items():
        #    util.print_data(key, value)

def show_from_xml(file):
    """
    show all data from the XML file
    """
    # show all the XML file
    # print(ET.tostring(root, encoding='utf8').decode('utf8'))
    try:
        # Parse the XML file
        tree = ET.parse(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file}' not found.")
    # Get the root element
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root:
        if child.tag not in ["devices", "pm", "os", "features", "clock"]:
            virtscenario.util.print_title(child.tag.upper())
            show_attrib_text(child)
        elif child.tag in ["pm", "os", "features", "clock"]:
            show_tag(root, child.tag)
        elif child.tag == "devices":
            devices = root.find('devices')
            for dev in devices:
                # do not show pci controller
                if dev.tag == "controller" and dev.attrib.get('type') == "pci":
                    continue
                else:
                    virtscenario.util.print_title(dev.tag.upper())
                    show_attrib_text(dev)
        else:
            # Show regular elements
            print(child.tag.upper())
            show_attrib_text(child)
