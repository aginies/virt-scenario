# -*- coding: utf-8 -*-
# Authors: Joerg Roedel <jroedel@suse.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# vim: ts=4 sw=4 et

import argparse

import virt_select_firmware.firmware as f
import virt_select_firmware.libvirt as l

def main():
    firmwares = f.load_firmware_info()
    loaders = l.get_libvirt_loaders()

    parser = argparse.ArgumentParser(prog='virt-select-firmware',
                                     description='Select correct firmware for a virtual machine')
    parser.add_argument('-a', '--arch', default='x86_64',
                        help='CPU architecture of the virtual machine',
                        action='store', dest='arch')
    parser.add_argument('-f', '--feature', default=[],
                        help='Required feature of firmware',
                        action='append', dest='features')

    args = parser.parse_args();

    for fw in firmwares:
        if l.loader_supported(fw.executable, loaders) and fw.match(args.arch, args.features):
            print(fw.executable)
