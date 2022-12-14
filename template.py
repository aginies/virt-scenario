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
    <uuid>${uuid}</uuid>
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
  <name>${name}</name>
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
