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
Qemu list of options and other VAR
"""

OVMF_PATH = "/usr/share/qemu"
OVMF_VARS = "/var/lib/libvirt/qemu/nvram"

# qemu-system-x86_64 -machine help
LIST_MACHINETYPE = ['microvm', 'xenfv-4.2', 'xenfv', 'xenfv-3.1', 'pc', 'pc-i440fx-6.2',
                    'pc-i440fx-6.1', 'pc-i440fx-6.0', 'pc-i440fx-5.2', 'pc-i440fx-5.1',
                    'pc-i440fx-5.0', 'pc-i440fx-4.2', 'pc-i440fx-4.1', 'pc-i440fx-4.0',
                    'pc-i440fx-3.1', 'pc-i440fx-3.0', 'pc-i440fx-2.9', 'pc-i440fx-2.8',
                    'pc-i440fx-2.7', 'pc-i440fx-2.6', 'pc-i440fx-2.5', 'pc-i440fx-2.4',
                    'pc-i440fx-2.3', 'pc-i440fx-2.2', 'pc-i440fx-2.12', 'pc-i440fx-2.11',
                    'pc-i440fx-2.10', 'pc-i440fx-2.1', 'pc-i440fx-2.0', 'pc-i440fx-1.7',
                    'pc-i440fx-1.6', 'pc-i440fx-1.5', 'pc-i440fx-1.4', 'q35', 'pc-q35-6.2',
                    'pc-q35-6.1', 'pc-q35-6.0', 'pc-q35-5.2', 'pc-q35-5.1', 'pc-q35-5.0',
                    'pc-q35-4.2', 'pc-q35-4.1', 'pc-q35-4.0.1', 'pc-q35-4.0', 'pc-q35-3.1',
                    'pc-q35-3.0', 'pc-q35-2.9', 'pc-q35-2.8', 'pc-q35-2.7', 'pc-q35-2.6',
                    'pc-q35-2.5', 'pc-q35-2.4', 'pc-q35-2.12', 'pc-q35-2.11', 'pc-q35-2.10',
                    'isapc']

LIST_BOOTDEV = ['hd', 'cdrom', 'floppy', 'nertwork']
