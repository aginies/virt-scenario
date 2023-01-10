#!/usr/bin/env python3
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

def system_command(cmd):
    """
    Launch a system command
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=2)
    out = str(out, 'UTF-8')
    return out, errs

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
    formated_text = esc('31;1;1') +text +esc(0)
    print(formated_text)

def print_ok(text):
    """
    Print ok in green
    """
    formated_text = esc('32;1;1') +text +esc(0)
    print(formated_text)

def print_title(text):
    """
    Print title with blue background
    """
    formated_text = "\n"+esc('104;1;1') +text +esc(0)
    print(formated_text)

def print_summary(text):
    """
    Print title with magenta background
    """
    formated_text = "\n"+esc('45;1;1') +text +esc(0)
    print(formated_text)

def print_summary_ok(text):
    """
    Print title with green background
    """
    formated_text = "\n"+esc('42;1;1') +text +esc(0)
    print(formated_text)

def print_data(data, value):
    """
    Print the data
    """
    formated_text = "\n"+esc('101;1;1')+data+" "+esc(0)+" "+value.rstrip()
    print(formated_text.strip())

def macaddress():
    """
    generate a mac address
    """
    import string
    import random
    uppercased_hexdigits = ''.join(set(string.hexdigits.upper()))
    mac = ""
    j = 0
    for i in range(6):
        while j < 2:
            if i == 0:
                mac += random.choice("02468ACE")
            else:
                mac += random.choice(uppercased_hexdigits)
            j += 1
        mac += ":"
        j = 0
    finalmac = mac.strip(":")
    return finalmac

def bytes_to_gb(bytes):
    """
    convert bytes to Gib
    """
    gib = bytes/(1024*1024*1024)
    gib = round(gib, 2)
    return gib
