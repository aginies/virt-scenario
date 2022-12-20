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

import util
import proto_guest as guest
import scenario as s


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
#FILE = "VMa.xml"
#create_default_domain_xml(FILE)

# filing DATA
# using template
MEMORY_DATA = {
    'mem_unit': 'Kib',
    'max_memory': '4194304',
    'current_mem_unit': 'Kib',
    'memory': '4194304',
    }

OS_DATA = {
    'arch': 'x86_64',
    'machine': 'pc-q35-6.2',
    'boot_dev': 'hd',
    }

FEATURES_DATA = {
    'features': '<acpi/>\n    <apic/>',
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

TPM_DATA = {
    'tpm_model': 'tpm-crb',
    'tpm_type': 'passthrough',
    'device_path': '/dev/tpm0',
    }

# MAIN creation
DATA = s.BasicDefinition()
# other possible way to fill value...
#NAME = guest.create_name(DATA.name("cpu_perf"))

# There is some Immutable dict for the moment...
IMMUT = s.Immutable()
CONSOLE = guest.create_console(IMMUT.console_data)
CHANNEL = guest.create_channel(IMMUT.channel_data)
GRAPHICS = guest.create_graphics(IMMUT.graphics_data)
VIDEO = guest.create_video(IMMUT.video_data)
MEMBALLOON = guest.create_memballoon(IMMUT.memballoon_data)
RNG = guest.create_rng(IMMUT.rng_data)
METADATA = guest.create_metadata(IMMUT.metadata_data)

# CPU PERF SCENARIO
DO = s.Scenario()
CPU_PERF = DO.cpu_perf()
NAME = guest.create_name(CPU_PERF.name)
VCPU = guest.create_cpu(CPU_PERF.vcpu)
CPUMODE = guest.create_cpumode(CPU_PERF.cpumode)
POWER = guest.create_power(CPU_PERF.power)

MEMORY = guest.create_memory(MEMORY_DATA)
OS = guest.create_os(OS_DATA)
FEATURES = guest.create_features(FEATURES_DATA)
CLOCK = guest.create_clock(CLOCK_DATA)
ON = guest.create_on(ON_DATA)
EMULATOR = guest.create_emulator(DATA.emulator("/usr/bin/qemu-system-x86_64"))
DISK = guest.create_disk(DISK_DATA)
INTERFACE = guest.create_interface(INTERFACE_DATA)
INPUT = guest.create_input(DATA.input("keyboard", "virtio"))
INPUT2 = guest.create_input(DATA.input("mouse", "virtio"))
AUDIO = guest.create_audio(DATA.audio("ac97"))
WATCHDOG = guest.create_watchdog(DATA.watchdog("i6300esb", "poweroff"))
TPM = guest.create_tpm(TPM_DATA)


XML_ALL = "<!-- WARNING: THIS IS A GENERATED FILE FROM VIRT-SCENARIO -->\n"
# start the domain definition
XML_ALL += "<domain type='kvm'>\n"
XML_ALL += NAME+METADATA+MEMORY+VCPU+OS+FEATURES+CPUMODE+CLOCK+ON+POWER
# all below must be in devices section
XML_ALL += "<devices>\n"
XML_ALL += EMULATOR+DISK+INTERFACE+CONSOLE+CHANNEL+INPUT+INPUT2
XML_ALL += GRAPHICS+AUDIO+VIDEO+WATCHDOG+MEMBALLOON+RNG+TPM
# close the device section
XML_ALL += "</devices>\n"
# close domain section
XML_ALL += "</domain>\n"

create_from_template("VMb.xml")
validate_xml("VMb.xml")
