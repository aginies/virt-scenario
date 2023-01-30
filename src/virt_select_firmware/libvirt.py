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
"""
libvirt loader
"""

import xml.etree.ElementTree as ET
import subprocess

def get_libvirt_loaders():
    """
    get all libvirt loaders available
    """
    cmd = 'virsh domcapabilities'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=2)
    if errs:
        print(errs)
    out = str(out, 'UTF-8')

    libvirt_loaders = []

    root = ET.fromstring(out)
    loaders_list = root.findall("./os[@supported='yes']/loader[@supported='yes']/value")
    for loader in loaders_list:
        libvirt_loaders.append(loader.text)

    return libvirt_loaders

def loader_supported(loader, libvirt_loaders):
    """
    loader supported
    """
    for lib_loader in libvirt_loaders:
        if loader == lib_loader:
            return True
    return False
