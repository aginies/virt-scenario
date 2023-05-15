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
Util
"""

import subprocess
import os
import getpass
import shutil
import yaml
import virtscenario.qemulist as qemulist
import virtscenario.xmlutil as xmlutil

def system_command(cmd):
    """
    Launch a system command
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=2)
    out = str(out, 'UTF-8')
    return out, errs

def cmd_exists(cmd):
    """
    check a command exist
    """
    return shutil.which(cmd) is not None

COLORS = {
    'reset': '\033[0m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'purple': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bg_black': '\033[40m',
    'bg_red': '\033[41m',
    'bg_green': '\033[42m',
    'bg_yellow': '\033[43m',
    'bg_blue': '\033[44m',
    'bg_purple': '\033[45m',
    'bg_cyan': '\033[46m',
    'bg_white': '\033[47m',
}

def esc(color):
    """
    Return the ANSI escape code for the given color
    """
    return COLORS[color]

def print_error(text):
    """
    Print error in red
    """
    prefix = esc('bg_yellow') + ' ERROR ' + esc('reset') + " "
    formated_text = prefix+esc('red')+text+esc('reset')+"\n"
    print(formated_text)

def print_warning(text):
    """
    Print warning in red
    """
    prefix = esc('bg_yellow') + ' WARNING ' + esc('reset') + " "
    formated_text = "\n     "+prefix+esc('red') +text.upper()+esc('reset')+"\n"
    print(formated_text)

def print_recommended(toreport):
    """
    recommended VS user setting
    """
    print("####################################################################################")
    print("#{:^20s}|{:^30s}|{:^30s}#".format("Parameter", "Recommended", "User Settings"))
    print("####################################################################################")
    total = len(toreport)+1
    for number in range(1, int(total)):
        print("|{:^20s}|{:^30s}|{:^30s}|".format(toreport[number]["title"], toreport[number]["rec"], str(toreport[number]["set"])))
        print("|----------------------------------------------------------------------------------|")
    print("\n")

def print_ok(text):
    """
    Print ok in green
    """
    formated_text = esc('green')+text+esc('reset')
    print(formated_text)

def print_summary(text):
    """
    Print title with blue background
    """
    formated_text = "\n"+esc('bg_blue')+text+esc('reset')
    print(formated_text)

def print_title(text):
    """
    Print summary with magenta background
    """
    formated_text = esc('bg_purple')+text.upper()+esc('reset')
    print(formated_text)

def print_summary_ok(text):
    """
    Print summary with green background
    """
    formated_text = esc('bg_green')+text+esc('reset')+"\n"
    print(formated_text)

def print_command(text):
    """
    Print command with blue background
    """
    formated_text = esc('bg_blue')+text+esc('reset')+"\n\n"
    print(formated_text)

def print_data(data, value):
    """
    Print the data
    """
    formated_text = "\n"+esc('bg_cyan')+data+" "+esc('reset')+" "+value.rstrip()
    print(formated_text.strip())

def generate_mac_address() -> str:
    """
    generate a mac address
    """
    import string
    import random
    HEX_DIGITS = string.hexdigits.upper()
    PREFIX_DIGITS = "02468ACE"

    prefix = ''.join(random.sample(PREFIX_DIGITS, k=2))
    octets = [prefix] + [''.join(random.sample(HEX_DIGITS, k=2)) for _ in range(5)]

    mac_address = ':'.join(octets)
    return mac_address

def bytes_to_gibibytes(bbytes):
    """
    Convert bytes to gibibytes.
    """
    if not isinstance(bbytes, (int, float)) or bbytes < 0:
        raise ValueError("It must be an int or a float.")

    BYTES_IN_GIBIBYTE = 1024 ** 3
    gibibytes = bbytes / BYTES_IN_GIBIBYTE
    return round(gibibytes, 2)

def validate_yaml_file(file_path):
    """
    validate the yaml file
    """
    try:
        with open(file_path, 'r') as stream:
            yaml_contents = yaml.safe_load(stream)
    except FileNotFoundError:
        print(f"file {file_path} not found.")
        return False
    except yaml.YAMLError as exc:
        print(f"Error while parsing the YAML file: {exc}")
        return False
    if not isinstance(yaml_contents, dict):
        print("File should contain a dict.")
        return False

    return yaml_contents

def validate_xml(xmlfile):
    """
    validate the generated file
    """
    print_summary("\nValidation of the XML file")
    cmd = "virt-xml-validate "+xmlfile
    out, errs = system_command(cmd)
    if errs:
        print(errs)
    print(out)

