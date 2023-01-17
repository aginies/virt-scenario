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
configure dict with data to use to create the XML config
"""

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
        self.usb_data = None
        self.watchdog_data = None
        self.cpumode_data = None
        self.power_data = None
        self.emulator_data = None
        self.memory_data = None
        self.os_data = None
        self.ondef_data = None
        self.features_data = None
        self.clock_data = None
        self.iothreads_data = None
        self.security_data = None
        self.video_data = None

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

    def cpumode_pass(self, migratable, extra):
        """
        cpumode def
        """
        self.cpumode_data = {
            'migratable': migratable,
            'extra': extra,
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

    def usb(self, model):
        """
        define the usb model
        """
        self.usb_data = {
            'model': model,
        }
        return self.usb_data

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

    def features(self, features):
        """
        features def
        """
        self.features_data = {
            'features': features,
        }
        return self.features_data

    def security(self, sectype, secdata):
        """
        security def
        """
        self.security_data = {
            'sectype': sectype,
            'secdata': secdata,
        }
        return self.security_data

    def clock(self, clock_offset, clock):
        """
        clock def
        """
        self.clock_data = {
            'clock_offset': clock_offset,
            'clock': clock,
        }
        return self.clock_data

    def video(self, vtype):
        """
        video def
        """
        self.video_data = {
            'type': vtype,
        }
        return self.video_data

    def iothreads(self, iothreads):
        """
        iothreads def
        """
        self.iothreads_data = {
            'iothreads': iothreads,
        }
        return self.iothreads_data

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
        self.access_host_fs_data = None

    def disk(self, disk):
        """
        disk
        """
        source_file = disk.disk_path+"/"+disk.storage_name+"."+disk.disk_format
        self.disk_data = {
            'disk_type': disk.disk_type,
            'disk_cache': disk.disk_cache,
            'disk_target': disk.disk_target,
            'disk_bus': disk.disk_bus,
            'path': disk.disk_path,
            'format': disk.disk_format,
            'storage_name': disk.storage_name,
            'source_file': source_file,
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

    def tpm_emulated(self, tpm_model, tpm_type, version):
        """
        TPM emulated
        """
        self.tpm_data = {
            'tpm_model': tpm_model,
            'tpm_type': tpm_type,
            'version': version,
        }
        return self.tpm_data
