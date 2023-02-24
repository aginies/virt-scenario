#  -*- coding: latin-1 -*-
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
import virtscenario.util as util

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
    loader = ET.SubElement(osdef, 'loader')
    # /usr/share/qemu/ovmf-x86_64-smm-opensuse-code.bin
    loader.text = loader_file
    loader.set("readonly", "yes")
    loader.set("type", "pflash")
    loader.tail = "\n    "
    nvram = ET.SubElement(osdef, 'nvram')
    nvram.text = nvram_file
    nvram.tail = "\n  "
    ET.ElementTree(root).write(file)

def add_attestation(file, godh, session):
    """
    add attestation element in the Tree
    """
    tree = ET.parse(file)
    root = tree.getroot()
    lsdef = root.find('launchSecurity')
    # remove previous attestation
    if lsdef.find('dhCert'):
        lsdef.remove('dhCert')
    if lsdef.find('session'):
        lsdef.remove('session')
    # python >= 3.9
    #ET.indent(root, space='    ', level=0)
    dhcert = ET.SubElement(lsdef, 'dhCert')
    gtext = open(godh).read()
    dhcert.text = gtext #open(godh).read()
    dhcert.tail = "\n    "
    sessionel = ET.SubElement(lsdef, 'session')
    stext = open(session).read()
    sessionel.text = stext #open(session).read()
    sessionel.tail = "\n  "
    ET.ElementTree(root).write(file)

def show_tag(root, child):
    """
    show tag, attrib, text
    """
    util.print_title(child.upper())
    datachild = root.find(child)
    # show attrib is present
    if root.find(child).attrib:
        print(root.find(child).attrib)
    for options in datachild:
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
    util.print_data(str(dev.tag), toprint)
    # parse all sub element
    for sube in dev:
        show_attrib_text(sube)
        #print(sube.tag)
        #for key, value in sube.items():
        #    util.print_data(key, value)

def show_from_xml(file):
    """
    show all data from the XML file
    """
    # show all the XML file
    # print(ET.tostring(root, encoding='utf8').decode('utf8'))
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root:
        if child.tag not in ["devices", "pm", "os", "features", "clock"]:
            util.print_title(child.tag.upper())
            show_attrib_text(child)
        elif child.tag == "pm":
            show_tag(root, child.tag)
        elif child.tag == "os":
            show_tag(root, child.tag)
        elif child.tag == "clock":
            show_tag(root, child.tag)
        elif child.tag == "features":
            show_tag(root, child.tag)
        elif child.tag == "devices":
            devices = root.find('devices')
            for dev in devices:
                # do not show pci controller
                if dev.tag == "controller" and dev.attrib['type'] == "pci":
                    next
                else:
                    util.print_title(dev.tag.upper())
                    show_attrib_text(dev)
        else:
            if "/" in child.tag == False:
                print('Unknow tag: '+str(child.tag)+"\n")
