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
Scenario definition
"""

class Scenario:
    """
    Scenario
    """
    def name(self, name):
        self.NAME_DATA = {
            'VM_name': name,
        }
        return self.NAME_DATA
        
    def cpu(self, number):
        self.CPU_DATA = {
            'vcpu': number,
        }
        return self.CPU_DATA

    def cpu_perf():
        """
        cpu perf
        """

    def storage_perf():
        """
        storage performance
        """

    def video_perf():
        """
        video performance
        """

    def network_perf():
        """
        network performance
        """

    def host_hardware():
        """
        host hardware
        """

    def easy_migration():
        """
        easy migration
        """

    def computation():
        """
        computation
        """

    def access_host_fs():
        """
        access host filesystem
        """

    def testing_os():
        """
        testing an OS
        """

    def secure_vm():
        """
        secure VM
        """

    def soft_rt_vm():
        """
        soft Real Time VM
        """
