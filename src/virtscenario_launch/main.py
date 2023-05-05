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
Main
"""

import os
import argparse
import yaml
import libvirt
import virtscenario.hypervisors as hv
import virtscenario.configstore as cs
import virtscenario.configuration as configuration
import virtscenario.util as util

def get_arg_parse():
    parser = argparse.ArgumentParser(description='Perform SEV guest attestation and launch guest')
    parser.add_argument('--list', '-l', help='List domain configurations', action='store_true')
    parser.add_argument('--start', help='Start domain')
    parser.add_argument('--status', help='Check domain status')
    parser.add_argument('--off', help="Shutdown domain")
    parser.add_argument('--force', '-f', help="Force domain off", action="store_true")
    return parser

def parse_command_line():
    return get_arg_parse().parse_args()
class VMConfigs:
    """
    VM Configurations
    """
    conf_file = ""
    base_path = "./"
    def __init__(self):
        self.conf_file = configuration.find_conffile()
        self.get_base_path()

    def get_base_path(self):
        with open(self.conf_file) as file:
            data = yaml.full_load(file)
            for item, value in data.items():
                if item == "config":
                    for subitem in value:
                        for k2, v2 in subitem.items():
                            if k2 == 'vm-config-store':
                                self.base_path = os.path.expanduser(v2)

    def list_vms(self):
        vm_array = []
        for vmname in os.listdir(self.base_path):
            filename = self.base_path + "/" + vmname + "/config.yaml"
            if os.path.isfile(filename):
                vm_array.append(vmname)

        return vm_array

    def load_vm(self, vmname):
        config = cs.ConfigStore(self.base_path)
        return config.load_config(vmname)

def list_vms():
    configs = VMConfigs()

    print("Available VMs:")
    for vmname in configs.list_vms():
        print("  {}".format(vmname))

def validate_vm(vm):
    if not vm.attestation:
        return True

    params = vm.sev_validate_params()
    # TODO fix --insecure when client/server split is ready
    cmd = "virt-qemu-sev-validate --insecure {}".format(params)

    out, errs = util.system_command(cmd)
    if errs or not out:
        print(errs)
        return False

    ret = out.find("OK: Looks good to me")
    if ret == -1:
        return False

    print("SEV(-ES) attestation passed!")
    return True

def launch_vm(name):
    hvfile = configuration.find_hvfile()
    hv.load_hypervisors(hvfile)

    configs = VMConfigs()
    vm = configs.load_vm(name)

    if vm is None:
        print("Configuration for domain {} not found".format(name))
        return

    hypervisor = hv.get_hypervisor(vm.hypervisor)
    if hypervisor is None:
        print("Hypervisor {} not found!".format(vm.hypervisor))
        return

    hypervisor.connect()
    if not hypervisor.is_connected():
        print("Failed to connect to hypervisor {}".format(vm.hypervisor))
        return

    dom = hypervisor.dominfo(name)
    if dom is None:
        hypervisor.define_domain(vm.domain_config)
        dom = hypervisor.dominfo(name)

    state, _ = dom.state()
    if state != libvirt.VIR_DOMAIN_RUNNING and state != libvirt.VIR_DOMAIN_PAUSED:
        # Launch domain in paused state
        if dom.createWithFlags(libvirt.VIR_DOMAIN_START_PAUSED) < 0:
            print("Failed to start domain '{}'".format(name))
    elif state == libvirt.VIR_DOMAIN_RUNNING:
        print("Domain {} already running".format(name))
    else:
        print("Domain {} in an unsupported state - please shut it down first".format(name))
        return

    state, _ = dom.state()

    if validate_vm(vm) is False:
        print("Validation failed for domain {} - shutting down".format(name))
        dom.destroy()
        return

    print("Validation successfull for domain {}".format(name))

    if state == libvirt.VIR_DOMAIN_PAUSED:
        dom.resume()

def status_vm(name):
    hvfile = configuration.find_hvfile()
    hv.load_hypervisors(hvfile)

    configs = VMConfigs()
    vm = configs.load_vm(name)

    if vm is None:
        print("Configuration for domain {} not found".format(name))
        return

    hypervisor = hv.get_hypervisor(vm.hypervisor)
    if hypervisor is None:
        print("Hypervisor {} not found!".format(vm.hypervisor))
        return

    hypervisor.connect()
    if not hypervisor.is_connected():
        print("Failed to connect to hypervisor {}".format(vm.hypervisor))
        return

    dom = hypervisor.dominfo(name)
    if dom is None:
        print("No such domain {}".format(name))
        return

    state, _ = dom.state()
    if state == libvirt.VIR_DOMAIN_NOSTATE:
        state_str = "No state"
    elif state == libvirt.VIR_DOMAIN_RUNNING:
        state_str = "Running"
    elif state == libvirt.VIR_DOMAIN_BLOCKED:
        state_str = "Blocked"
    elif state == libvirt.VIR_DOMAIN_PAUSED:
        state_str = "Paused"
    elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
        state_str = "Shutdown"
    elif state == libvirt.VIR_DOMAIN_SHUTOFF:
        state_str = "Shutoff"
    elif state == libvirt.VIR_DOMAIN_CRASHED:
        state_str = "Crashed"
    elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
        state_str = "PM suspend"
    else:
        state_str = "Unknown"

    print("Domain {} state: {}".format(name, state_str))

    if state == libvirt.VIR_DOMAIN_RUNNING or state == libvirt.VIR_DOMAIN_PAUSED:
        if validate_vm(vm) is False:
            print("Validation failed for domain {}".format(name))
            return

        print("Validation successfull for domain {}".format(name))

    return

def shutdown_vm(name):
    global FORCE

    hvfile = configuration.find_hvfile()
    hv.load_hypervisors(hvfile)

    configs = VMConfigs()
    vm = configs.load_vm(name)

    if vm is None:
        print("Configuration for domain {} not found".format(name))
        return

    hypervisor = hv.get_hypervisor(vm.hypervisor)
    if hypervisor is None:
        print("Hypervisor {} not found!".format(vm.hypervisor))
        return

    hypervisor.connect()
    if not hypervisor.is_connected():
        print("Failed to connect to hypervisor {}".format(vm.hypervisor))
        return

    dom = hypervisor.dominfo(name)
    if dom is None:
        print("No such domain {}".format(name))
        return

    state, _ = dom.state()
    if state == libvirt.VIR_DOMAIN_RUNNING or state == libvirt.VIR_DOMAIN_PAUSED:
        # Shutdown domain
        if FORCE is True:
            print("Forcing domain {} off".format(name))
            dom.destroy()
        else:
            print("Shutting domain {} down".format(name))
            dom.shutdown()
    else:
        print("Domain {} in an unsupported state - please use virsh".format(name))
        return

FORCE = False

def main():
    """
    Main; use arg to display mathings firmwares
    """
    global FORCE

    args = parse_command_line()
    if args.force:
        FORCE = True
    if args.list:
        list_vms()
    elif args.start:
        launch_vm(args.start)
    elif args.status:
        status_vm(args.status)
    elif args.off:
        shutdown_vm(args.off)
    else:
        get_arg_parse().print_help()
