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
import uuid
import os
import getpass
import shutil
import yaml
import json
import socket
import virtscenario.qemulist as qemulist
import virtscenario.xmlutil as xmlutil
import virtscenario.hypervisors as hv

def system_command(cmd):
    """
    Launch a system command
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=5)
    #out = str(out, 'UTF-8')
    out = out.decode('utf-8')
    return out, errs

def run_command_with_except(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        stdout = result.stdout
        stderr = result.stderr
        return stdout, stderr
    except subprocess.CalledProcessError as e:
        print(f"Command:\n'{cmd}'\n failed with exit code {e.returncode}:")
        print(e.stderr)

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

def print_info(text):
    """
    Print info in green
    """
    formated_text = esc('bg_blue')+text+esc('reset')+"\n"
    print(formated_text)

def print_summary(text):
    """
    Print title with blue background
    """
    formated_text = "\n"+esc('bg_blue')+text+esc('reset')+"\n"
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
    hex_digits = string.hexdigits.upper()
    prefix_digits = "02468ACE"

    prefix = ''.join(random.sample(prefix_digits, k=2))
    octets = [prefix] + [''.join(random.sample(hex_digits, k=2)) for _ in range(5)]

    mac_address = ':'.join(octets)
    return mac_address

def bytes_to_gibibytes(bbytes):
    """
    Convert bytes to gibibytes.
    """
    if not isinstance(bbytes, (int, float)) or bbytes < 0:
        raise ValueError("It must be an int or a float.")

    byte_in_gigabyte = 1024 ** 3
    gibibytes = bbytes / byte_in_gigabyte
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
        print(cmd)
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
    """ update virt host cert"""
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
    directory = os.path.dirname(filename)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    print_title("Guest Section")
    create_xml_config(filename, data)
    if verbose is True:
        xmlutil.show_from_xml(filename)
    validate_xml(filename)
    cfg_store.store_config()
    print_summary_ok("Guest XML Configuration is done")
    if not is_localhost(data.hypervisor_name):
        vm_image = data.STORAGE_DATA['path']+"/"+data.STORAGE_DATA['storage_name']+"."+data.STORAGE_DATA['format']
        print("\nYou should copy the XML configuration and the VM image to "+data.hypervisor_name+" host.")
        print(filename+"\n"+vm_image+"\n")

def find_ext_file(ext):
    """
    Show all extension files in current path
    """
    files_list = []
    for files in os.listdir('.'):
        if files.endswith(ext):
            files_list.append(files)
    return files_list

def create_xml_config(filename, data, disk=""):
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
    xml_all += data.name+data.memory+data.memory_backing+data.vcpu+data.osdef
    xml_all += data.security+data.features+data.cpumode+data.clock+data.hugepages
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
    # encryption needs uuid from VM image
    if data.STORAGE_DATA['encryption'] == "on":
        disk_file = data.STORAGE_DATA['path']+"/"+data.STORAGE_DATA['storage_name']+"."+data.STORAGE_DATA['format']
        disk_uuid = generate_secret_uuid(disk_file, data.STORAGE_DATA['password'])
        # update disk with encryption data
        xmlutil.add_encryption(filename, disk_uuid)

def create_from_template(finalfile, xml_all):
    """
    create the VM domain XML from all template input given
    """
    print_title("\nCreate The XML VM configuration")
    print(finalfile)
    with open(finalfile, 'w') as file_h:
        file_h.write(xml_all)

def generate_secret_uuid(image, password):
    """
    uuid
    virsh secret-define --xml "<secret ephemeral='no' private='yes'><uuid>your_secret_uuid</uuid><usage type='volume'><volume>/path/to/encrypted_disk.qcow2</volume></usage></secret>"
    virsh secret-set-value --secret your_secret_uuid --base64 "$(echo -n 'your_passphrase' | base64)"
    """
    check_secret_uuid(image)
    secret_uuid = str(uuid.uuid4())
    tmp_file = "/tmp/secret.xml"
    file = open(tmp_file, "w")
    file.write("<secret ephemeral='no' private='yes'>\n  <uuid>"+secret_uuid+"</uuid>\n  <usage type='volume'>\n  <volume>"+str(image)+"</volume>\n  </usage>\n</secret>")
    file.close()
    cmd_define_secret = "virsh secret-define --file "+tmp_file
    cmd_password = "virsh secret-set-value --secret "+secret_uuid+" $(echo -n '"+password+"' | base64)"
    run_command_with_except(cmd_define_secret)
    run_command_with_except(cmd_password)
    os.remove(tmp_file)
    return secret_uuid

def check_secret_uuid(image):
    hypervisor = hv.select_hypervisor()
    if not hypervisor.is_connected():
        print_error("No connection to LibVirt")
        return

    secrets = hypervisor.secret_list()
    # Check if the image path exists in the secrets
    for secret_name in secrets:
        secret = hypervisor.secret_lookup_by_uuid(secret_name)
        xml_desc = secret.XMLDesc(0)
        if image in xml_desc:
            print(f"Secret with image path {image} already exists. Undefining it")
            cmd_rm_uuid = "virsh secret-undefine "+secret_name
            print(cmd_rm_uuid)
            run_command_with_except(cmd_rm_uuid)

def get_qemu_img_uuid(image):
    """
    retrieve the uuid from the image
    """
    command = ["qemu-img", "info", "--output=json", image]
    output = subprocess.check_output(command).decode("utf-8")
    img_info = json.loads(output)
    return img_info['format-specific']['data']['encrypt']['uuid']

def get_machine_type(qemu):
      """
      get machine type from qemu
      """
      import re
      output = subprocess.check_output([qemu, "-machine", "help"])

      # convert the output to a string and extract the machine types using regular expressions
      output_str = output.decode("utf-8")
      machine_types = []
      for line in output_str.split("\n"):
          if line.startswith("Supported"):
              continue
          machine_type = re.match(r"^(\S+)", line)
          if machine_type:
              machine_types.append(machine_type.group(1))

      return machine_types

def check_name(name):
    """
    check the VM name is a alphnumeric+number only
    """
    return all(inputc.isalnum() for inputc in name)

def is_localhost(to_check):
    """
    check if setup is local or not
    """
    hostname = socket.gethostname()
    if to_check in ["localhost", hostname]:
        return True
    else:
        return False
