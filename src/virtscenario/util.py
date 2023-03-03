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

def esc(code):
    """
    Better layout with some color
    """
    # foreground: 31:red 32:green 34:blue 36:cyan
    # background: 41:red 44:blue 107:white
    # 0:reset
    return f'\033[{code}m'

def print_error(text):
    """
    Print error in red
    """
    formated_text = esc('31;1;1')+text+esc(0)
    print(formated_text)

def print_warning(text):
    """
    Print warning in red
    """
    formated_text = "\n     "+esc('31;1;1') +text.upper()+esc(0)+"\n"
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

def print_ok(text):
    """
    Print ok in green
    """
    formated_text = esc('32;1;1')+text+esc(0)
    print(formated_text)

def print_title(text):
    """
    Print title with blue background
    """
    formated_text = "\n"+esc('104;1;1')+text+esc(0)
    print(formated_text)

def print_summary(text):
    """
    Print title with magenta background
    """
    formated_text = esc('45;1;1')+text.upper()+esc(0)
    print(formated_text)

def print_summary_ok(text):
    """
    Print title with green background
    """
    formated_text = esc('42;1;1')+text+esc(0)+"\n#######################\n"
    print(formated_text)

def print_data(data, value):
    """
    Print the data
    """
    formated_text = "\n"+esc('101;1;1')+data+" "+esc(0)+" "+value.rstrip()
    print(formated_text.strip())

def generate_mac_address():
    """
    generate a mac address
    """
    import string
    import random
    HEX_DIGITS = string.hexdigits.upper()
    PREFIX_DIGITS = "02468ACE"

    octets = []
    for i in range(6):
        if i == 0:
            octets.append(random.choice(PREFIX_DIGITS))
        else:
            octets.append(''.join(random.choices(HEX_DIGITS, k=2)))

    mac_address = ':'.join([octet for octet in octets])
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

def validate_yaml_file(file):
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
