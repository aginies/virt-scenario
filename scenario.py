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


class BasicDefinition:
    """
    Basic definition class
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

class Scenario:
    """
    scenario class
    """
    def __init__(self):
        self.name = None
        self.vcpu = None
        self.cpumode = None
        self.power = None


    def cpu_perf(self):
        """
        cpu perf
        """
        self.name = BasicDefinition.name(self, "Cpu_perf")
        self.vcpu = BasicDefinition.vcpu(self, "6")
        self.cpumode = BasicDefinition.cpumode(self, "host-passthrough", "off")
        self.power = BasicDefinition.power(self, "no", "no")
        return self

    def storage_perf():
        """
        storage performance
        """

    def video_perf():
        """
        video performance
        """

    def network_perf():
        """
        network performance
        """

    def host_hardware():
        """
        host hardware
        """

    def easy_migration():
        """
        easy migration
        """

    def computation():
        """
        computation
        """

    def access_host_fs():
        """
        access host filesystem
        """

    def testing_os():
        """
        testing an OS
        """

    def secure_vm():
        """
        secure VM
        """

    def soft_rt_vm():
        """
        soft Real Time VM
        """
