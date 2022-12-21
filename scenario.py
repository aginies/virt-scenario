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
class Immutable:
    """
    Immutable XML def
    TOFIX
    """
    def __init__(self):
        """
        init
        """
        self.console_data = {}
        self.channel_data = {}
        self.graphics_data = {}
        self.video_data = {}
        self.memballoon_data = {}
        self.rng_data = {}
        self.metadata_data = {}

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


class BasicConfiguration:
    """
    Basic configuration class
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

class ComplexConfiguration:
    """
    Complex configuration class
    """
    def __init__(self):
        """
        init
        """
        self.storage_data = None

    def storage(self, plop):
        """
        storage
        """
        print(plop)
        self.storage_data = {}
        return self.storage_data

class Features():
    """
    Features class
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
        unit = MemoryUnit("Kib", "Kib")
        self.memory = BasicConfiguration.memory(self, unit, "8192", "8192")
        return self

    def storage_perf(self):
        """
        storage performance
        """
        self.storage = ComplexConfiguration.storage(self, "plop")
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
        self.name = BasicConfiguration.name(self, "network_perf")
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
        self.name = BasicConfiguration.name(self, "access_host_fs")
        return self

class Scenario():
    """
    scenario class
    """
    def __init__(self):
        self.name = None
        self.vcpu = None 
        self.memory = None
        self.cpumode = None
        self.power = None

    def computation(self):
        """
        computation
        need cpu, memory, storage perf
        """
        self.name = BasicConfiguration.name(self, "computation")
        Features.cpu_perf(self)
        Features.memory_perf(self)
        Features.storage_perf(self)
        return self

    def testing_os(self):
        """
        testing an OS
        """
        self.name = BasicConfiguration.name(self, "access_host_fs")
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
        self.name = BasicConfiguration.name(self, "access_host_fs")
        return self

    def soft_rt_vm(self):
        """
        soft Real Time VM
        """
        self.name = BasicConfiguration.name(self, "soft_rt_vm")
        return self
