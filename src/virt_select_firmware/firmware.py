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
firmware functions
"""

import json
import os

FIRMWARE_META_BASE_DIR = "/usr/share/qemu/firmware/"

class Firmware:
    """
    firmware class
    """
    def __init__(self):
        """
        Set default values
        """
        self.executable = None
        self.nvram_template = None
        self.architectures = []
        self.features = []
        self.interfaces = []

    def load_from_json(self, jsondata):
        """
        Initialize object from a json firmware description
        """
        if "interface-types" in jsondata:
            self.interfaces = jsondata['interface-types']
        else:
            return False

        if 'mapping' in jsondata:
            if 'executable' in jsondata['mapping'] and 'filename' in jsondata['mapping']['executable']:
                self.executable = jsondata['mapping']['executable']['filename']
            elif 'filename' in jsondata['mapping']:
                self.executable = jsondata['mapping']['filename']
            if 'nvram-template' in jsondata['mapping'] and 'filename' in jsondata['mapping']['nvram-template']:
                self.nvram_template = jsondata['mapping']['nvram-template']['filename']

        if self.executable is None:
            return False

        if 'features' in jsondata:
            for feat in jsondata['features']:
                self.features.append(feat)

        if 'targets' in jsondata:
            for target in jsondata['targets']:
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
        for arch in self.architectures:
            print("    " + arch)
        print("  Features:")
        for feat in self.features:
            print("    " + feat)

        return True

    def match(self, arch, features=[], interface='uefi'):
        """
        Check if this firmware supports a given architecture and feature set
        """
        if self.executable is None:
            return False

        matches_interface = False
        for inter in self.interfaces:
            if inter == interface:
                matches_interface = True
                break

        matches_arch = False
        for sarch in self.architectures:
            if sarch == arch:
                matches_arch = True
                break

        matches_features = True
        for feat1 in features:
            match_this = False
            for feat2 in self.features:
                if feat1 == feat2:
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
    firmwares = []
    for file in os.listdir(path):
        _, ext = os.path.splitext(file)
        if ext != '.json':
            continue
        try:
            ffile = open(FIRMWARE_META_BASE_DIR + file)
            data = json.load(ffile)
            ffile.close()
            firmw = Firmware()
            if firmw.load_from_json(data):
                firmwares.append(firmw)
        except ValueError:
            print("Error parsing {}".format(file))

    return firmwares
