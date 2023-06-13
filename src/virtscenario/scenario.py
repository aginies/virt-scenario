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

import virtscenario.dict as c
import virtscenario.configuration as configuration
import virtscenario.features as f
import virtscenario.hypervisors as hv
import virtscenario.guest as guest
import virtscenario.util as util
import virtscenario.configstore as configstore
import virtscenario.firmware as fw
import virtscenario.host as host
import virtscenario.sev as sev

class Scenarios():
    """
    Scenarios class
    This class is used to create all the configuration needed calling feature's class
    WARNING:
    vcpu, memory, machine can be overwritten by user setting
    """
    def __init__(self):
        self.name = None
        self.vcpu = None
        self.memory = None
        self.memory_backing = None
        self.cpumode = None
        self.callsign = None
        self.power = None
        self.osdef = None
        self.ondef = None
        self.watchdog = None
        self.storage = None
        self.disk = None
        self.network = None
        self.memory = None
        self.tpm = None
        self.audio = None
        self.features = None
        self.clock = None
        self.iothreads = None
        self.access_host_fs = None
        self.video = None
        self.usb = None
        self.security = None
        self.inputkeyboard = None
        self.inputmouse = None

    def pre_computation(self, name):
        """
        computation
        need cpu, memory, storage perf
        """
        if name is None:
            name = "computation"

        # BasicConfiguration definition
        self.name = c.BasicConfiguration.name(self, name)
        self.osdef = c.BasicConfiguration.osdef(self, "x86_64", "pc-q35-6.2", "hd")
        self.watchdog = c.BasicConfiguration.watchdog(self, "i6300esb", "poweroff")
        self.ondef = c.BasicConfiguration.ondef(self, "restart", "restart", "restart")
        self.features = c.BasicConfiguration.features(self, "<acpi/><apic/>")
        self.iothreads = c.BasicConfiguration.iothreads(self, "4")
        self.video = c.BasicConfiguration.video(self, "qxl")
        # Set some expected features
        f.Features.cpu_perf(self)
        f.Features.features_perf(self)
        f.Features.memory_perf(self)
        f.Features.storage_perf(self)
        f.Features.network_perf(self)
        f.Features.clock_perf(self)

        # prefiled storage
        STORAGE_DATA_REC = {}
        STORAGE_DATA_REC['preallocation'] = "off"
        STORAGE_DATA_REC['encryption'] = "off"
        STORAGE_DATA_REC['disk_cache'] = "unsafe"
        STORAGE_DATA_REC['lazy_refcounts'] = "on"
        STORAGE_DATA_REC['format'] = "raw"
        self.STORAGE_DATA_REC = STORAGE_DATA_REC

        return self

    def do_computation(self, verbose):
        """
        Will prepare the System for a Computation VM
        """
        if configuration.check_conffile(self.conf.conffile) is not False:
            configuration.Configuration.basic_config(self)

            hypervisor = hv.select_hypervisor()
            hypervisor.name = self.hypervisor_name
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            name = self.conf.dataprompt.get('name')

            # computation setup
            scenario = Scenarios()
            computation = scenario.pre_computation(name)

            self.callsign = computation.name['VM_name']
            self.name = guest.create_name(computation.name)

            # Configure VM without pinned memory
            configuration.Configuration.set_memory_pin(self, False)
            computation.memory_pin = False

            self.CONSOLE = configuration.Configuration.CONSOLE
            self.CHANNEL = configuration.Configuration.CHANNEL
            self.GRAPHICS = configuration.Configuration.GRAPHICS
            self.RNG = configuration.Configuration.RNG

            self.cpumode = guest.create_cpumode_pass(computation.cpumode)
            self.power = guest.create_power(computation.power)
            self.ondef = guest.create_ondef(computation.ondef)
            self.watchdog = guest.create_watchdog(computation.watchdog)
            self.network = guest.create_interface(computation.network)
            self.features = guest.create_features(computation.features)
            self.clock = guest.create_clock(computation.clock)
            self.video = guest.create_video(computation.video)
            self.iothreads = guest.create_iothreads(computation.iothreads)
            self.controller = guest.create_controller(self.conf.listosdef)
            self.vcpu = guest.create_cpu(computation.vcpu)
            self.memory = guest.create_memory(computation.memory)
            self.memory_backing = guest.create_memory_backing()
            self.osdef = guest.create_osdef(computation.osdef)

            self.custom = ["vnet"]
            fw_features = ['secure-boot']
            firmware = fw.find_firmware(self.fw_info, arch=self.conf.listosdef['arch'], features=fw_features, interface='uefi')
            if firmware:
                self.custom = ["loader", "vnet"]
                self.loader = firmware

            # Check user setting
            configuration.Configuration.check_user_settings(self, computation)

            cfg_store = configstore.create_config_store(self, computation, hypervisor, self.conf.overwrite)
            if cfg_store is None:
                util.print_error("No config store found...")
                return

            # recommended setting for storage
            self.STORAGE_DATA_REC = computation.STORAGE_DATA_REC
            self.STORAGE_DATA_REC['path'] = self.conf.diskpath['path']
            self.STORAGE_DATA['storage_name'] = self.callsign

            configuration.Configuration.check_storage(self)

            # XML File path
            self.filename = cfg_store.get_domain_config_filename()

            self.disk = guest.create_xml_disk(self.STORAGE_DATA)

            # transparent hugepages doesnt need any XML config
            self.hugepages = ""

            if self.conf.overwrite == "on":
                # remove previous domain in the hypervisor
                hypervisor.remove_domain(self.callsign)


            if (self.conf.mode != "guest" or self.conf.mode == "both") and util.check_iam_root() is True:
                util.print_title("Host Section")
                # Create the Virtual Disk image
                if self.conf.vmimage is None:
                    host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                host.transparent_hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("enable", "disable")
                host.swappiness("0")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                host.host_end()

            if self.conf.mode != "host" or self.conf.mode == "both":

                util.final_step_guest(cfg_store, self, verbose)
        else:
            util.print_error("configuration.check_conffile(conf) is True")

    def pre_desktop(self, name):
        """
        desktop
        """
        if name is None:
            name = "desktop"

        # BasicConfiguration definition
        self.name = c.BasicConfiguration.name(self, name)
        self.osdef = c.BasicConfiguration.osdef(self, "x86_64", "pc-q35-6.2", "hd")
        self.ondef = c.BasicConfiguration.ondef(self, "destroy", "restart", "destroy")
        self.audio = c.BasicConfiguration.audio(self, "ac97")
        self.usb = c.BasicConfiguration.usb(self, "qemu-xhci")
        self.tpm = c.ComplexConfiguration.tpm(self, "tpm-crb", "passthrough", "/dev/tpm0")
        #self.access_host_fs = ComplexConfiguration.access_host_fs(self, "plop")
        # memory
        unit = f.MemoryUnit("Gib", "Gib")
        self.memory = c.BasicConfiguration.memory(self, unit, "4", "4")
        # vcpu
        self.vcpu = c.BasicConfiguration.vcpu(self, "4")

        self.cpumode = c.BasicConfiguration.cpumode_pass(self, "on", "")
        self.power = c.BasicConfiguration.power(self, "yes", "yes")
        # Disk
        #diskdata = f.Disk("file", "none", "vda", "virtio", "/tmp", self.name['VM_name'], "qcow2")
        #self.disk = c.ComplexConfiguration.disk(self, diskdata)

        self.iothreads = c.BasicConfiguration.iothreads(self, "4")
        # network
        macaddress = util.generate_mac_address()
        self.network = c.ComplexConfiguration.network(self, macaddress, "default", "e1000")

        # Set some expected features
        f.Features.features_perf(self)
        f.Features.clock_perf(self)
        f.Features.video_perf(self)

        # prefiled storage
        STORAGE_DATA_REC = {}
        STORAGE_DATA_REC['preallocation'] = "metadata"
        STORAGE_DATA_REC['encryption'] = "off"
        STORAGE_DATA_REC['disk_cache'] = "none"
        STORAGE_DATA_REC['lazy_refcounts'] = "off"
        STORAGE_DATA_REC['format'] = "qcow2"
        self.STORAGE_DATA_REC = STORAGE_DATA_REC

        return self

    def do_desktop(self, verbose=False):
        """
        Will prepare a Guest XML config for Desktop VM
        """
        # requires for Cmd but not for GTK app
        if configuration.check_conffile(self.conf.conffile) is not False:
            configuration.Configuration.basic_config(self)

            hypervisor = hv.select_hypervisor()
            hypervisor.name = self.hypervisor_name
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            name = self.conf.dataprompt.get('name')

            # BasicConfiguration
            scenario = Scenarios()
            desktop = scenario.pre_desktop(name)

            self.callsign = desktop.name['VM_name']
            self.name = guest.create_name(desktop.name)

            # Configure VM without pinned memory
            configuration.Configuration.set_memory_pin(self, False)
            desktop.memory_pin = False

            self.CONSOLE = configuration.Configuration.CONSOLE
            self.CHANNEL = configuration.Configuration.CHANNEL
            self.GRAPHICS = configuration.Configuration.GRAPHICS
            self.RNG = configuration.Configuration.RNG

            self.cpumode = guest.create_cpumode_pass(desktop.cpumode)
            self.power = guest.create_power(desktop.power)
            self.ondef = guest.create_ondef(desktop.ondef)
            self.network = guest.create_interface(desktop.network)
            self.audio = guest.create_audio(desktop.audio)
            self.usb = guest.create_usb(desktop.usb)
            if util.check_tpm() is not False:
                self.tpm = guest.create_tpm(desktop.tpm)
            else:
                self.tpm = ""
            self.features = guest.create_features(desktop.features)
            self.clock = guest.create_clock(desktop.clock)
            self.video = guest.create_video(desktop.video)
            self.iothreads = guest.create_iothreads(desktop.iothreads)
            self.controller = guest.create_controller(self.conf.listosdef)

            self.vcpu = guest.create_cpu(desktop.vcpu)
            self.memory = guest.create_memory(desktop.memory)
            self.memory_backing = guest.create_memory_backing()
            self.osdef = guest.create_osdef(desktop.osdef)

            self.custom = ["vnet"]
            fw_features = ['secure-boot']
            firmware = fw.find_firmware(self.fw_info, arch=self.conf.listosdef['arch'], features=fw_features, interface='uefi')
            if firmware:
                self.custom = ["loader", "vnet"]
                self.loader = firmware

            # Check user setting
            configuration.Configuration.check_user_settings(self, desktop)

            # config store
            cfg_store = configstore.create_config_store(self, desktop, hypervisor, self.conf.overwrite)
            if cfg_store is None:
                util.print_error("No config store found...")
                return

            # setting for storage
            self.STORAGE_DATA_REC = desktop.STORAGE_DATA_REC
            self.STORAGE_DATA_REC['path'] = self.conf.diskpath['path']
            self.STORAGE_DATA['storage_name'] = self.callsign

            configuration.Configuration.check_storage(self)
            self.disk = guest.create_xml_disk(self.STORAGE_DATA)

            # XML File path
            self.filename = cfg_store.get_domain_config_filename()

            # host filesystem
            self.hostfs = guest.create_host_filesystem(self.host_filesystem)

            # transparent hugepages doesnt need any XML config
            self.hugepages = ""

            if self.conf.overwrite == "on":
                # remove previous domain in the hypervisor
                hypervisor.remove_domain(self.callsign)

            if (self.conf.mode != "guest" or self.conf.mode == "both") and util.check_iam_root() is True:
                util.print_title("Host Section")
                # Create the Virtual Disk image
                if self.conf.vmimage is None:
                    host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                host.transparent_hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("enable", "enable")
                host.swappiness("35")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                host.host_end()

            if self.conf.mode != "host" or self.conf.mode == "both":
                util.final_step_guest(cfg_store, self, verbose)

    def testing_os(self):
        """
        testing an OS
        """
        self.name = c.BasicConfiguration.name(self, "testingos")
        return self

    def easy_migration(self):
        """
        easy migration
        """
        self.name = c.BasicConfiguration.name(self, "easy_migration")
        return self

    def secure_vm_update(self, sev_info):
        """
        do sec feature
        """
        f.Features.security_f(self, sev_info)

    def pre_secure_vm(self, name, sev_info):
        """
        secure VM
        """
        if name is None:
            name = "securevm"

        # BasicConfiguration definition
        self.name = c.BasicConfiguration.name(self, name)
        self.osdef = c.BasicConfiguration.osdef(self, "x86_64", "pc-q35-6.2", "hd")
        self.ondef = c.BasicConfiguration.ondef(self, "destroy", "destroy", "destroy")
        self.tpm = c.ComplexConfiguration.tpm_emulated(self, "tpm-crb", "emulator", "2.0")
        # memory
        unit = f.MemoryUnit("Gib", "Gib")
        self.memory = c.BasicConfiguration.memory_pinned(self, unit, "4", "4")
        # vcpu
        self.vcpu = c.BasicConfiguration.vcpu(self, "2")

        self.cpumode = c.BasicConfiguration.cpumode_pass(self, "off", "")
        self.power = c.BasicConfiguration.power(self, "no", "no")
        self.video = c.BasicConfiguration.video(self, "qxl")
        self.inputkeyboard = c.BasicConfiguration.input(self, "keyboard", "ps2")
        # network
        macaddress = util.generate_mac_address()
        self.network = c.ComplexConfiguration.network(self, macaddress, "default", "e1000")

        # Set some expected features
        f.Features.features_perf(self)
        f.Features.clock_perf(self)
        f.Features.security_f(self, sev_info)

        # prefiled storage
        STORAGE_DATA_REC = {}
        STORAGE_DATA_REC['preallocation'] = "metadata"
        STORAGE_DATA_REC['encryption'] = "on"
        STORAGE_DATA_REC['disk_cache'] = "writethrough"
        STORAGE_DATA_REC['lazy_refcounts'] = "on"
        STORAGE_DATA_REC['format'] = "qcow2"
        self.STORAGE_DATA_REC = STORAGE_DATA_REC

        return self

    def do_securevm(self, verbose):
        """
        Will prepare a Guest XML config and Host for Secure VM
        """
        if configuration.check_conffile(self.conf.conffile) is not False:
            configuration.Configuration.basic_config(self)

            hypervisor = hv.select_hypervisor()
            hypervisor.name = self.hypervisor_name
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            # SEV information
            sev_info = host.sev_info(hypervisor)

            if not sev_info.sev_supported:
                util.print_error("Selected hypervisor ({}) does not support SEV".format(hypervisor.name))
                return

            name = self.conf.dataprompt.get('name')

            # BasicConfiguration
            scenario = Scenarios()
            securevm = scenario.pre_secure_vm(name, sev_info)

            self.callsign = securevm.name['VM_name']
            self.name = guest.create_name(securevm.name)

            # Configure VM with pinned memory
            configuration.Configuration.set_memory_pin(self, True)
            securevm.memory_pin = True

            self.CONSOLE = configuration.Configuration.CONSOLE
            self.CHANNEL = configuration.Configuration.CHANNEL
            self.GRAPHICS = configuration.Configuration.GRAPHICS
            self.RNG = configuration.Configuration.RNG

            self.cpumode = guest.create_cpumode_pass(securevm.cpumode)
            self.power = guest.create_power(securevm.power)
            self.ondef = guest.create_ondef(securevm.ondef)
            self.network = guest.create_interface(securevm.network)
            if util.check_tpm() is not False:
                self.tpm = guest.create_tpm(securevm.tpm)
            else:
                self.tpm = ""
            self.features = guest.create_features(securevm.features)
            self.clock = guest.create_clock(securevm.clock)
            #self.iothreads = guest.create_iothreads(securevm.iothreads)
            # disable as this permit run some stuff on some other host CPU
            self.iothreads = ""
            self.video = guest.create_video(securevm.video)
            self.controller = guest.create_controller(self.conf.listosdef)
            self.vcpu = guest.create_cpu(securevm.vcpu)
            self.memory = guest.create_memory(securevm.memory)
            self.memory_backing = ""
            self.osdef = guest.create_osdef(securevm.osdef)
            self.inputkeyboard = guest.create_input(securevm.inputkeyboard)
            self.inputmouse = ""

            # transparent hugepages doesnt need any XML config
            self.hugepages = ""

            self.custom = ["vnet"]
            # Find matching firmware
            if sev_info.es_supported():
                fw_features = ['amd-sev-es']
            else:
                fw_features = ['amd-sev']

            firmware = fw.find_firmware(self.fw_info, arch=self.conf.listosdef['arch'], features=fw_features, interface='uefi')
            if firmware:
                self.custom = ["loader", "vnet"]
                self.loader = firmware

            # Check user setting
            configuration.Configuration.check_user_settings(self, securevm)

            cfg_store = configstore.create_config_store(self, securevm, hypervisor, self.conf.overwrite)
            if cfg_store is None:
                util.print_error("No config store found...")
                return

            # recommended setting for storage
            self.STORAGE_DATA_REC = securevm.STORAGE_DATA_REC
            self.STORAGE_DATA_REC['path'] = self.conf.diskpath['path']
            self.STORAGE_DATA['storage_name'] = self.callsign

            configuration.Configuration.check_storage(self)
            self.disk = guest.create_xml_disk(self.STORAGE_DATA)

            # XML File path
            self.filename = cfg_store.get_domain_config_filename()

            if (self.conf.mode != "guest" or self.conf.mode == "both") and util.check_iam_root() is True:
                util.print_title("Host Section")
                # Create the Virtual Disk image
                if self.conf.vmimage is None:
                    host.create_storage_image(self.STORAGE_DATA)
                # Deal with SEV
                util.print_title("Prepare SEV attestation")
                if sev_info.sev_supported is True:
                    host.kvm_amd_sev(sev_info)

                    dh_params = None
                    # certifate already present
                    if hypervisor.has_sev_cert():
                        util.print_ok("SEV Certificate already present")
                        # A host certificate is configured, try to enable remote attestation
                        cert_file = hypervisor.sev_cert_file()
                    else:
                        util.print_ok("SEV Certificate NOT present")
                    # forcing generation of a local PDH is NOT SECURE!
                    if self.force_sev is True or hypervisor.has_sev_cert() is False:
                        util.print_ok("Force PDH creation")
                        cert_file = "localhost.pdh"
                        sev.sev_extract_pdh(cfg_store, cert_file)
                        sev.sev_validate_pdh(cfg_store, cert_file)
                        util.update_virthost_cert_file(self.conf.hvfile, "localhost", cfg_store.get_path()+cert_file)

                    policy = sev_info.get_policy()
                    if not sev.sev_prepare_attestation(cfg_store, policy, cert_file):
                        util.print_error("Creation of attestation keys failed!")
                        return
                    session_key = sev.sev_load_session_key(cfg_store)
                    dh_params = sev.sev_load_dh_params(cfg_store)
                    sev_info.set_attestation(session_key, dh_params)
                    securevm.secure_vm_update(sev_info)
                    cfg_store.set_attestation(True)

                    self.security = guest.create_security(securevm.security)
                else:
                    util.print_error("SEV is not supported!") # this is not possible but lets catch this in case...

                # Prepare the host system
                # Transparent hugepages
                host.transparent_hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("disable", "")
                host.swappiness("0")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("bfq")
                # END of the config
                host.host_end()

            if self.conf.overwrite == "on":
                # remove previous domain in the hypervisor
                hypervisor.remove_domain(self.callsign)

            if self.conf.mode != "host" or self.conf.mode == "both":
                util.final_step_guest(cfg_store, self, verbose)

    def soft_rt_vm(self):
        """
        soft Real Time VM
        """
        self.name = c.BasicConfiguration.name(self, "soft_rt_vm")
        return self