def check_iam_root():
    """
    some part needs to be root user
    """
    if os.geteuid() != 0:
        print_error("You are not root.")
        return False
    return True

def check_tpm():
    """
    check /dev/tpm0 exist
    """
    path_to_tpm = "/dev/tpm0"
    if not os.path.exists(path_to_tpm):
        print_error("No {} found".format(path_to_tpm))
        return False
    return True

def update_virthost_cert_file(yaml_file_path, hypervisor, new_sev_cert_path):
    # Load the YAML file
    with open(yaml_file_path, 'r') as stream:
        data = yaml.safe_load(stream)

    if hypervisor in data:
        if 'sev-cert' in data[hypervisor]:
            # Update the value of the sev-cert key
            data[hypervisor]['sev-cert'] = new_sev_cert_path
        else:
            # no value, add a new sev-cert key
            data[hypervisor]['sev-cert'] = new_sev_cert_path

        with open(yaml_file_path, 'w') as fil:
            try:
                yaml.dump(data, fil)
            finally:
                fil.close()
    else:
        print_error("Hypervisor "+hypervisor+" not found ....")

    stream.close()

def to_report(toreport, conffile):
    """
    Report diff between recommend and user settings
    """
    if len(toreport) != 6:
        print_summary("\nComparison table between user and recommended settings")
        print_warning("You are over writing scenario setting!")
        print("     Overwrite are from file: "+conffile+"\n")
        print_recommended(toreport)

def input_password():
    """
    check input password until this is ok
    """
    while True:
        password1 = getpass.getpass("Please enter a password to encrypt the VM image: ")
        password2 = getpass.getpass("Confirm this password: ")
        if password1 == password2:
            return password1
        else:
            print("Passwords do not match. Please try again.")

def show_how_to_use(vmname):
    """
    show how to use the scenario
    """
    print_title("How to use this on your system")
    print_ok("Use the virt-scenario-launch tool:\n")
    print("virt-scenario-launch --start "+vmname+"\n")

def final_step_guest(cfg_store, data, verbose):
    """
    show setting from xml
    create the XML config
    validate the XML file
    """
    filename = cfg_store.get_domain_config_filename()
    print_title("Guest Section")
    create_xml_config(filename, data)
    if verbose is True:
        xmlutil.show_from_xml(filename)
    validate_xml(filename)
    cfg_store.store_config()
    print_summary_ok("Guest XML Configuration is done")

def find_ext_file(ext):
    """
    Show all extension files in current path
    """
    files_list = []
    for files in os.listdir('.'):
        if files.endswith(ext):
            files_list.append(files)
    return files_list

def create_xml_config(filename, data):
    """
    draft xml create step
    create the xml file
    """
    # DEBUG from pprint import pprint; pprint(vars(data))
    print_title("\nCreate the XML file")
    # final XML creation
    # start the domain definition
    xml_all = ""
    # first line must be a warning, kvm by default
    xml_all = "<!-- WARNING: THIS IS A GENERATED FILE FROM VIRT-SCENARIO -->\n"
    xml_all += "<domain type='kvm'>\n"
    xml_all += data.name+data.memory+data.vcpu+data.osdef+data.security
    xml_all += data.features+data.cpumode+data.clock+data.hugepages
    xml_all += data.ondef+data.power+data.iothreads
    # all below must be in devices section
    xml_all += "\n  <devices>"
    xml_all += data.emulator+data.controller
    xml_all += data.disk+data.network+data.CONSOLE
    xml_all += data.CHANNEL+data.inputmouse+data.inputkeyboard
    xml_all += data.GRAPHICS+data.video+data.RNG+data.watchdog
    xml_all += data.hostfs+data.usb+data.tpm+data.cdrom
    # close the device section
    xml_all += "</devices>\n"
    # close domain section
    xml_all += "</domain>\n"

    # create the file from the template and setting
    create_from_template(filename, xml_all)
    if "loader" in data.custom:
        if data.loader is None:
            executable = qemulist.OVMF_PATH+"/ovmf-x86_64-smm-opensuse-code.bin"
        else:
            executable = data.loader
        xmlutil.add_loader_nvram(filename, executable, qemulist.OVMF_VARS+"/"+data.callsign+".VARS")
    if "vnet" in data.custom:
        xmlutil.change_network_source(filename, data.vnet)
    ### if "XXXX" in data.custom:

def create_from_template(finalfile, xml_all):
    """
    create the VM domain XML from all template input given
    """
    print_title("\nCreate The XML VM configuration")
    print(finalfile)
    with open(finalfile, 'w') as file_h:
        file_h.write(xml_all)
