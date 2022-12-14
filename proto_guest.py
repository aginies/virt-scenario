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
Guest side
"""

import libvirt
from pathlib import Path
import proto_util as util

FILES_LIST = {
        ''
        }

def create_default_domain_xml(file):
    """
    create the VM domain XML
    """
    cmd = "virt-install --print-xml --virt-type kvm --arch x86_64 --machine pc-q35-6.2 --osinfo sles12sp5 --rng /dev/urandom --network test_net >" +file
    util.system_command(cmd)

def concatenate_files(FILES_LIST):
    """
    concatenate files
    """
    vmxmlfile = 'tet_vmconfig.xml'
    xmlfiles = ['file1.txt', 'file2.txt', 'file3.txt']
    print('VM config file: '+vmxmlfile)
    with open(vmxmlfile, 'w') as outfile:
        for fname in xmlfiles:
            print('Will concatenate fname: '+fname)
            my_file = Path(fname)
            if my_file.is_file():
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
            else:
                print(fname + ' doesnt exist ')


file = "d.xml"
create_default_domain_xml(file)
