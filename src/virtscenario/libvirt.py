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

class FeatureNotSupported(BaseException):
    def __init(self):
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
        """
        detect sec cap
        """
        sev_info = {}
        sev_info['sev_supported'] = False
        sev_info['sev_es_supported'] = False
        sev_info['sev_cbitpos'] = None
        sev_info['sev_reduced_phys_bits'] = None
        try:
            feature_list = xmlroot.findall("./features/sev[@supported='yes']")
            if not feature_list:
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
            if not cbitpos_list:
                raise FeatureNotSupported()

            cbitpos = cbitpos_list[0]
            sev_info['sev_cbitpos'] = cbitpos.text

            # Get reducedPhysBits
            reduced_list = sev_features.findall("./reducedPhysBits")
            if not reduced_list:
                raise FeatureNotSupported()

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

    def _detect_loaders(self, xmlroot):
        """
        check loader
        """
        loaders = []

        loaders_list = xmlroot.findall("./os[@supported='yes']/loader[@supported='yes']/value")
        for loader in loaders_list:
            loaders.append(loader.text)

        return loaders

    def dom_features_detect(self, hypervisor):
        """
        detect dom capabilities on the hypervisor
        """
        xmldata = hypervisor.domain_capabilities()
        root = ET.fromstring(xmldata)

        self.sev_info = self._detect_sev(root)
        self.loaders = self._detect_loaders(root)

    def features_sev(self):
        """
        get SEV info
        """
        return self.sev_info

    def supported_firmware(self):
        """
        supported firmware
        """
        return self.loaders

    def firmware_supported(self, executable):
        """
        return supported firmware
        """
        for uload in self.loaders:
            if executable == uload:
                return True
        return False

def dominfo(hypervisor):
    """
    get dom info
    """
    info = LibVirtDomInfo()
    info.dom_features_detect(hypervisor)
    return info
