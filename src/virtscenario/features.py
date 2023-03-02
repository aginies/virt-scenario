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

import virtscenario.util as util
import virtscenario.configuration as c

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
    def __init__(self, dtype, dcache, dtarget, dbus, dpath, storage_name, dformat):
        """
        init disk
        """
        self.disk_type = dtype
        self.disk_cache = dcache
        self.disk_target = dtarget
        self.disk_bus = dbus
        self.disk_path = dpath
        self.disk_format = dformat
        self.storage_name = storage_name

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
        return self.features

    def security_f(self, sev_info):
        """
        security
        """
        self.security = c.BasicConfiguration.security(self, "sev", sev_info.get_xml())
        return self.security

    def memory_perf(self):
        """
        memory perf
        """
        unit = MemoryUnit("Mib", "Mib")
        self.memory = c.BasicConfiguration.memory(self, unit, "8192", "8192")
        return self.memory

    def storage_perf(self):
        """
        storage performance
        """
        # Disk
        diskdata = Disk("file", "none", "vda", "virtio", "/tmp", self.name['VM_name'], "raw")
        self.disk = c.ComplexConfiguration.disk(self, diskdata)
        self.iothreads = c.BasicConfiguration.iothreads(self, "4")
        return self

    def video_perf(self):
        """
        video performance
        """
        self.video = c.BasicConfiguration.video(self, "virtio")
        return self.video

    def network_perf(self):
        """
        network performance
        """
        macaddress = util.macaddress()
        self.network = c.ComplexConfiguration.network(self, macaddress, "default", "virtio")
        return self.network

    def clock_perf(self):
        """
        clock perf
        """
        dataclock = "<timer name=\'rtc\' tickpolicy=\'catchup\'/>"
        dataclock += "\n    <timer name=\'pit\' tickpolicy=\'delay\'/>"
        dataclock += "\n    <timer name=\'hpet\' present=\'no\'/>"
        self.clock = c.BasicConfiguration.clock(self, "utc", dataclock)
        return self.clock

    def host_hardware(self):
        """
        host hardware
        """
        self.name = c.BasicConfiguration.name(self, "host_hardware")
        # features
        # <ioapic driver='kvm'/>
        # kernel_irqchip=on
        return self.name

    def access_host_fs_perf(self):
        """
        access host filesystem
        """
        self.access_host_fs = c.ComplexConfiguration.access_host_fs(self)
        return self.access_host_fs
