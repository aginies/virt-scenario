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
import configuration as c
import features as f

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
        self.ondef = None
        self.watchdog = None
        self.storage = None
        self.disk = None
        self.network = None
        self.memory = None
        self.tpm = None
        self.audio = None
        self.features = None
        self.clock = None
        self.iothreads = None
        self.access_host_fs = None
        self.usb = None

    def computation(self):
        """
        computation
        need cpu, memory, storage perf
        """
        # BasicConfiguration definition
        self.name = c.BasicConfiguration.name(self, "computation")
        self.osdef = c.BasicConfiguration.osdef(self, "x86_64", "pc-q35-6.2", "hd")
        self.watchdog = c.BasicConfiguration.watchdog(self, "i6300esb", "poweroff")
        self.ondef = c.BasicConfiguration.ondef(self, "restart", "restart", "restart")
        self.features = c.BasicConfiguration.features(self, "<acpi/><apic/>")
        # Set some expected features
        f.Features.cpu_perf(self)
        f.Features.features_perf(self)
        f.Features.memory_perf(self)
        f.Features.storage_perf(self)
        f.Features.network_perf(self)
        f.Features.clock_perf(self)
        return self

    def desktop(self):
        """
        desktop
        """
        # BasicConfiguration definition
        self.name = c.BasicConfiguration.name(self, "desktop")
        self.osdef = c.BasicConfiguration.osdef(self, "x86_64", "pc-i440fx-6.2", "hd")
        self.ondef = c.BasicConfiguration.ondef(self, "destroy", "restart", "destroy")
        self.audio = c.BasicConfiguration.audio(self, "ac97")
        self.usb = c.BasicConfiguration.usb(self, "qemu-xhci")
        self.tpm = c.ComplexConfiguration.tpm(self, "tpm-crb", "passthrough", "/dev/tpm0")
        #self.access_host_fs = ComplexConfiguration.access_host_fs(self, "plop")
        # memory
        unit = f.MemoryUnit("Gib", "Gib")
        self.memory = c.BasicConfiguration.memory(self, unit, "4", "4")
        # vcpu
        self.vcpu = c.BasicConfiguration.vcpu(self, "2")

        self.cpumode = c.BasicConfiguration.cpumode(self, "host-passthrough", "on")
        self.power = c.BasicConfiguration.power(self, "yes", "yes")
        # Disk
        diskdata = f.Disk("qcow2", "none", "vda", "virtio")
        source_file = "/tmp/"+self.name['VM_name']+".qcow2"
        self.disk = c.ComplexConfiguration.disk(self, diskdata, source_file)
        self.iothreads = c.BasicConfiguration.iothreads(self, "0")
        # network
        macaddress = util.macaddress()
        self.network = c.ComplexConfiguration.network(self, macaddress, "default", "e1000", "off")

        # Set some expected features
        f.Features.features_perf(self)
        f.Features.clock_perf(self)
        return self

    def testing_os(self):
        """
        testing an OS
        """
        self.name = c.BasicConfiguration.name(self, "test")
        return self

    def easy_migration(self):
        """
        easy migration
        """
        self.name = c.BasicConfiguration.name(self, "easy_migration")
        return self

    def secure_vm(self):
        """
        secure VM
        """
        # BasicConfiguration definition
        self.name = c.BasicConfiguration.name(self, "securevm")
        self.osdef = c.BasicConfiguration.osdef(self, "x86_64", "pc-q35-6.2", "hd")
        self.ondef = c.BasicConfiguration.ondef(self, "destroy", "destroy", "destroy")
        self.tpm = c.ComplexConfiguration.tpm_emulated(self, "tpm-crb", "emulator", "2.0")
        # memory
        unit = f.MemoryUnit("Gib", "Gib")
        self.memory = c.BasicConfiguration.memory(self, unit, "4", "4")
        # vcpu
        self.vcpu = c.BasicConfiguration.vcpu(self, "2")

        self.cpumode = c.BasicConfiguration.cpumode(self, "host-passthrough", "on")
        self.power = c.BasicConfiguration.power(self, "no", "no")
        # Disk
        diskdata = f.Disk("qcow2", "none", "vda", "virtio")
        source_file = "/tmp/"+self.name['VM_name']+".qcow2"
        self.disk = c.ComplexConfiguration.disk(self, diskdata, source_file)
        self.iothreads = c.BasicConfiguration.iothreads(self, "0")
        # network
        macaddress = util.macaddress()
        self.network = c.ComplexConfiguration.network(self, macaddress, "default", "e1000", "off")

        # Set some expected features
        f.Features.features_perf(self)
        f.Features.clock_perf(self)
        f.Features.security(self)
        return self

    def soft_rt_vm(self):
        """
        soft Real Time VM
        """
        self.name = c.BasicConfiguration.name(self, "soft_rt_vm")
        return self
