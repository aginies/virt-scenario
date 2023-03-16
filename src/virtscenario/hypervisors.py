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

"""
Hypervisor List
"""

import os
import yaml
import libvirt

import virtscenario.util as util

class HyperVisor:
    """
    Represents a connection to a LibVirt instance running locally or remote
    """
    def __init__(self):
        self.name = "localhost"
        self.url = "qemu:///system"
        self.sev_cert = None
        self.conn = None

    def initialize(self, name, url, sev_cert):
        self.name = name
        self.url = url
        self.sev_cert = sev_cert

        # Check if cert-file exists
        if self.sev_cert is not None and not os.path.isfile(self.sev_cert):
            self.sev_cert = None

    def is_connected(self):
        return self.conn is not None

    def connect(self):
        if self.conn is None:
            self.conn = libvirt.open(self.url)
        return self.is_connected()

    def domain_capabilities(self):
        return self.conn.getDomainCapabilities()

    def dominfo(self, name):
        try:
            return self.conn.lookupByName(name)
        except libvirt.libvirtError:
            return None

    def define_domain(self, xmlfile):
        file = open(xmlfile, 'r')
        xml = file.read()
        file.close()

        try:
            dom = self.conn.defineXML(xml)
        except libvirt.libvirtError as e:
            print(repr(e))
            return

    def has_sev_cert(self):
        return self.sev_cert is not None

    def sev_cert_file(self):
        return self.sev_cert

# Default to running on the same host
HV_LIST = [HyperVisor()]
HV_SELECTED = HV_LIST[0]

def load_hypervisors(filename):
    global HV_LIST
    global HV_SELECTED

    if not os.path.isfile(filename):
        print("{} not found or not valid".format(filename))
        return

    with open(filename, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError:
            util.print_error("Failed to load Hypervisor list")

        old_list = HV_LIST.copy()
        HV_LIST.clear()

        for item, conf in data.items():
            name = item
            url = ""
            sev_cert = None
            if 'url' in conf.keys():
                url = conf['url']
            if 'sev-cert' in conf.keys():
                sev_cert = conf['sev-cert']
            hyperv = HyperVisor()
            hyperv.initialize(name, url, sev_cert)
            HV_LIST.append(hyperv)
        if not HV_LIST:
            # Reset to old list if nothing was loaded
            HV_LIST = old_list
        HV_SELECTED = HV_LIST[0]

def list_hypervisors():
    global HV_LIST
    global HV_SELECTED

    print("Available Hypervisor configurations:")
    for hyperv in HV_LIST:
        selected = ' '
        if hyperv.name == HV_SELECTED.name:
            selected = '*'
        print("  {} {}".format(selected, hyperv.name))

def get_hypervisor(name):
    global HV_LIST

    for hyperv in HV_LIST:
        if hyperv.name == name:
            return hyperv

    return None

def set_default_hv(name):
    global HV_LIST
    global HV_SELECTED

    for hyperv in HV_LIST:
        if hyperv.name == name:
            HV_SELECTED = hyperv
            return True
    return False

def select_hypervisor():
    HV_SELECTED.connect()
    return HV_SELECTED
