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

import proto_util as util
import proto_guest as guest


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


def validate_xml(xmlfile):
    """
    validate the generated file
    """
    cmd = "virt-xml-validate "+xmlfile
    out, errs = util.system_command(cmd)
    if errs:
        print(errs)
    print(out)


######
# MAIN
# ####

# virt-install test
FILE = "VMa.xml"
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
    'arch': 'x86_64',
    'machine': 'pc-q35-6.2',
    'boot_dev': 'hd',
    }

FEATURES_DATA = {
    'features': '<acpi/>\n<apic/>',
    }

CPUMODE_DATA = {
    'cpu_mode': 'host-passthrough',
    'migratable': 'on',
    }

CLOCK_DATA = {
    'clock_offset': 'utc',
    'clock': '<timer name=\'rtc\' tickpolicy=\'catchup\'/>\n<timer name=\'pit\' tickpolicy=\'delay\'/>\n<timer name=\'hpet\' present=\'no\'/>',
    }

ON_DATA = {
    'on_poweroff': 'destroy',
    'on_reboot': 'restart',
    'on_crash': 'destroy',
    }

POWER_DATA = {
    'suspend_to_mem': 'no',
    'suspend_to_disk': 'no',
    }

EMULATOR_DATA = {}

DISK_DATA = {
    'disk_type': 'qcow2',
    'disk_cache': 'none',
    'source_file': '/data/TEST/images/sle15SP3/nodes_images/sle15sp34.qcow2',
    'disk_target': 'vda',
    'disk_bus': 'virtio',
    }

INTERFACE_DATA = {
    'mac_address': '02:30:81:12:ba:29',
    'network': 'slehpcsp3',
    'type': 'virtio',
    }

CONSOLE_DATA = {}

CHANNEL_DATA = {}

INPUT_DATA = {}

GRAPHICS_DATA = {}

AUDIO_DATA = {}

VIDEO_DATA = {}

WATCHDOG_DATA = {
    'model': 'i6300esb',
    'action': 'poweroff',
    }

MEMBALLOON_DATA = {}

RNG_DATA = {}

TPM_DATA = {
    'tpm_model': 'tpm-crb',
    'tpm_type': 'passthrough',
    'device_path': '/dev/tpm0',
    }

# MAIN creation
XML_ALL = ""
NAME = guest.create_name(NAME_DATA)
METADATA = guest.create_metadata(METADATA_DATA)
MEMORY = guest.create_memory(MEMORY_DATA)
CPU = guest.create_cpu(CPU_DATA)
OS = guest.create_os(OS_DATA)
FEATURES = guest.create_features(FEATURES_DATA)
CPUMODE = guest.create_cpumode(CPUMODE_DATA)
CLOCK = guest.create_clock(CLOCK_DATA)
ON = guest.create_on(ON_DATA)
POWER = guest.create_power(POWER_DATA)
EMULATOR = guest.create_emulator(EMULATOR_DATA)
DISK = guest.create_disk(DISK_DATA)
INTERFACE = guest.create_interface(INTERFACE_DATA)
CONSOLE = guest.create_console(CONSOLE_DATA)
CHANNEL = guest.create_channel(CHANNEL_DATA)
INPUT = guest.create_input(INPUT_DATA)
GRAPHICS = guest.create_graphics(GRAPHICS_DATA)
AUDIO = guest.create_audio(AUDIO_DATA)
VIDEO = guest.create_video(VIDEO_DATA)
WATCHDOG = guest.create_watchdog(WATCHDOG_DATA)
MEMBALLOON = guest.create_memballoon(MEMBALLOON_DATA)
RNG = guest.create_rng(RNG_DATA)
TPM = guest.create_tpm(TPM_DATA)


XML_ALL = "<!-- WARNING: THIS IS AN GENERATED FILE -->\n"
XML_ALL += "<domain type='kvm'>\n"
XML_ALL += NAME+METADATA+MEMORY+CPU+OS+FEATURES+CPUMODE+CLOCK+ON+POWER
XML_ALL += "<devices>\n"+EMULATOR+DISK+INTERFACE
XML_ALL += CONSOLE+CHANNEL+INPUT+GRAPHICS+AUDIO+VIDEO+WATCHDOG+MEMBALLOON+RNG+TPM
XML_ALL += "</devices>\n"
XML_ALL += "</domain>\n"

create_from_template("VMb.xml")
validate_xml("VMb.xml")
