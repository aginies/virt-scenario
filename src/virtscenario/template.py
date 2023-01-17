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
libvirt template definition
"""

NETWORK_TEMPLATE = """<network>
    <name>${network_name}</name>
    <uuid>${network_uuid}</uuid>
    <forward mode='nat'>
        <nat>
            <port start='1024' end='65535'/>
        </nat>
    </forward>
    <bridge name='${bridge}' stp='${stp}' delay='0'/>
    <ip address='${ip}' netmask='${netmask}'>
        <dhcp>
            <range start='${dhcp_start}' end='${dhcp_end}'/>
        </dhcp>
    </ip>
</network>"""

# External creation of XML storage (not in XML guest config)
STORAGE_TEMPLATE = """<volume>
  <name>${storage_name}</name>
  <allocation>${allocation}</allocation>
  <capacity unit='${unit}'>${capacity}</capacity>
  <target>
  <path>${path}</path>
    <permissions>
      <owner>${owner}</owner>
      <group>${group}</group>
      <mode>${mode}</mode>
      <label>${label}</label>
    </permissions>
  </target>
</volume>"""

NAME_TEMPLATE = """
  <name>${VM_name}</name>
  <uuid>${VM_uuid}</uuid>"""

METADATA_TEMPLATE = """
  <metadata>
    <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
      <libosinfo:os id="http://suse.com/sles/12.3"/>
    </libosinfo:libosinfo>
  </metadata>"""

MEMORY_TEMPLATE = """
  <memory unit='${mem_unit}'>${max_memory}</memory>
  <currentMemory unit='${current_mem_unit}'>${memory}</currentMemory>"""

CPU_TEMPLATE = """
  <vcpu placement='static'>${vcpu}</vcpu>"""

OS_TEMPLATE = """
  <os>
    <type arch='${arch}' machine='${machine}'>hvm</type>
    <boot dev='${boot_dev}'/>
  </os>"""

# virt-install --features help
FEATURES_TEMPLATE = """
  <features>
     ${features}
  </features>"""

CPUMODE_PASS_TEMPLATE = """
  <cpu mode='host-passthrough' check='none' migratable='${migratable}'>
    <cache mode='passthrough'/>${extra}
  </cpu>"""

CLOCK_TEMPLATE = """
  <clock offset='${clock_offset}'>
    ${clock}
  </clock>"""

ON_TEMPLATE = """
  <on_poweroff>${on_poweroff}</on_poweroff>
  <on_reboot>${on_reboot}</on_reboot>
  <on_crash>${on_crash}</on_crash>"""

POWER_TEMPLATE = """
  <pm>
    <suspend-to-mem enabled='${suspend_to_mem}'/>
    <suspend-to-disk enabled='${suspend_to_disk}'/>
  </pm>"""

IOTHREADS_TEMPLATE = """
   <iothreads>${iothreads}</iothreads>"""

# <devices>
EMULATOR_TEMPLATE = """
    <emulator>${emulator}</emulator>"""

DISK_TEMPLATE = """
    <disk type='${disk_type}' device='disk'>
      <driver name='qemu' type='${format}' cache='${disk_cache}'/>
      <source file='${source_file}'/>
      <target dev='${disk_target}' bus='${disk_bus}'/>
      <!--<address type='pci' domain='0x0000' bus='0x06' slot='0x00' function='0x0'/>-->
    </disk>"""

INTERFACE_TEMPLATE = """
    <interface type='network'>
      <mac address='${mac_address}'/>
      <source network='${network}'/>
      <model type='${type}'/>
      <!--<address type='pci' domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>-->
    </interface>"""

CONSOLE_TEMPLATE = """
    <console type='pty'>
      <target type='virtio' port='0'/>
    </console>"""

CHANNEL_TEMPLATE = """
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>"""

INPUT_TEMPLATE = """
    <input type='${type}' bus='${bus}'/>"""

GRAPHICS_TEMPLATE = """
    <graphics type='vnc' port='-1' autoport='yes' keymap='fr'>
      <listen type='address'/>
    </graphics>"""

AUDIO_TEMPLATE = """
    <sound model='${model}'/>"""

VIDEO_TEMPLATE = """
    <video>
      <model type='${type}' ram='65536' vram='65536' vgamem='16384' heads='1' primary='yes'/>
      <!--<address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>-->
    </video>"""

VIDEO_VIRTIO_TEMPLATE = """
    <video>
      <model type='virtio' heads='1' primary='yes'/>
      <!--<address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>-->
      <driver iommu='on'/>
    </video>"""

WATCHDOG_TEMPLATE = """
    <watchdog model='${model}' action='${action}'>
      <!--<address type='pci' domain='0x0000' bus='0x10' slot='0x00' function='0x0'/>-->
    </watchdog>"""

MEMBALLOON_TEMPLATE = """
    <memballoon model='virtio'>
      <!--<address type='pci' domain='0x0000' bus='0x09' slot='0x00' function='0x0'/>-->
      <driver iommu='on'/>
    </memballoon>"""

RNG_TEMPLATE = """
    <rng model='virtio'>
      <backend model='random'>/dev/urandom</backend>
      <driver iommu='on'/>
      <!--<address type='pci' domain='0x0000' bus='0x0a' slot='0x00' function='0x0'/>-->
    </rng>"""

USB_TEMPLATE = """
    <controller type='usb' index='0' model='${model}'>
      <!--<address type='pci' domain='0x0000' bus='0x03' slot='0x1d' function='0x7'/>-->
    </controller>"""

TPM_TEMPLATE = """
    <tpm model="${tpm_model}">
      <backend type="${tpm_type}">
      <device path="${device_path}"/>
      </backend>
    </tpm>"""

TPM_TEMPLATE_EMULATED = """
    <tpm model="${tpm_model}">
      <backend type="${tpm_type}" version="${version}"/>
    </tpm>"""

SECURITY_TEMPLATE = """
  <launchSecurity type='${sectype}'>
    ${secdata}
  </launchSecurity>"""

CONTROLLER_SATA = """
    <controller type="sata" index="0">
      <address type="pci" domain="0x0000" bus="0x00" slot="0x1f" function="0x2"/>
    </controller>"""

CONTROLLER_IDE = """
    <controller type="ide" index="0">
      <address type="pci" domain="0x0000" bus="0x00" slot="0x01" function="0x1"/>
    </controller>"""

CONTROLLER_Q35_TEMPLATE = """
    <controller type="pci" index="0" model="pcie-root"/>
    <controller type="pci" index="1" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="1" port="0x10"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x0" multifunction="on"/>
    </controller>
    <controller type="pci" index="2" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="2" port="0x11"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x1"/>
    </controller>
    <controller type="pci" index="3" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="3" port="0x12"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x2"/>
    </controller>
    <controller type="pci" index="4" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="4" port="0x13"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x3"/>
    </controller>
    <controller type="pci" index="5" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="5" port="0x14"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x4"/>
    </controller>
    <controller type="pci" index="6" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="6" port="0x15"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x5"/>
    </controller>
    <controller type="pci" index="7" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="7" port="0x16"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x6"/>
    </controller>
    <controller type="pci" index="8" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="8" port="0x17"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x7"/>
    </controller>
    <controller type="pci" index="9" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="9" port="0x18"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x0" multifunction="on"/>
    </controller>
    <controller type="pci" index="10" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="10" port="0x19"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x1"/>
    </controller>
    <controller type="pci" index="11" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="11" port="0x1a"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x2"/>
    </controller>
    <controller type="pci" index="12" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="12" port="0x1b"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x3"/>
    </controller>
    <controller type="pci" index="13" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="13" port="0x1c"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x4"/>
    </controller>
    <controller type="pci" index="14" model="pcie-root-port">
      <model name="pcie-root-port"/>
      <target chassis="14" port="0x1d"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x5"/>
    </controller>"""

CONTROLLER_PC_TEMPLATE = """
    <controller type="pci" index="0" model="pci-root"/>"""
# END  </devices>
