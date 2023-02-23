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

import yaml
import os
import virtscenario.util as util

class HyperVisor:
   """
   Represents a connection to a LibVirt instance running locally or remote
   """ 
   def __init__(self):
       self.name = "localhost"
       self.url = "qemu:///system"
       self.sev_cert = None

   def initialize(self, name, url, sev_cert):
       self.name = name
       self.url = url
       self.sev_cert = sev_cert

# Default to running on the same host
HV_LIST = [ HyperVisor() ]

def load_hypervisors(filename):
    if not os.path.isfile(filename):
        print("{} not found or not valid".format(filename))
        return

    with open(filename, "r") as stream:
        try:
            data = yaml.safe_load(stream);
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
            hv = HyperVisor()
            hv.initialize(name, url, sev_cert)
            HV_LIST.append(hv)

def select_hypervisor():
    if len(HV_LIST) == 1:
        return HV_LIST[0]
 
    while True:
        print("Available hypervisor configurations")
        for hv in HV_LIST:
            print("    {}".format(hv.name))
        name = input("Please enter a valid Hypervisor configuration: ")
        for hv in HV_LIST:
            if hv.name == name:
                return hv
