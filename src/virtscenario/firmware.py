# Authors: Joerg Roedel <jroedel@suse.com>
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

import virt_select_firmware.firmware as fw

def default_firmware_info():
    return fw.load_firmware_info()

def reload_firmware_info(path):
    return fw.load_firmware_info(path)

def find_firmware(fw_info, arch, features=[], interface='uefi'):
    for firmw in fw_info:
        if firmw.match(arch=arch, features=features, interface=interface):
            return firmw.executable

    return ''
