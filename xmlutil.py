#!/usr/bin/env python3
#
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
import util

#Element.iter(‘tag’) -Iterates over all the child elements(Sub-tree elements)
#Element.findall(‘tag’) -Finds only elements with a tag which are direct children of current element
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
    add an element in the Tree
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
    print("DEBUG: "+nvram_file)
    nvram.text = nvram_file
    nvram.tail = "\n  "
    ET.ElementTree(root).write(file)

def show_from_xml(file):
    """
    show all data from the XML file
    """
    tree = ET.parse(file)
    root = tree.getroot()

    # <name>sle15sp32</name>
    name = root.find('name').text
    print('Name: '+name)

    # <uuid>b405bd80-fa37-4c49-a335-cd7d153eaa1a</uuid>
    uuid = root.find('uuid').text
    print('uuid: ' +uuid)

    # <vcpu placement='static'>2</vcpu>
    print('vcpu attrib:' +str(root.find('vcpu').attrib))
    print('vcpu: ' +str(root.find('vcpu').text))

    # <cpu mode='host-passthrough' check='none' migratable='on'/>
    cpu = root.find('cpu')
    print('Cpu: ' +str(cpu.attrib))

    #  <os>
    #    <type arch='x86_64' machine='pc-q35-6.2'>hvm</type>
    #    <boot dev='hd'/>
    #  </os>
    osdef = root.find('os')
    for tag in osdef:
        print('os tag: '+str(tag.tag)+' value: '+str(tag.attrib)+" "+str(tag.text) if tag.text else "")

    # <memory unit='KiB'>4194304</memory>
    mem = root.find('memory')
    attr = mem.attrib
    value = root.find('memory').text
    print('Memory:' +str(attr) +" "+value)

    #   <features>
    #    <acpi/>
    #    <apic/>
    #  </features>
    features = root.find('features')
    for tag in features:
        print('features tag: '+str(tag.tag) + ' value: ' +str(tag.attrib))

    #  <clock offset='utc'>
    #    <timer name='rtc' tickpolicy='catchup'/>
    #    <timer name='pit' tickpolicy='delay'/>
    #    <timer name='hpet' present='no'/>
    #  </clock>
    clock = root.find('clock')
    print(root.find('clock').attrib)
    for timer in clock:
        print('Clock: ' +str(timer.tag) + ' value: ' +str(timer.attrib))

    #  <on_poweroff>destroy</on_poweroff>
    #  <on_reboot>restart</on_reboot>
    #  <on_crash>destroy</on_crash>
    #  <pm>
    #    <suspend-to-mem enabled='no'/>
    #    <suspend-to-disk enabled='no'/>
    #  </pm>

    #<devices>
    devices = root.find('devices')
    print(root.find('devices').attrib)
    for dev in devices:
        # <emulator>/usr/bin/qemu-system-x86_64</emulator>
        if str(dev.tag) == "emulator":
            print('Emulator: ' +str(dev.text))

        # <disk type='file' device='disk'>
        #  <driver name='qemu' type='qcow2' cache='none'/>
        #  <source file='/data/TEST/images/sle15SP3/nodes_images/sle15sp32.qcow2'/>
        #  <target dev='vda' bus='virtio'/>
        #  <address type='pci' domain='0x0000' bus='0x06' slot='0x00' function='0x0'/>
        # </disk>
        if str(dev.tag) == "disk":
            # device is a disk
            print('disk attrib: ' +str(dev.attrib))
            for disk in dev:
                print('disk: ' +str(disk.tag) + ' value: ' +str(disk.attrib))
                if disk.tag == "source":
                    filev = disk.attrib.get('file')
                    print('file value: ' +str(filev))

        # <controller type='pci' index='1' model='pcie-root-port'>
        #   <model name='pcie-root-port'/>
        #   <target chassis='1' port='0x10'/>
        #   <address type='pci' domain='0x0000' bus='0x00' slot='0x02'
        #    function='0x0' multifunction='on'/>
        # </controller>
        if str(dev.tag) == "controller":
            # device is a controller
            print('controller attrib: ' +str(dev.attrib))
            # adding an attribute to <controller>
            dev.set('ADDING', 'PLUS')
            # removing an attribute to <controller>
            dev.attrib.pop('index')
            for controller in dev:
                print('controller: ' +str(controller.tag) + ' value: ' +str(controller.attrib))
                if controller.tag == "address":
                    controller.set('BORDEL', 'JESAISPAS')
                    multifunctionv = controller.attrib.get('multifunction')
                    print('multifunction value: ' +str(multifunctionv))

            model = dev.get('model')
            print('model: ' +str(model))

        # <interface type='network'>
        #   <mac address='02:d3:b7:bb:44:b5'/>
        #   <source network='slehpcsp3'/>
        #   <model type='virtio'/>
        #   <address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
        # </interface>
        if str(dev.tag) == "interface":
            print('interface attrib: ' +str(dev.attrib))
            for interface in dev:
                print('interface: ' +str(interface.tag) + ' value: ' +str(interface.attrib))

        # <console type='pty'>
        #   <target type='virtio' port='0'/>
        # </console>
        if str(dev.tag) == "console":
            print('console attrib: ' +str(dev.attrib))
            for console in dev:
                print('console: ' +str(console.tag) + ' value: ' +str(console.attrib))

        # <channel type='unix'>
        #    <target type='virtio' name='org.qemu.guest_agent.0'/>
        #    <address type='virtio-serial' controller='0' bus='0' port='1'/>
        # </channel>
        if str(dev.tag) == "channel":
            print('channel attrib: ' +str(dev.attrib))
            for channel in dev:
                print('channel: ' +str(channel.tag) + ' value: ' +str(channel.attrib))

        # <input type='tablet' bus='usb'>
        #    <address type='usb' bus='0' port='1'/>
        # </input>
        # <input type='mouse' bus='ps2'/>
        # <input type='keyboard' bus='ps2'/>
        if str(dev.tag) == "input":
            # device is an input
            print('input attrib: ' +str(dev.attrib))
            for input in dev:
                print('input: ' +str(input.tag) + ' value: ' +str(input.attrib))

        # <graphics type='vnc' port='-1' autoport='yes' keymap='fr'>
        #   <listen type='address'/>
        # </graphics>
        if str(dev.tag) == "graphics":
            print('graphics attrib: ' +str(dev.attrib))
            for graphics in dev:
                print('graphics: ' +str(graphics.tag) + ' value: ' +str(graphics.attrib))

        # <audio id='1' type='none'/>


        # <video>
        #   <model type='virtio' heads='1' primary='yes'/>
        #   <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x0'/>
        # </video>
        if str(dev.tag) == "video":
            print('video attrib: ' +str(dev.attrib))
            for video in dev:
                print('video: ' +str(video.tag) + ' value: ' +str(video.attrib))

        # <watchdog model='i6300esb' action='poweroff'>
        #   <address type='pci' domain='0x0000' bus='0x10' slot='0x01' function='0x0'/>
        # </watchdog>
        if str(dev.tag) == "watchdog":
            print('watchdog attrib: ' +str(dev.attrib))
            for watchdog in dev:
                print('watchdog: ' +str(watchdog.tag) + ' value: ' +str(watchdog.attrib))

        # <memballoon model='virtio'>
        #   <address type='pci' domain='0x0000' bus='0x09' slot='0x00' function='0x0'/>
        # </memballoon>
        if str(dev.tag) == "memballoon":
            print('memballoon attrib: ' +str(dev.attrib))
            for memballoon in dev:
                print('memballoon: ' +str(memballoon.tag) + ' value: ' +str(memballoon.attrib))

        # <rng model='virtio'>
        #   <backend model='random'>/dev/urandom</backend>
        #   <address type='pci' domain='0x0000' bus='0x0a' slot='0x00' function='0x0'/>
        # </rng>
        #    if str(dev.tag) == "rng":
        #        print('rng attrib: ' +str(dev.attrib))
        #          for rng in dev:
        #            print('rng: ' +str(rng.tag) + ' value: ' +str(rng.attrib))

        else:
            if "/" in dev.tag == False:
                print('Unknow tag: ' +str(dev.tag) + "\n")
