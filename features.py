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
Features
"""

import util
import configuration as c

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
        self.features = None
        self.clock = None
        self.video = None
        self.access_host_fs = None
        self.iothreads = None
        self.security = None

    def cpu_perf(self):
        """
        cpu perf
        """
        self.vcpu = c.BasicConfiguration.vcpu(self, "6")
        self.cpumode = c.BasicConfiguration.cpumode_pass(self, "off", "")
        self.power = c.BasicConfiguration.power(self, "no", "no")
        return self

    def features_perf(self):
        """
        features perf
        """
        datafeatures = "<acpi/>\n    <apic/>\n    <pae/>"
        self.features = c.BasicConfiguration.features(self, datafeatures)
        return self

    def security(self):
        """
        security
        """
        secdata = "<cbitpos>47</cbitpos>\n"
        secdata += "    <reducedPhysBits>1</reducedPhysBits>\n"
        secdata += "    <policy>0x0033</policy>"
        self.security = c.BasicConfiguration.security(self, "sev", secdata)
        return self

    def memory_perf(self):
        """
        memory perf
        """
        unit = MemoryUnit("Mib", "Mib")
        self.memory = c.BasicConfiguration.memory(self, unit, "8192", "8192")
        return self

    def storage_perf(self):
        """
        storage performance
        """
        # Disk
        diskdata = Disk("raw", "none", "vda", "virtio")
        source_file = "/tmp/"+self.name['VM_name']+"raw"
        self.disk = c.ComplexConfiguration.disk(self, diskdata, source_file)
        self.iothreads = c.BasicConfiguration.iothreads(self, "1")
        return self

    def video_perf(self):
        """
        video performance
        """
        self.video = c.BasicConfiguration.video(self, "qxl")
        return self

    def network_perf(self):
        """
        network performance
        """
        macaddress = util.macaddress()
        self.network = c.ComplexConfiguration.network(self, macaddress, "default", "virtio", "on")
        return self

    def clock_perf(self):
        """
        clock perf
        """
        dataclock = "<timer name=\'rtc\' tickpolicy=\'catchup\'/>"
        dataclock += "\n    <timer name=\'pit\' tickpolicy=\'delay\'/>"
        dataclock += "\n    <timer name=\'hpet\' present=\'no\'/>"
        self.clock = c.BasicConfiguration.clock(self, "utc", dataclock)
        return self

    def host_hardware(self):
        """
        host hardware
        """
        self.name = c.BasicConfiguration.name(self, "host_hardware")
        # features
        # <ioapic driver='kvm'/>
        # kernel_irqchip=on
        return self

    def access_host_fs_perf(self):
        """
        access host filesystem
        """
        self.access_host_fs = c.ComplexConfiguration.access_host_fs(self)
        return self
