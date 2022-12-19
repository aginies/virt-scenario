#!/usr/bin/env python3
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
Guest side
"""

import uuid
from string import Template
import proto_util as util
import template

FILES_LIST = {
    'plop',
}


def create_default_domain_xml(xmlfile):
    """
    create the VM domain XML
    """
    cmd1 = "virt-install --print-xml --virt-type kvm --arch x86_64 --machine pc-q35-6.2 "
    cmd2 = "--osinfo sles12sp5 --rng /dev/urandom --network test_net >" +xmlfile
    util.system_command(cmd1 + cmd2)

def create_from_template(finalfile):
    """
    create the VM domain XML from all template input given
    """
    print("Create Then XML VM configuration " +finalfile)
    with open(finalfile, 'w') as file_h:
        file_h.write(XML_ALL)

def create_name(name_data):
    """
    name and uuid
    """
    xml_template = template.NAME_TEMPLATE
    xml_name = {
        'VM_name': name_data['VM_name'],
        'VM_uuid': str(uuid.uuid4()),
    }
    xml = Template(xml_template).substitute(xml_name)
    return xml


def create_memory(memory_data):
    """
    memory
    """
    xml_template = template.MEMORY_TEMPLATE
    xml_mem = {
        'mem_unit': memory_data['mem_unit'],
        'max_memory': memory_data['max_memory'],
        'current_mem_unit': memory_data['current_mem_unit'],
        'memory': memory_data['memory'],
    }
    xml = Template(xml_template).substitute(xml_mem)
    return xml

def create_cpu(cpu_data):
    """
    cpu
    """
    xml_template = template.CPU_TEMPLATE
    xml_cpu = {
        'vcpu': cpu_data['vcpu'],
    }
    xml = Template(xml_template).substitute(xml_cpu)
    return xml

def create_os(os_data):
    """
    os
    """
    xml_template = template.OS_TEMPLATE
    xml_os = {
        'arch': os_data['arch'],
        'machine': os_data['machine'],
        'boot_dev': os_data['boot_dev'],
    }
    xml = Template(xml_template).substitute(xml_os)
    return xml

def create_features(features_data):
    """
    features
    """
    xml_template = template.FEATURES_TEMPLATE
    xml_features = {
        'features': features_data['features'],
    }
    xml = Template(xml_template).substitute(xml_features)
    return xml

######
# MAIN
# ####

# virt-install test
FILE = "d.xml"
create_default_domain_xml(FILE)

# filing DATA
# using template
NAME_DATA = {
    'VM_name': 'testvmname',
    }

MEMORY_DATA = {
    'mem_unit': 'Kib',
    'max_memory': '4194304',
    'current_mem_unit': 'Kib',
    'memory': '4194304',
    }

CPU_DATA = {
    'vcpu': '3',
    }

OS_DATA = {
    'arch': 'x8_64',
    'machine': 'pc-q35-6.2',
    'boot_dev': 'hd',
    }

FEATURES_DATA = {
    'features': '</acpi></apic>',
    }


# MAIN creation
XML_ALL = ""
NAME = create_name(NAME_DATA)
MEMORY = create_memory(MEMORY_DATA)
CPU = create_cpu(CPU_DATA)
OS = create_os(OS_DATA)
FEATURES = create_features(FEATURES_DATA)


XML_ALL = "<!-- WARNING: THIS IS AN GENERATED FILE -->\n"
XML_ALL += "<domain>\n"
XML_ALL += NAME+MEMORY+CPU+OS+FEATURES
XML_ALL += "</domain>\n"

create_from_template("VM.xml")
