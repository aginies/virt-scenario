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
  <uuid>${VM_uuid}</uuid>
"""

METADATA_TEMPLATE = """
  <metadata>
    <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
      <libosinfo:os id="http://suse.com/sles/12.3"/>
    </libosinfo:libosinfo>
  </metadata>
"""

MEMORY_TEMPLATE = """
  <memory unit='${mem_unit}'>${max_memory}</memory>
  <currentMemory unit='${current_mem_unit}'>${memory}</currentMemory>
"""

CPU_TEMPLATE = """
  <vcpu placement='static'>${vcpu}</vcpu>
"""

OS_TEMPLATE = """
  <os>
    <type arch='${arch}' machine='${machine}'>hvm</type>
    <boot dev='${boot_dev}'/>
  </os>
"""

# virt-install --features help
FEATURES_TEMPLATE = """
  <features>
     ${features}
  </features>
"""

CPUMODE_TEMPLATE = """
  <cpu mode='${cpu_mode}' check='none' migratable='${migratable}'/>
"""

CLOCK_TEMPLATE = """
  <clock offset='${clock_offset}'>
    ${clock}
  </clock>
"""

ON_TEMPLATE = """
  <on_poweroff>${on_poweroff}</on_poweroff>
  <on_reboot>${on_reboot}</on_reboot>
  <on_crash>${on_crash}</on_crash>
"""

POWER_TEMPLATE = """
  <pm>
    <suspend-to-mem enabled='${suspend_to_mem}'/>
    <suspend-to-disk enabled='${suspend_to_disk}'/>
  </pm>
"""

# <devices>

EMULATOR_TEMPLATE = """
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
"""

DISK_TEMPLATE = """
    <disk type='file' device='disk'>
      <driver name='qemu' type='${disk_type}' cache='${disk_cache}'/>
      <source file='${source_file}'/>
      <target dev='${disk_target}' bus='${disk_bus}'/>
      <address type='pci' domain='0x0000' bus='0x06' slot='0x00' function='0x0'/>
    </disk>
"""

INTERFACE_TEMPLATE = """
    <interface type='network'>
      <mac address='02:30:81:12:ba:29'/>
      <source network='slehpcsp3'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
    </interface>
"""

CONSOLE_TEMPLATE = """
    <console type='pty'>
      <target type='virtio' port='0'/>
    </console>
"""

CHANNEL_TEMPLATE = """
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
"""

INPUT_TEMPLATE = """
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
"""

GRAPHICS_TEMPLATE = """
    <graphics type='vnc' port='-1' autoport='yes' keymap='fr'>
      <listen type='address'/>
    </graphics>
"""

AUDIO_TEMPLATE = """
    <audio id='1' type='none'/>
"""

VIDEO_TEMPLATE = """
    <video>
      <model type='virtio' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x0'/>
    </video>
"""

WATCHDOG_TEMPLATE = """
    <watchdog model='i6300esb' action='poweroff'>
      <address type='pci' domain='0x0000' bus='0x10' slot='0x01' function='0x0'/>
    </watchdog>
"""

MEMBALLOON_TEMPLATE = """
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x09' slot='0x00' function='0x0'/>
    </memballoon>
"""

RNG_TEMPLATE = """
    <rng model='virtio'>
      <backend model='random'>/dev/urandom</backend>
      <address type='pci' domain='0x0000' bus='0x0a' slot='0x00' function='0x0'/>
    </rng>
"""

# END  </devices>
