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

"""
SEV Feature Detection
"""

from string import Template
import xml.etree.ElementTree as ET
import virtscenario.template as template
import virtscenario.util as util

"""
SEV Policy bits
"""
# Disable debug support
SEV_POLICY_NODBG    = 0x01
# Disable key sharing with other domains
SEV_POLICY_NOKS     = 0x02
# Enable encrypted state
SEV_POLICY_ES       = 0x04
# Migration via PSP is disallowed
SEV_POLICY_NOSEND   = 0x08
# The guest must not be transmitted to another platform that is not in the domain when set.
SEV_POLICY_DOMAIN   = 0x10
# The guest must not be transmitted to another platform that is not SEV capable when set.
SEV_POLICY_SEV      = 0x20

class SevNotSupported(BaseException):
    def __init(__self__):
        pass

class SevInfo:
    """
    AMD Secure Encrypted Virtualization (SEV) host feature detection
    This class is used to detect SEV host features like the CBIT position and
    SEV-ES availability.
    """
    def __init__(self):
        """
        Member initialization
        """
        self.sev_supported = False
        self.sev_es_supported = False
        self.sev_cbitpos = None
        self.sev_reduced_phys_bits = None

    def supported(self):
        return self.sev_supported

    def host_detect(self):
        """
        Detect SEV features from the 'virsh domcapabilities' XML outout
        """

        try:
            xmldata, errs = util.system_command("virsh domcapabilities")
            if errs:
                print(errs)
                return
            root = ET.fromstring(xmldata)
            feature_list = root.findall("./features/sev[@supported='yes']")
            if len(feature_list) == 0:
                raise SevNotSupported()

            # SEV is supported on this machine
            self.sev_supported = True

            # Now check capabilites of SEV
            sev_features = feature_list[0]

            # Search for SEV-ES support
            max_es_guests = sev_features.findall("./maxESGuests")
            if len(max_es_guests) > 0:
                # libVirt claims SEV-ES support - check maximum number of guests is > 0
                es_guests = max_es_guests[0]
                num_guests = int(es_guests.text)
                if num_guests > 0:
                    self.sev_es_supported = True

            # Get C-Bit Position
            cbitpos_list = sev_features.findall("./cbitpos")
            if len(cbitpos_list) == 0:
                raise SevNotSupported

            cbitpos = cbitpos_list[0]
            self.sev_cbitpos = cbitpos.text

            # Get reducedPhysBits
            reduced_list = sev_features.findall("./reducedPhysBits")
            if len(reduced_list) == 0:
                raise SevNotSupported

            reduced_phys_bits = reduced_list[0]
            self.sev_reduced_phys_bits = reduced_phys_bits.text

        except SevNotSupported:
            self.sev_supported = False
            self.sev_es_supported = False
            self.cbitpos = None
            self.reduced_phys_bits = None
            return False

        return True

    def get_xml(self):
        """
        Generate libVirt XML specification for SEV
        """
        if self.sev_supported == False:
            return '';

        policy = SEV_POLICY_NODBG + SEV_POLICY_NOKS + SEV_POLICY_DOMAIN + SEV_POLICY_SEV

        # Enable SEV-ES when supported
        if self.sev_es_supported:
            policy += SEV_POLICY_ES

        # Generate XML
        xml_template = template.SEV_TEMPLATE;
        xml_sev_data = {
            'cbitpos': self.sev_cbitpos,
            'reducedphysbits': self.sev_reduced_phys_bits,
            'policy': hex(policy),
        }

        return Template(xml_template).substitute(xml_sev_data)
