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

def print_title(text):
    """
    Print title with blue background
    """
    formated_text = "\n"+esc('bg_blue')+text+esc('reset')
    print(formated_text)

def print_summary(text):
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

def bytes_to_gibibytes(bytes):
    """
    Convert bytes to gibibytes.
    """
    if not isinstance(bytes, (int, float)) or bytes < 0:
        raise ValueError("It must be an int or a float.")

    BYTES_IN_GIBIBYTE = 1024 ** 3
    gibibytes = bytes / BYTES_IN_GIBIBYTE
    return round(gibibytes, 2)

def validate_yaml_file(file_path):
    """
    validate the yaml file
    """
    try:
        with open(file_path, 'r') as stream:
            yaml_contents = yaml.safe_load(stream)
    except FileNotFoundError:
        raise ValueError(f"file {file_path} not found.")
    except yaml.YAMLError as exc:
        raise ValueError(f"Error while parsing the YAML file: {exc}")

    if not isinstance(yaml_contents, dict):
        raise ValueError("File should contain a dict.")

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
        print("     Overwrite are from "+conffile+"\n")
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
