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
import sys
import yaml
import libvirt
import xml.etree.ElementTree as ET

import virtscenario.util

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
            try:
                print("Connecting to libvirt "+self.url+" ...")
                self.conn = libvirt.open(self.url)
                ver = self.conn.getVersion()
                virtscenario.util.print_ok('Connected to libvirtd socket; Version: '+str(ver))
                return self.is_connected()

            except libvirt.libvirtError as verror:
                print(repr(verror), file=sys.stderr)
                return 666

    def domain_capabilities(self):
        return self.conn.getDomainCapabilities()

    def secret_list(self):
        """
        return list of secret key
        """
        return self.conn.listSecrets()

    def domain_list(self):
        """
        return all domains available on the hypervisor
        """
        all = []
        active_domain_ids = self.conn.listDomainsID()
        active_domains = [self.conn.lookupByID(domain_id) for domain_id in active_domain_ids]
        inactive_domain_ids = self.conn.listDefinedDomains()
        inactive_domains = [self.conn.lookupByName(domain_name) for domain_name in inactive_domain_ids]
        for domain in active_domains:
            all.append(domain.name())
        for domain in inactive_domains:
            all.append(domain.name())
        return all

    def remove_domain(self, domain):
        """
        remove a domain by name
        """
        all_domains = self.domain_list()
        if domain in all_domains:
            if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                virtscenario.util.print_warning(f"Domain {domain_name} is running! I will not undefine it.")
            else:
                domain = self.conn.lookupByName(domain)
                domain.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_NVRAM)

    def secret_lookup_by_uuid(self, secret_name):
        """
        look by uuid
        """
        return self.conn.secretLookupByUUIDString(secret_name)

    def network_list(self):
        """
        Return a list of all network available on the hypervisor
        """
        networks = self.conn.listNetworks()
        inactive_networks = self.conn.listDefinedNetworks()
        return inactive_networks+networks

    def get_all_machine_type(self):
        """
        get the list of available machine type from the hypervisor
        """
        all_machine_type = []
        self.conn = libvirt.open()
        host = self.conn.getCapabilities()
        root = ET.fromstring(host)
        find_machine_type = root.findall('.//guest/arch/machine')
        for value in find_machine_type:
            if value not in all_machine_type:
                all_machine_type.append(value.text)

        return sorted(all_machine_type)

    def dominfo(self, name):
        for dom in self.conn.listDefinedDomains():
            if dom == name:
                return self.conn.lookupByName(name)
        for dom in self.conn.listAllDomains(0):
            if dom.name() == name:
                return dom
        return None

    def define_domain(self, xmlfile):
        file = open(xmlfile, 'r')
        xml = file.read()
        file.close()

        try:
            dom = self.conn.defineXML(xml)
            return dom
        except libvirt.libvirtError as err:
            print(repr(err))
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
            virtscenario.util.print_error("Failed to load Hypervisor list")

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

def list_all_hypervisors():
    global HV_LIST
    list = []
    for hyperv in HV_LIST:
        list.append(hyperv.name)
    return list

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

def connect_hypervisor(name):
    for hyperv in HV_LIST:
        if hyperv.name == name:
            HV_SELECTED = hyperv
            HV_SELECTED.connect()
            return HV_SELECTED
