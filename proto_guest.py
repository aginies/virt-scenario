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
Guest side definition
"""

import uuid
from string import Template
import proto_util as util
import template


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

def create_metadata(metadata_data):
    """
    name and uuid
    """
    xml_template = template.METADATA_TEMPLATE
    #xml_metadata = { }
    #xml = Template(xml_template).substitute(xml_metadata)
    return xml_template

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

def create_cpumode(cpumode_data):
    """
    features
    """
    xml_template = template.CPUMODE_TEMPLATE
    xml_cpumode = {
        'cpu_mode': cpumode_data['cpu_mode'],
        'migratable': cpumode_data['migratable'],
    }
    xml = Template(xml_template).substitute(xml_cpumode)
    return xml

def create_clock(clock_data):
    """
    clock
    """
    xml_template = template.CLOCK_TEMPLATE
    xml_clock = {
        'clock_offset': clock_data['clock_offset'],
        'clock': clock_data['clock'],
    }
    xml = Template(xml_template).substitute(xml_clock)
    return xml

def create_on(on_data):
    """
    on power etc...
    """
    xml_template = template.ON_TEMPLATE
    xml_on = {
        'on_poweroff': on_data['on_poweroff'],
        'on_reboot': on_data['on_reboot'],
        'on_crash': on_data['on_crash'],
    }
    xml = Template(xml_template).substitute(xml_on)
    return xml

def create_power(power_data):
    """
    power
    """
    xml_template = template.POWER_TEMPLATE
    xml_power = {
        'suspend_to_mem': power_data['suspend_to_mem'],
        'suspend_to_disk': power_data['suspend_to_disk'],
    }
    xml = Template(xml_template).substitute(xml_power)
    return xml

def create_emulator(power_data):
    """
    power
    """
    xml_template = template.EMULATOR_TEMPLATE
    #xml_emulator = { }
    #xml = Template(xml_template).substitute(xml_emulator)
    return xml_template


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

METADATA_DATA = {}

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

CPUMODE_DATA = {
    'cpu_mode': '',
    'migratable': 'on',
    }

CLOCK_DATA = {
    'clock_offset': '',
    'clock': '',
    }

ON_DATA = {
    'on_poweroff': '',
    'on_reboot': '',
    'on_crash': '',
    }

POWER_DATA = {
    'suspend_to_mem': '',
    'suspend_to_disk': '',
    }

EMULATOR_DATA = {}


# MAIN creation
XML_ALL = ""
NAME = create_name(NAME_DATA)
METADATA = create_metadata(METADATA_DATA)
MEMORY = create_memory(MEMORY_DATA)
CPU = create_cpu(CPU_DATA)
OS = create_os(OS_DATA)
FEATURES = create_features(FEATURES_DATA)
CPUMODE = create_cpumode(CPUMODE_DATA)
CLOCK = create_clock(CLOCK_DATA)
ON = create_on(ON_DATA)
POWER = create_power(POWER_DATA)
EMULATOR = create_emulator(EMULATOR_DATA)

XML_ALL = "<!-- WARNING: THIS IS AN GENERATED FILE -->\n"
XML_ALL += "<domain>\n"
XML_ALL += NAME+METADATA+MEMORY+CPU+OS+FEATURES+CPUMODE+CLOCK+ON+POWER+EMULATOR
XML_ALL += "</domain>\n"

create_from_template("VM.xml")
