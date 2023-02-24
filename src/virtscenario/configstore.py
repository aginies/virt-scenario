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

import yaml
import os

import virtscenario.util as util

class ConfigStore:
    base_path = None
    name = None
    hypervisor = None
    attestation = False

    def __init__(self, base_path="./"):
        self.base_path = base_path

    def initialize(self, name, hypervisor):
        self.name = name
        self.hypervisor = hypervisor.name

    def set_attestation(self, attestation):
        self.attestation = attestation

    def build_path(self):
        if self.base_path == "":
            return self.name

        path = os.path.expanduser(self.base_path);
        if path[-1] != '/':
            path += '/';

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

def create_config_store(config, vm_data, hypervisor):
    cfg_store = ConfigStore(config.vm_config_store)
    cfg_store.initialize(vm_data.name['VM_name'], hypervisor)
    if cfg_store.exists():
        util.print_error("VM with name {} already exists. Please set a new name and try again".format(vm_data.name['VM_name']));
        return None;
    return cfg_store
