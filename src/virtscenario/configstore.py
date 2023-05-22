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
Guest Configuration Store
"""

import os
import ast
import xml.etree.ElementTree as ET
import yaml
import virtscenario.util as util

class ConfigStore:
    base_path = None
    name = None
    hypervisor = None
    attestation = False
    tik_file = ""
    tek_file = ""
    policy = 0
    loader = None

    def __init__(self, base_path="./"):
        self.base_path = base_path
        self.domain_config = ""

    def initialize(self, name, hypervisor):
        self.name = name
        self.hypervisor = hypervisor.name

    def set_attestation(self, attestation):
        self.attestation = attestation

    def build_path(self):
        if self.base_path == "":
            return self.name

        path = os.path.expanduser(self.base_path)
        if path[-1] != '/':
            path += '/'

        return path + self.name + '/'

    def exists(self):
        return os.path.isdir(self.build_path())

    def get_path(self):
        path = self.build_path()
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def get_domain_config_filename(self):
        path = self.get_path()
        return path + 'domain.xml'

    def get_config_filename(self):
        path = self.get_path()
        return path + 'config.yaml'

    def store_config(self):
        filename = self.get_config_filename()
        config = {
            'name': self.name,
            'host': self.hypervisor,
            'domain-config': self.get_domain_config_filename(),
            'attestation': self.attestation
        }

        with open(filename, 'w') as config_yaml:
            yaml.dump(config, config_yaml)

    def load_config(self, vmname):
        filename = self.base_path + "/" + vmname + "/config.yaml"
        if not os.path.isfile(filename):
            print("VM {} not found".format(vmname))
            return None
        with open(filename, 'r') as file:
            data = yaml.full_load(file)
            for key, value in data.items():
                if key == 'name':
                    self.name = value
                elif key == 'host':
                    self.hypervisor = value
                elif key == 'domain-config':
                    self.domain_config = value
                elif key == 'attestation' and value is True:
                    self.attestation = True

        if self.attestation is True and os.path.isfile(self.domain_config):
            xmlroot = ET.parse(self.domain_config)
            elem = xmlroot.findall("./launchSecurity[@type='sev']/policy")
            if elem is None:
                print("Failed to load SEV policy from {} - disabling attestation".format(self.domain_config))
                self.attestation = False
                return self

            self.policy = ast.literal_eval(elem[0].text)

            elem = xmlroot.findall("./os/loader")
            if elem is not None:
                self.loader = elem[0].text

            self.tik_file = self.base_path + "/" + vmname + "/tik.bin"
            self.tek_file = self.base_path + "/" + vmname + "/tek.bin"

        return self

    def sev_validate_params(self):
        params = "--tik {} --tek {} --policy {} --domain {}".format(self.tik_file, self.tek_file, str(self.policy), self.name)
        if self.loader is not None:
            params = "{} --firmware {}".format(params, self.loader)

        return params

def create_config_store(config, vm_data, hypervisor, overwrite):
    cfg_store = ConfigStore(config.vm_config_store)
    #from pprint import pprint
    #print("IN CONFIG STORE --------------------------")
    #pprint(vars(vm_data))
    #print("END CONFIG STORE --------------------------")
    cfg_store.initialize(vm_data.name['VM_name'], hypervisor)
    if cfg_store.exists() and overwrite != "on":
        util.print_error("VM with name {} already exists in {} directory.\nPlease set a new name and try again.\nYou can also use the option: overwrite on".format(vm_data.name['VM_name'], cfg_store.get_path()))
        return None
    elif cfg_store.exists() and overwrite == "on":
        util.print_ok("VM with name {} already exists in {} directory.\nForce mode enabled, overwriting files.".format(vm_data.name['VM_name'], cfg_store.get_path()))
    return cfg_store
