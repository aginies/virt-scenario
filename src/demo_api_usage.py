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
This is a demo how to use the virt-scenario API in your own script
"""

import virtscenario.configuration as configuration
import virtscenario.scenario as scena
# not needed if you don't use extra
import virtscenario.util as util

def main():
    ## init config
    config = configuration.Configuration()
    self = config
    ## preload scenario config: computation, desktop, secure
    preload = scena.Scenarios.pre_computation(config, "VMname")
    #preload = scena.Scenarios.pre_desktop(config, "VMname")
    #preload = scena.Scenarios.pre_secure_vm(config, "VMname")
    ## self.conf
    self.conf = preload
    # find the virtscenario and hyperviror config file
    # you can also provide the configuration path, see below
    self.conf.conffile = configuration.find_conffile()
    self.conf.hvfile = configuration.find_hvfile()

    # Mode: (experimental)
    # - guest: only XML guest configuration
    # - host: only host configuration
    # - both should be done (default)
    self.conf.mode = "both"

    ## setting up some user parameter
    # Force overwrite any previous config
    self.conf.dataprompt.update({'overwrite': "on"})
    # Select the yaml configuration file
    #self.conf.dataprompt.update({'mainconf': "/path/to/mainconf"})
    # Load Hypervisor configuration
    #self.conf.dataprompt.update({'hvconf': "/path/to/hvconf"})
    # VM name
    self.conf.dataprompt.update({'name': "YOURVMNAME"})
    # Number of CPU, int
    self.conf.dataprompt.update({'vcpu': 6})
    # Memory in GiB
    self.conf.dataprompt.update({'memory': 4}) 
    ## Storage
    self.conf.dataprompt.update({'cluster_size': 1024})
    self.conf.dataprompt.update({'preallocation': "metadata"})
    self.conf.dataprompt.update({'encryption': "off"})
    self.conf.dataprompt.update({'disk_cache': "none"})
    self.conf.dataprompt.update({'lazy_refcounts': "off"})
    self.conf.dataprompt.update({'disk_target': "vdb"})
    self.conf.dataprompt.update({'capacity': 8})
    # Installation media
    self.conf.dataprompt.update({'dvd': "/path/to/dvd"})
    # Select an VM image to use
    self.conf.dataprompt.update({'vmimage': "/path/to/vmimage"})
    # Machine Type
    self.conf.dataprompt.update({'machine': "q35"})
    # Boot device
    self.conf.dataprompt.update({'boot_dev': "hd"})
    # Virtual Network to use
    self.conf.dataprompt.update({'vnet': "default"})
    # Set hypervisor for which VMs are configured
    #self.conf.dataprompt.update({'hvselected': "localhost"})
    # Force the extract of a localhost PDH file
    # only available for securevm scenario
    #self.conf.dataprompt.update({'force_sev': "off"})

    ## do the scenario: "data, Verbose"
    scena.Scenarios.do_computation(preload, True)
    #scena.Scenarios.do_desktop(preload, True)
    #scena.Scenarios.do_securevm(preload, True)

    ## extra
    # function to show difference between recomendation and user settings
    if self.nothing_to_report is False:
        util.to_report(self.toreport, self.conf.conffile)
    # show how to use it
    util.show_how_to_use(self.conf.callsign)

main()
