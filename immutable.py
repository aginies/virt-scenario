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
Immutable data
"""


# filing DATA
# using template
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
