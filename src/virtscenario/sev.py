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

import os

from string import Template
import virtscenario.template as template
import virtscenario.libvirt as libvirt
import virtscenario.util as util

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
        self.session_key = None
        self.dh_param = None

    def supported(self):
        """
        SEV is supported
        """
        return self.sev_supported

    def es_supported(self):
        """
        es is supported
        """
        return self.sev_es_supported

    def host_detect(self, hypervisor):
        """
        Detect SEV features from LibVirt domain capabilites
        """

        sev_info = libvirt.dominfo(hypervisor).features_sev()
        if sev_info['sev_supported'] is False:
            return False

        self.sev_supported = True
        self.sev_es_supported = sev_info['sev_es_supported']
        self.sev_cbitpos = sev_info['sev_cbitpos']
        self.sev_reduced_phys_bits = sev_info['sev_reduced_phys_bits']

        return True

    def get_policy(self):
        """
        get sev policy
        """
        policy = SEV_POLICY_NODBG + SEV_POLICY_NOKS + SEV_POLICY_DOMAIN + SEV_POLICY_SEV

        # Enable SEV-ES when supported
        if self.sev_es_supported:
            policy += SEV_POLICY_ES

        return policy

    def set_attestation(self, session, dh_param):
        """
        deal with attestaion (guest)
        """
        self.session_key = session
        self.dh_param = dh_param

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

            xml = Template(xml_template).substitute(xml_sev_data)

            if self.session_key is not None and self.dh_param is not None:
                xml_attestation_template = template.SEV_ATTESTATION_TEMPLATE
                xml_sev_attestation_data = {
                    'session_key': self.session_key,
                    'dhcert': self.dh_param,
                }
                xml += Template(xml_attestation_template).substitute(xml_sev_attestation_data)

        return xml

def sev_extract_pdh(cfg_store, certfile):
    """
    extract the PDH
    The PDH is used to negotiate a master secret between the SEV firmware and external entities
    """
    if util.cmd_exists("sevctl") is False:
        util.print_error("Please install sevctl tool")
        return

    target_path = cfg_store.get_path()
    cmd = "cd "+target_path+";sevctl export --full "+certfile
    out, errs = util.system_command(cmd)
    if errs:
        print(str(errs)+" "+str(out))
    print(cmd)
    print(out)

def sev_validate_pdh(cfg_store, certfile):
    """
    guest owner should validate the PDH integrity
    """
    target_path = cfg_store.get_path()
    cmd = "sevctl verify --sev "+target_path+"/"+certfile
    out, errs = util.system_command(cmd)
    if errs:
        print(str(errs)+" "+str(out))
    print(cmd)
    print(out)

def sev_prepare_attestation(cfg_store, policy, certfile):
    """
    prepare the SEV attestation
    """
    target_path = cfg_store.get_path()
    cmd = "cd {}; sevctl session --name '{}' {} {}".format(target_path, 'tmp', certfile, policy)
    output, errors = util.system_command(cmd)
    if errors:
        print(errors)
        return False
    print(output)

    files = {
        'tik': "tmp_tik.bin",
        'tek': "tmp_tek.bin",
        'godh': "tmp_godh.b64",
        'session': "tmp_session.b64"
    }

    for key, filename in files.items():
        if os.path.isfile(target_path + "/" + filename):
            new_name = target_path + "/" + key + ".bin"
            os.rename(target_path + "/" + filename, new_name)
        else:
            return False

    return True

def sev_load_session_key(cfg_store):
    """
    load the sev session key
    """
    filename = cfg_store.get_path() + "/session.bin"
    data = ""
    with open(filename, 'r') as filed:
        data = filed.read()
    return data

def sev_load_dh_params(cfg_store):
    """
    load the sev dh param
    """
    filename = cfg_store.get_path() + "/godh.bin"
    data = ""
    with open(filename, 'r') as filed:
        data = filed.read()
    return data
