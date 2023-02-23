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
import virtscenario.template as template
import virtscenario.libvirt as libvirt

# SEV Policy bits
# Disable debug support
SEV_POLICY_NODBG = 0x01
# Disable key sharing with other domains
SEV_POLICY_NOKS = 0x02
# Enable encrypted state
SEV_POLICY_ES = 0x04
# Migration via PSP is disallowed
SEV_POLICY_NOSEND = 0x08
# The guest must not be transmitted to another platform that is not in the domain when set.
SEV_POLICY_DOMAIN = 0x10
# The guest must not be transmitted to another platform that is not SEV capable when set.
SEV_POLICY_SEV = 0x20

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
        self.cbitpos = None
        self.sev_reduced_phys_bits = None
        self.reduced_phys_bits = None

    def supported(self):
        """
        SEV is supported
        """
        return self.sev_supported

    def es_supported(self):
        return self.sev_es_supported

    def host_detect(self, hypervisor):
        """
        Detect SEV features from LibVirt domain capabilites
        """

        sev_info = libvirt.dominfo(hypervisor).features_sev()
        if sev_info['sev_supported'] == False:
            return False

        self.sev_supported = True
        self.sev_es_supported = sev_info['sev_es_supported']
        self.sev_cbitpos = sev_info['sev_cbitpos']
        self.sev_reduced_phys_bits = sev_info['sev_reduced_phys_bits']

        return True
    def get_policy(self):
        policy = SEV_POLICY_NODBG + SEV_POLICY_NOKS + SEV_POLICY_DOMAIN + SEV_POLICY_SEV

        # Enable SEV-ES when supported
        if self.sev_es_supported:
            policy += SEV_POLICY_ES

        return policy

    def get_xml(self):
        """
        Generate libVirt XML specification for SEV
        """
        # generate the xml config only if SEV is available
        if self.sev_supported is True:
            policy = self.get_policy()

            # Generate XML
            xml_template = template.SEV_TEMPLATE
            xml_sev_data = {
                'cbitpos': self.sev_cbitpos,
                'reducedphysbits': self.sev_reduced_phys_bits,
                'policy': hex(policy),
            }

            return Template(xml_template).substitute(xml_sev_data)
