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

import json
import os

FIRMWARE_META_BASE_DIR="/usr/share/qemu/firmware/"

class Firmware:
    def __init__(self):
        """
        Set default values
        """
        self.executable = None
        self.nvram_template = None
        self.architectures = []
        self.features = []
        self.interfaces = []

    def load_from_json(self, json):
        """
        Initialize object from a json firmware description
        """
        if "interface-types" in json:
            self.interfaces = json['interface-types']
        else:
            return False

        if 'mapping' in json:
            if 'executable' in json['mapping'] and 'filename' in json['mapping']['executable']:
                self.executable = json['mapping']['executable']['filename']
            elif 'filename' in json['mapping']:
                self.executable = json['mapping']['filename']
            if 'nvram-template' in json['mapping'] and 'filename' in json['mapping']['nvram-template']:
                self.nvram_template = json['mapping']['nvram-template']['filename']

        if self.executable == None:
            return False

        if 'features' in json:
            for f in json['features']:
                self.features.append(f)

        if 'targets' in json:
            for target in json['targets']:
                self.architectures.append(target['architecture'])

        if len(self.architectures) == 0:
            return False

        return True

    def print(self):
        """
        Print object for debugging
        """
        print("Firmware: {}".format(self.executable))
        print("  NV-RAM: {}".format(self.nvram_template))
        print("  Architectures:")
        for s in self.architectures:
            print("    " + s)
        print("  Features:")
        for s in self.features:
            print("    " + s)

        return True

    def match(self, arch, features=[], interface='uefi'):
        """
        Check if this firmware supports a given architecture and feature set
        """
        if self.executable is None:
            return False

        matches_interface = False
        for i in self.interfaces:
            if i == interface:
                matches_interface = True
                break

        matches_arch = False;
        for a in self.architectures:
            if a == arch:
                matches_arch = True
                break

        matches_features = True
        for f1 in features:
            match_this = False
            for f2 in self.features:
                if f1 == f2:
                    match_this = True
                    break
            matches_features = match_this
            if not matches_features:
                break

        return matches_interface and matches_arch and matches_features

def load_firmware_info(path=FIRMWARE_META_BASE_DIR):
    """
    Parse the firmware description JSON files
    """
    firmwares = [];
    for fn in os.listdir(path):
        name, ext = os.path.splitext(fn)
        if ext != '.json':
            continue
        try:
            f = open(FIRMWARE_META_BASE_DIR + fn)
            data = json.load(f)
            f.close()
            fw = Firmware()
            if fw.load_from_json(data):
                firmwares.append(fw)
        except ValueError:
            print("Error parsing {}".format(fn))

    return firmwares
