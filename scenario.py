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
Scenario definition
"""

import util

class MemoryUnit:
    """
    useful to avoid repetition of mem unit
    """
    def __init__(self, mem_unit, current_mem_unit):
        """
        init
        """
        self.mem_unit = mem_unit
        self.current_mem_unit = current_mem_unit

class Disk:
    """
    useful to avoid repetition of Disk
    """
    def __init__(self, disk_type, disk_cache, disk_target, disk_bus):
        """
        init disk
        """
        self.disk_type = disk_type
        self.disk_cache = disk_cache
        self.disk_target = disk_target
        self.disk_bus = disk_bus


class BasicConfiguration:
    """
    Basic configuration class
    This is where all configuration is set using value set by the Class Features
    the dict will be used in all templates
    """
    def __init__(self):
        """
        init
        """
        self.name_data = None
        self.vcpu_data = None
        self.audio_data = None
        self.input_data = None
        self.watchdog_data = None
        self.cpumode_data = None
        self.power_data = None
        self.emulator_data = None
        self.memory_data = None
        self.os_data = None

    def name(self, name):
        """
        define the name of the VM
        """
        self.name_data = {
            'VM_name': name,
        }
        return self.name_data

    def vcpu(self, vcpu):
        """
        define the VCPU number
        """
        self.vcpu_data = {
            'vcpu': vcpu,
        }
        return self.vcpu_data

    def cpumode(self, cpumode, migratable):
        """
        cpumode def
        """
        self.cpumode_data = {
            'cpu_mode': cpumode,
            'migratable': migratable,
        }
        return self.cpumode_data

    def power(self, suspend_to_mem, suspend_to_disk):
        """
        suspend mode
        """
        self.power_data = {
            'suspend_to_mem': suspend_to_mem,
            'suspend_to_disk': suspend_to_disk,
            }
        return self.power_data

    def audio(self, model):
        """
        define the audio model
        """
        self.audio_data = {
            'model': model,
        }
        return self.audio_data

    def input(self, inputtype, bus):
        """
        define the input
        """
        self.input_data = {
            'type': inputtype,
            'bus': bus,
        }
        return self.input_data

    def watchdog(self, model, action):
        """
        define the watchdog
        """
        self.watchdog_data = {
            'model': model,
            'action': action,
        }
        return self.watchdog_data

    def emulator(self, emulator):
        """
        emulator to use
        """
        self.emulator_data = {
            'emulator': emulator,
        }
        return self.emulator_data

    def memory(self, unit, max_memory, memory):
        """
        memory to use
        """
        self.memory_data = {
            'mem_unit': unit.mem_unit,
            'max_memory': max_memory,
            'current_mem_unit': unit.current_mem_unit,
            'memory': memory,
        }
        return self.memory_data

    def osdef(self, arch, machine, boot_dev):
        """
        os def
        """
        self.os_data = {
            'arch': arch,
            'machine': machine,
            'boot_dev': boot_dev,
        }
        return self.os_data

    def ondef(self, on_poweroff, on_reboot, on_crash):
        """
        on def
        """
        self.ondef_data = {
            'on_poweroff': on_poweroff,
            'on_reboot': on_reboot,
            'on_crash': on_crash,
        }
        return self.ondef_data

class ComplexConfiguration:
    """
    Complex configuration class
    Same as BasicConfiguration but for complex stuff
    """
    def __init__(self):
        """
        init
        """
        self.disk_data = None
        self.access_host_fs_data = None
        self.network_data = None
        self.tpm_data = None

    def disk(self, disk, source_file):
        """
        disk
        """
        self.disk_data = {
            'disk_type': disk.disk_type,
            'disk_cache': disk.disk_cache,
            'source_file': source_file,
            'disk_target': disk.disk_target,
            'disk_bus': disk.disk_bus,
        }
        return self.disk_data

    def network(self, mac, network, intertype):
        """
        network
        """
        self.network_data = {
            'mac_address': mac,
            'network': network,
            'type': intertype,
            }
        return self.network_data

    def access_host_fs(self):
        """
        access host fs configuration
        """
        self.access_host_fs_data = {}
        return self.access_host_fs_data

    def tpm(self, tpm_model, tpm_type, device_path):
        """
        TPM def
        """
        self.tpm_data = {
            'tpm_model': tpm_model,
            'tpm_type': tpm_type,
            'device_path': device_path,
        }
        return self.tpm_data

class Features():
    """
    Features class
    called by Scenario to file what's expected
    """
    def __init__(self):
        """
        init
        """
        self.name = None
        self.vcpu = None
        self.cpumode = None
        self.power = None
        self.memory = None
        self.storage = None
        self.disk = None
        self.network = None
        self.access_host_fs = None

    def cpu_perf(self):
        """
        cpu perf
        """
        self.vcpu = BasicConfiguration.vcpu(self, "6")
        self.cpumode = BasicConfiguration.cpumode(self, "host-passthrough", "off")
        self.power = BasicConfiguration.power(self, "no", "no")
        return self

    def memory_perf(self):
        """
        memory perf
        """
        unit = MemoryUnit("Mib", "Mib")
        self.memory = BasicConfiguration.memory(self, unit, "8192", "8192")
        return self

    def storage_perf(self):
        """
        storage performance
        """
        # Disk
        diskdata = Disk("raw", "none", "vda", "virtio")
        source_file = "/tmp/"+self.name['VM_name']+"raw"
        self.disk = ComplexConfiguration.disk(self, diskdata, source_file)
        return self

    def video_perf(self):
        """
        video performance
        """
        self.name = BasicConfiguration.name(self, "video_perf")
        return self

    def network_perf(self):
        """
        network performance
        """
        macaddress = util.macaddress()
        self.network = ComplexConfiguration.network(self, macaddress, "default", "virtio")
        return self

    def host_hardware(self):
        """
        host hardware
        """
        self.name = BasicConfiguration.name(self, "host_hardware")
        return self

    def access_host_fs(self):
        """
        access host filesystem
        """
        self.access_host_fs = ComplexConfiguration.access_host_fs(self)
        return self

class Scenarios():
    """
    Scenarios class
    This class is used to create all the configuration needed calling feature's class
    WARNING:
    vcpu, memory, machine can be overwritten by user setting
    """
    def __init__(self):
        self.name = None
        self.vcpu = None
        self.memory = None
        self.cpumode = None
        self.power = None
        self.osdef = None
        self.watchdog = None
        self.storage = None
        self.disk = None
        self.network = None
        self.memory = None
        self.tpm = None
        self.audio = None

    def computation(self):
        """
        computation
        need cpu, memory, storage perf
        """
        # BasicConfiguration definition
        self.name = BasicConfiguration.name(self, "computation")
        self.osdef = BasicConfiguration.osdef(self, "x86_64", "pc-q35-6.2", "hd")
        self.watchdog = BasicConfiguration.watchdog(self, "i6300esb", "poweroff")
        self.ondef = BasicConfiguration.ondef(self, "restart", "restart", "restart")
        # Set some expected features
        Features.cpu_perf(self)
        Features.memory_perf(self)
        Features.storage_perf(self)
        Features.network_perf(self)
        return self

    def desktop(self):
        """
        desktop
        """
        # BasicConfiguration definition
        self.name = BasicConfiguration.name(self, "desktop")
        self.osdef = BasicConfiguration.osdef(self, "x86_64", "pc-i440fx-6.2", "hd")
        self.ondef = BasicConfiguration.ondef(self, "destroy", "restart", "destroy")
        self.audio = BasicConfiguration.audio(self, "ac97")
        self.tpm = ComplexConfiguration.tpm(self, "tpm-crb", "passthrough", "/dev/tpm0")
        # memory
        unit = MemoryUnit("Gib", "Gib")
        self.memory = BasicConfiguration.memory(self, unit, "4", "4")
        # vcpu
        self.vcpu = BasicConfiguration.vcpu(self, "2")

        self.cpumode = BasicConfiguration.cpumode(self, "host-passthrough", "on")
        self.power = BasicConfiguration.power(self, "yes", "yes")
        # Disk
        diskdata = Disk("qcow2", "none", "vda", "virtio")
        source_file = "/tmp/"+self.name['VM_name']+".qcow2"
        self.disk = ComplexConfiguration.disk(self, diskdata, source_file)
        # network
        macaddress = util.macaddress()
        self.network = ComplexConfiguration.network(self, macaddress, "default", "e1000")

        # Set some expected features
        Features.access_host_fs(self)
        return self

    def testing_os(self):
        """
        testing an OS
        """
        self.name = BasicConfiguration.name(self, "test")
        return self

    def easy_migration(self):
        """
        easy migration
        """
        self.name = BasicConfiguration.name(self, "easy_migration")
        return self

    def secure_vm(self):
        """
        secure VM
        """
        self.name = BasicConfiguration.name(self, "securevm")
        return self

    def soft_rt_vm(self):
        """
        soft Real Time VM
        """
        self.name = BasicConfiguration.name(self, "soft_rt_vm")
        return self
