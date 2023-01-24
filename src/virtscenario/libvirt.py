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

import xml.etree.ElementTree as ET
import virtscenario.util as util

class FeatureNotSupported(BaseException):
    def __init(__self__):
        pass

class LibVirtDomInfo:
    """
    Wrapper around 'virsh domcapabilities' which parses the XML data and
    provides it via method calls to consumers.
    """
    def __init__(self):
        self.sev_info = {}
        self.loaders = []

    def _detect_sev(self, xmlroot):
        sev_info = {}
        sev_info['sev_supported'] = False
        sev_info['sev_es_supported'] = False
        sev_info['sev_cbitpos'] = None
        sev_info['sev_reduced_phys_bits'] = None
        try:
            feature_list = xmlroot.findall("./features/sev[@supported='yes']")
            if len(feature_list) == 0:
                raise FeatureNotSupported()

            # SEV is supported on this machine
            sev_info['sev_supported'] = True

            # Now check capabilites of SEV
            sev_features = feature_list[0]

            # Search for SEV-ES support
            max_es_guests = sev_features.findall("./maxESGuests")
            if len(max_es_guests) > 0:
                # libVirt claims SEV-ES support - check maximum number of guests is > 0
                es_guests = max_es_guests[0]
                num_guests = int(es_guests.text)
                if num_guests > 0:
                    sev_info['sev_es_supported'] = True

            # Get C-Bit Position
            cbitpos_list = sev_features.findall("./cbitpos")
            if len(cbitpos_list) == 0:
                raise SevNotSupported

            cbitpos = cbitpos_list[0]
            sev_info['sev_cbitpos'] = cbitpos.text

            # Get reducedPhysBits
            reduced_list = sev_features.findall("./reducedPhysBits")
            if len(reduced_list) == 0:
                raise SevNotSupported

            reduced_phys_bits = reduced_list[0]
            sev_info['sev_reduced_phys_bits'] = reduced_phys_bits.text
        except FeatureNotSupported:
            # Make sure to not report half-filled info
            sev_info = {}
            sev_info['sev_supported'] = False
            sev_info['sev_es_supported'] = False
            sev_info['sev_cbitpos'] = None
            sev_info['sev_reduced_phys_bits'] = None

        return sev_info

    def dom_features_detect(self):
        xmldata, errs = util.system_command("virsh domcapabilities")
        if errs:
            print(errs)
            return
        root = ET.fromstring(xmldata)

        self.sev_info = self._detect_sev(root)

    def features_sev(self):
        return self.sev_info

LIBVIRT_DOM_INFO = LibVirtDomInfo()

def init_dominfo():
    LIBVIRT_DOM_INFO.dom_features_detect()

def dominfo():
    return LIBVIRT_DOM_INFO
