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
Guest side definition
"""

from cmd import Cmd
import getpass
import os
import yaml
import virtscenario.util as util
import virtscenario.guest as guest
import virtscenario.scenario as s
import virtscenario.configuration as c
import virtscenario.qemulist as qemulist
import virtscenario.xmlutil as xmlutil
import virtscenario.host as host
import virtscenario.libvirt as libvirt
import virtscenario.firmware as fw
import virtscenario.sev as sev
import virtscenario.hypervisors as hv
import virtscenario.configstore as configstore

def create_default_domain_xml(xmlfile):
    """
    create the VM domain XML
    """
    cmd1 = "virt-install --print-xml --virt-type kvm --arch x86_64 --machine pc-q35-6.2 "
    cmd2 = "--osinfo sles12sp5 --rng /dev/urandom --network test_net >" +xmlfile
    util.system_command(cmd1+cmd2)

def create_from_template(finalfile, xml_all):
    """
    create the VM domain XML from all template input given
    """
    util.print_summary("\nCreate The XML VM configuration")
    print(os.path.dirname(os.path.abspath(finalfile))+"/"+finalfile)
    with open(finalfile, 'w') as file_h:
        file_h.write(xml_all)

def validate_xml(xmlfile):
    """
    validate the generated file
    """
    cmd = "virt-xml-validate "+xmlfile
    out, errs = util.system_command(cmd)
    util.print_summary("\nValidation of the XML file")
    if errs:
        print(errs)
    print(out)

def create_xml_config(filename, data):
    """
    draft xml create step
    create the xml file
    """
    # final XML creation
    # start the domain definition
    xml_all = ""
    # first line must be a warning, kvm by default
    xml_all = "<!-- WARNING: THIS IS A GENERATED FILE FROM VIRT-SCENARIO -->\n"
    xml_all += "<domain type='kvm'>\n"
    xml_all += data.name+data.memory+data.vcpu+data.osdef+data.security
    xml_all += data.features+data.cpumode+data.clock+data.hugepages
    xml_all += data.ondef+data.power+data.iothreads
    # all below must be in devices section
    xml_all += "\n  <devices>"
    xml_all += data.emulator+data.controller
    xml_all += data.disk+data.network+data.CONSOLE
    xml_all += data.CHANNEL+data.inputmouse+data.inputkeyboard
    xml_all += data.GRAPHICS+data.video+data.RNG+data.watchdog
    xml_all += data.usb+data.tpm
    # close the device section
    xml_all += "</devices>\n"
    # close domain section
    xml_all += "</domain>\n"

    # create the file from the template and setting
    create_from_template(filename, xml_all)
    if "loader" in data.custom:
        if data.loader is None:
            executable = qemulist.OVMF_PATH+"/ovmf-x86_64-smm-opensuse-code.bin"
        else:
            executable = data.loader
        xmlutil.add_loader_nvram(filename, executable, qemulist.OVMF_VARS+"/"+data.callsign+".VARS")
    ### if "XXXX" in data.custom:

def final_step_guest(cfg_store, data):
    """
    show setting from xml
    create the XML config
    validate the XML file
    """
    filename = cfg_store.get_domain_config_filename()
    util.print_summary("Guest Section")
    create_xml_config(filename, data)
    xmlutil.show_from_xml(filename)
    validate_xml(filename)
    cfg_store.store_config()
    util.print_summary_ok("Guest XML Configuration is done")

def find_yaml_file():
    """ Show all yaml file in current path"""
    yaml_list = []
    for files in os.listdir('.'):
        if files.endswith(".yaml"):
            yaml_list.append(files)
    return yaml_list

conffile_locations = [
    '/etc/',
    '~/.local/etc/'
]

conffile_name = 'virtscenario.yaml'
hvfile_name = 'virthosts.yaml'

def find_file(name):
    global conffile_locations
    conffile = "{}/{}".format(conffile_locations[0], name)

    for path in conffile_locations:
        path = os.path.expanduser(path)
        filename = "{}/{}".format(path, name)
        if os.path.isfile(filename):
            conffile = filename

    return conffile

def find_conffile():
    global conffile_name

    return find_file(conffile_name)

def find_hvfile():
    global hvfile_name

    return find_file(hvfile_name)

######
# MAIN
# ####

# virt-install test
#FILE = "VMa.xml"
#create_default_domain_xml(FILE)

def main():
    """
    main
    """

    # Main loop
    MyPrompt().cmdloop()
    return 0

class MyPrompt(Cmd):
    """
    prompt Cmd
    """
    # define some None
    conffile = find_conffile()
    hvfile = find_hvfile()
    vm_config_store = '~/.local/virtscenario/'
    emulator = None
    inputkeyboard = ""
    inputmouse = ""
    xml_all = None
    vcpu = name = diskpath = memory = osdef = ondef = cpumode = power = watchdog = ""
    audio = usb = disk = features = clock = network = filename = tpm = iothreads = ""
    callsign = custom = security = video = controller = hugepages = toreport = ""
    # prompt Cmd
    prompt = 'virt-scenario > '
    introl = {}
    introl[0] = "\n"+util.esc('32;1;1') +" virt-scenario "+util.esc(0)+ "Interactive Terminal!\n\n"
    introl[1] = " Prepare a Libvirt XML guest config and the host to run a customized guest:\n"
    introl[2] = util.esc('34;1;1')+" computation | desktop | securevm"+util.esc(0)+"\n"
    introl[3] = "\n Possible User Settings:\n"
    introl[4] = util.esc('34;1;1')+" name|vcpu|memory|machine|bootdev|diskpath|conf"+util.esc(0)+"\n"
    introl[5] = "\n"+" Some settings which overwrite scenario settings can be done in: "+conffile+"\n"
    introl[6] = util.esc('31;1;1')+"\n WARNING:"+util.esc(0)+" This is under Devel...\n"
    introl[7] = " Source code: https://github.com/aginies/virt-scenario\n"
    introl[8] = " Report bug: https://github.com/aginies/virt-scenario/issues\n"
    intro = ''
    for line in range(9):
        intro += introl[line]

    # There is some Immutable in dict for the moment...
    #IMMUT = immut.Immutable()
    CONSOLE = guest.create_console()#IMMUT.console_data)
    CHANNEL = guest.create_channel()#IMMUT.channel_data)
    GRAPHICS = guest.create_graphics()#IMMUT.graphics_data)
    MEMBALLOON = guest.create_memballoon()#IMMUT.memballoon_data)
    RNG = guest.create_rng()#IMMUT.rng_data)
    METADATA = guest.create_metadata()#IMMUT.metadata_data)

    promptline = '_________________________________________\n'
    prompt = promptline +'> '

    # what kind of configuration should be done
    mode = "both"
    all_modes = ['guest', 'host', 'both']

    dataprompt = {
        'name': None,
        'vcpu': None,
        'memory': None,
        'machine': None,
        'bootdev': None,
        'path': '/var/libvirt/images',
        }

    # default os
    listosdef = ({
        'arch': "x86_64",
        'machine': "pc-q35-6.2",
        'boot_dev': 'hd',
    })


    def check_user_settings(self, virtum):
        """
        Check if the user as set some stuff, if yes use it
        """
        vcpuuser = self.dataprompt.get('vcpu')
        if vcpuuser != None:
            self.vcpu = guest.create_cpu({'vcpu': vcpuuser})
        else:
            self.vcpu = guest.create_cpu(virtum.vcpu)

        nameuser = self.dataprompt.get('name')
        if nameuser != None:
            self.name = guest.create_name({'VM_name': nameuser})
        else:
            self.name = guest.create_name(virtum.name)

        diskpathuser = self.dataprompt.get('path')
        if diskpathuser != None:
            self.diskpath = {'path': diskpathuser}

        memoryuser = self.dataprompt.get('memory')
        if memoryuser != None:
            self.memory = guest.create_memory({
                'mem_unit': 'Gib',
                'max_memory': memoryuser,
                'current_mem_unit': 'Gib',
                'memory': memoryuser,
                })
        else:
            self.memory = guest.create_memory(virtum.memory)

        machineuser = self.dataprompt.get('machine')
        bootdevuser = self.dataprompt.get('bootdev')
        if machineuser != None:
            self.listosdef.update({'machine': machineuser})
        if bootdevuser != None:
            self.listosdef.update({'boot_dev': bootdevuser})
        self.osdef = guest.create_osdef(self.listosdef)

    def update_prompt(self, args):
        """
        update prompt with value set by user
        """
        line1 = line2 = line3 = line4 = line5 = line6 = ""
        self.promptline = '---------- User Settings ----------\n'

        # update prompt with all values
        name = self.dataprompt.get('name')
        if name != None:
            line1 = util.esc('32;1;1')+'Name: '+util.esc(0)+name+'\n'

        vcpu = self.dataprompt.get('vcpu')
        if vcpu != None:
            line2 = util.esc('32;1;1')+'Vcpu: '+util.esc(0)+vcpu+'\n'

        memory = self.dataprompt.get('memory')
        if memory != None:
            line3 = util.esc('32;1;1')+'Memory: '+util.esc(0)+memory+' Gib\n'

        machine = self.dataprompt.get('machine')
        if machine != None:
            line4 = util.esc('32;1;1')+'Machine Type: '+util.esc(0)+machine+'\n'

        bootdev = self.dataprompt.get('bootdev')
        if bootdev != None:
            line5 = util.esc('32;1;1')+'Boot Device: '+util.esc(0)+bootdev+'\n'

        diskpath = self.dataprompt.get('path')
        if diskpath != None:
            line6 = util.esc('32;1;1')+'Disk Path: '+util.esc(0)+diskpath+'\n'

        if args == 'name':
            self.dataprompt.update({'name': name})
        if args == 'vcpu':
            self.dataprompt.update({'vcpu': vcpu})
        if args == 'memory':
            self.dataprompt.update({'memory': memory})
        if args == 'machine':
            self.dataprompt.update({'machine': machine})
        if args == 'bootdev':
            self.dataprompt.update({'bootdev': bootdev})
        if args == 'diskpath':
            self.dataprompt.update({'path': diskpath})

        self.prompt = self.promptline+line1+line2+line3+line4+line5+line6+'\n'+'> '

    def check_conffile(self):
        """
        check if the configuration file is present
        """
        if os.path.isfile(self.conffile) is False:
            util.print_error(self.conffile+" configuration Yaml file Not found!")
            print("Please select one to contine:")
            print("conf /path/to/file.yaml")
            return False

    def basic_config(self):
        """
        init the basic configuration
        """
        self.vcpu = ""
        self.memory = ""
        self.osdef = ""
        self.name = ""
        self.ondef = ""
        self.cpumode = ""
        self.power = ""
        self.watchdog = ""
        self.audio = ""
        self.usb = ""
        self.disk = ""
        self.features = ""
        self.clock = ""
        self.ondef = ""
        self.network = ""
        self.filename = ""
        self.tpm = ""
        self.iothreads = ""
        self.callsign = ""
        self.custom = ""
        self.loader = None
        self.security = ""
        self.video = ""
        self.config = ""
        self.fw_info = fw.default_firmware_info()

        # prefile STORAGE_DATA in case of...
        self.STORAGE_DATA = {
            # XML part
            'disk_type': 'file',
            'disk_cache': '',
            'disk_target': 'vda',
            'disk_bus': 'virtio',
            'format': 'qcow2',
            'unit': 'G',
            'capacity': '20',
            'cluster_size': '2M',
            'lazy_refcounts': '',
            'preallocation': '',
            'compression_type': 'zlib',
            'encryption': '',
            #'password': '',
        }
        # This dict is the recommended settings for storage
        self.STORAGE_DATA_REC = {}

        # BasicConfiguration
        # pre filed in case of...
        data = c.BasicConfiguration()
        self.emulator = guest.create_emulator(data.emulator("/usr/bin/qemu-system-x86_64"))
        self.inputkeyboard = guest.create_input(data.input("keyboard", "virtio"))
        self.inputmouse = guest.create_input(data.input("mouse", "virtio"))

        # Using config.yaml to file some VAR
        with open(self.conffile) as file:
            config = yaml.full_load(file)
            # parse all section of the yaml file
            for item, value in config.items():
                # check mathing section
                if item == "hypervisors":
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == 'hvconf':
                                self.hvfile = valuei
                            else:
                                util.print_error("Unknow parameter in hypervisors section: {}".format(datai))
                elif item == "config":
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == 'path':
                                self.vm_config = valuei
                            elif datai == 'vm-config-store':
                                self.vm_config_store = valuei
                            else:
                                util.print_error("Unknown parameter in config section: {}".format(datai))
                elif item == "emulator":
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == "emulator":
                                self.emulator = guest.create_emulator(data.emulator(valuei))
                            elif datai == "fw_meta":
                                self.fw_info = fw.reload_firmware_info(valuei)
                            else:
                                util.print_error("Unknow parameter in emulator section")
                elif item == "input":
                    # Parse keyboard and mouse
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == "keyboard":
                                self.inputkeyboard = guest.create_input(data.input("keyboard", valuei))
                            elif datai == "mouse":
                                self.inputmouse = guest.create_input(data.input("mouse", valuei))
                            else:
                                util.print_error("Unknow parameter in input section")
                elif item == "architecture":
                    # Parse list os def section
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == "arch":
                                self.listosdef.update({'arch': valuei})
                            else:
                                util.print_error("Unknow parameter in lisofdef section")
                elif item == "STORAGE_DATA":
                    # available option in config.yaml file, all other ignored
                    storage_dict = ["disk_type", "disk_cache", "disk_target", "disk_bus", "path",
                                    "format", "unit", "capacity", "cluster_size",
                                    "lazy_refcounts", "preallocation", "compression_type",
                                    "encryption",
                                   ]
                    # Parse storage section
                    for dall in value:
                        for datai, valuei in dall.items():
                            # check the option is the same and file it
                            if datai in storage_dict:
                                self.STORAGE_DATA[datai] = valuei
                                #print("DEBUG "+datai+":"+str(valuei))
                            else:
                                util.print_error("Unknow option for storage!")
                else:
                    util.print_error("Unknow Section: {}".format(item))
        hv.load_hypervisors(self.hvfile)
        #return self

    def check_storage(self):
        """
        use storage data from config.yaml if available, compare to recommended
        create a list to show diff between user setting and recommended
        """
        self.toreport = {1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}
        nestedindex = 0
        # Create the XML disk part

        # DISK PATH
        # if no data path set use recommended
        if self.STORAGE_DATA['path'] == "":
            self.STORAGE_DATA['path'] = self.diskpath['path']
        # if path differ grab data to report
        if self.diskpath['path'] != self.STORAGE_DATA['path']:
            # there is no diff is no user setting
            if self.STORAGE_DATA['path'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk path"
                self.toreport[nestedindex]['rec'] = self.diskpath['path']
                self.toreport[nestedindex]['set'] = self.STORAGE_DATA['path']

        # PREALLOCATION
        if self.STORAGE_DATA['preallocation'] is False:
            self.STORAGE_DATA['preallocation'] = "off"
        # no preallocation has been set, using recommended
        # if they differ grab data to report
        if self.STORAGE_DATA['preallocation'] != self.STORAGE_DATA_REC['preallocation']:
            # there is no diff is no user setting
            if self.STORAGE_DATA['preallocation'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk preallocation"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA_REC['preallocation']
                self.toreport[nestedindex]['set'] = self.STORAGE_DATA['preallocation']
        if self.STORAGE_DATA['preallocation'] == "":
            self.STORAGE_DATA['preallocation'] = self.STORAGE_DATA_REC['preallocation']

        # ENCRYPTION
        if self.STORAGE_DATA['encryption'] is False:
            self.STORAGE_DATA['encryption'] = "off"
        if self.STORAGE_DATA['encryption'] is True:
            self.STORAGE_DATA['encryption'] = "on"
        if self.STORAGE_DATA_REC['encryption'] is True:
            self.STORAGE_DATA_REC['encryption'] == "on"
        if self.STORAGE_DATA_REC['encryption'] is False:
            self.STORAGE_DATA_REC['encryption'] == "off"
        # if they differ grab data to report
        if self.STORAGE_DATA['encryption'] != self.STORAGE_DATA_REC['encryption']:
            # there is no diff is no user setting
            if self.STORAGE_DATA['encryption'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk Encryption"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA_REC['encryption']
                self.toreport[nestedindex]['set'] = "off"
        # if no encryption set and recommended is on
        if self.STORAGE_DATA['encryption'] == "" and self.STORAGE_DATA_REC['encryption'] == "on":
            self.STORAGE_DATA['encryption'] = "on"
        # ask for password in case of encryption on
        if self.STORAGE_DATA['encryption'] == "on":
            self.STORAGE_DATA['encryption'] = self.STORAGE_DATA_REC['encryption']
            # Ask for the disk password
            password = getpass.getpass("Please enter password to encrypt the VM image: ")
            self.STORAGE_DATA['password'] = password

        # DISKCACHE
        if self.STORAGE_DATA['disk_cache'] != self.STORAGE_DATA_REC['disk_cache']:
            if self.STORAGE_DATA['disk_cache'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk Cache"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA_REC['disk_cache']
                self.toreport[nestedindex]['set'] = self.STORAGE_DATA['disk_cache']
        # if no disk_cache use the recommanded one
        if self.STORAGE_DATA['disk_cache'] == "":
            self.STORAGE_DATA['disk_cache'] = self.STORAGE_DATA_REC['disk_cache']

        # LAZY_REFCOUNTS
        if self.STORAGE_DATA['lazy_refcounts'] is False:
            self.STORAGE_DATA['lazy_refcounts'] = "off"
        if self.STORAGE_DATA['lazy_refcounts'] is True:
            self.STORAGE_DATA['lazy_refcounts'] = "on"
        if self.STORAGE_DATA_REC['lazy_refcounts'] is True:
            self.STORAGE_DATA_REC['lazy_refcounts'] == "on"
        if self.STORAGE_DATA_REC['lazy_refcounts'] is False:
            self.STORAGE_DATA_REC['lazy_refcounts'] == "off"
        if self.STORAGE_DATA['lazy_refcounts'] != self.STORAGE_DATA_REC['lazy_refcounts']:
            if self.STORAGE_DATA['lazy_refcounts'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk Lazy_refcounts"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA_REC['lazy_refcounts']
                self.toreport[nestedindex]['set'] = self.STORAGE_DATA['lazy_refcounts']
        # if no disk_cache use the recommanded one
        if self.STORAGE_DATA['lazy_refcounts'] == "":
            self.STORAGE_DATA['lazy_refcounts'] = self.STORAGE_DATA_REC['lazy_refcounts']

        # DISK FORMAT
        if self.STORAGE_DATA['format'] != self.STORAGE_DATA_REC['format']:
            if self.STORAGE_DATA['format'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk Format"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA_REC['format']
                self.toreport[nestedindex]['set'] = self.STORAGE_DATA['format']
        # if no disk format use the recommanded one
        if self.STORAGE_DATA['format'] == "":
            self.STORAGE_DATA['format'] = self.STORAGE_DATA_REC['format']

        # Remove index in dict which are empty
        if nestedindex >= 1:
            for count in range(1, 6):
                if len(self.toreport) != nestedindex:
                    self.toreport.pop(len(self.toreport))

    def do_shell(self, args):
        """
        Execute a system command
        """
        out, errs = util.system_command(args)
        if errs:
            print(errs)
        if not out:
            util.print_error(' No output... seems weird...')
        else:
            print(out)

    def help_shell(self):
        """
        help on execute command
        """
        print("Execute a system command")

    def do_info(self, args):
        """
        show system info
        """
        import psutil
        util.print_data("Number of Physical cores", str(psutil.cpu_count(logical=False)))
        util.print_data("Number of Total cores", str(psutil.cpu_count(logical=True)))
        cpu_frequency = psutil.cpu_freq()
        util.print_data("Max Frequency", str(cpu_frequency.max)+"Mhz")
        virtual_memory = psutil.virtual_memory()
        util.print_data("Total Memory present", str(util.bytes_to_gb(virtual_memory.total))+"Gb")

    def help_info(self):
        """
        show help on info
        """
        print("Show system info")

    def help_computation(self):
        """
        show some help on computation scenario
        """
        print("Will prepare a Guest XML config for computation")

    def do_computation(self, args):
        """
        computation
        """
        if self.check_conffile() is not False:
            self.basic_config()

            hypervisor = hv.select_hypervisor()
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            # computation setup
            scenario = s.Scenarios()
            computation = scenario.computation()
            cfg_store = configstore.create_config_store(self, computation, hypervisor)

            # Check user setting
            self.check_user_settings(computation)

            self.callsign = computation.name['VM_name']
            self.name = guest.create_name(computation.name)
            self.cpumode = guest.create_cpumode_pass(computation.cpumode)
            self.power = guest.create_power(computation.power)
            self.ondef = guest.create_ondef(computation.ondef)
            self.watchdog = guest.create_watchdog(computation.watchdog)
            self.network = guest.create_interface(computation.network)
            self.features = guest.create_features(computation.features)
            self.clock = guest.create_clock(computation.clock)
            self.video = guest.create_video(computation.video)
            self.iothreads = guest.create_iothreads(computation.iothreads)
            self.controller = guest.create_controller(self.listosdef)
            self.custom = ["loader",]
            self.hugepages = guest.create_hugepages()

            self.STORAGE_DATA['storage_name'] = self.callsign
            self.STORAGE_DATA_REC['path'] = self.diskpath['path']
            self.STORAGE_DATA_REC['preallocation'] = "off"
            self.STORAGE_DATA_REC['encryption'] = "off"
            self.STORAGE_DATA_REC['disk_cache'] = "unsafe"
            self.STORAGE_DATA_REC['lazy_refcounts'] = "on"
            self.STORAGE_DATA_REC['format'] = "raw"
            self.filename = self.callsign+".xml"
            self.check_storage()
            self.disk = guest.create_disk(self.STORAGE_DATA)

            if self.mode != "host" or self.mode == "both":
                final_step_guest(cfg_store, self)

            if self.mode != "guest" or self.mode == "both":
                util.print_summary("Host Section")
                # Create the Virtual Disk image
                host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                host.hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("enable", "disable")
                host.swappiness("0")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                host.host_end(self.filename, self.toreport, self.conffile)

    def help_desktop(self):
        """
        show some help on desktop scenario
        """
        print("Will prepare a Guest XML config for Desktop VM")

    def do_desktop(self, args):
        """
        desktop
        """
        if self.check_conffile() is not False:
            self.basic_config()

            hypervisor = hv.select_hypervisor()
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            # BasicConfiguration
            scenario = s.Scenarios()
            desktop = scenario.desktop()
            cfg_store = configstore.create_config_store(self, desktop, hypervisor)

            # Check user setting
            self.check_user_settings(desktop)

            self.callsign = desktop.name['VM_name']
            self.name = guest.create_name(desktop.name)
            self.cpumode = guest.create_cpumode_pass(desktop.cpumode)
            self.power = guest.create_power(desktop.power)
            self.ondef = guest.create_ondef(desktop.ondef)
            self.network = guest.create_interface(desktop.network)
            self.audio = guest.create_audio(desktop.audio)
            self.usb = guest.create_usb(desktop.usb)
            self.tpm = guest.create_tpm(desktop.tpm)
            self.features = guest.create_features(desktop.features)
            self.clock = guest.create_clock(desktop.clock)
            self.video = guest.create_video(desktop.video)
            self.iothreads = guest.create_iothreads(desktop.iothreads)
            self.controller = guest.create_controller(self.listosdef)
            self.hugepages = guest.create_hugepages()

            self.STORAGE_DATA['storage_name'] = self.callsign
            self.STORAGE_DATA_REC['path'] = self.diskpath['path']
            self.STORAGE_DATA_REC['preallocation'] = "metadata"
            self.STORAGE_DATA_REC['encryption'] = "off"
            self.STORAGE_DATA_REC['disk_cache'] = "none"
            self.STORAGE_DATA_REC['lazy_refcounts'] = "off"
            self.STORAGE_DATA_REC['format'] = "qcow2"
            self.filename = desktop.name['VM_name']+".xml"
            self.check_storage()
            self.disk = guest.create_disk(self.STORAGE_DATA)

            if self.mode != "host" or self.mode == "both":
                final_step_guest(cfg_store, self)

            if self.mode != "guest" or self.mode == "both":
                util.print_summary("Host Section")
                # Create the Virtual Disk image
                host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                host.hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("enable", "enable")
                host.swappiness("35")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                host.host_end(self.filename, self.toreport, self.conffile)

    def help_securevm(self):
        """
        show some help on secure VM scenario
        """
        print("Will prepare a Guest XML config and Host for Secure VM")

    def do_securevm(self, args):
        """
        securevm
        """
        if self.check_conffile() is not False:
            self.basic_config()

            hypervisor = hv.select_hypervisor()
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            # SEV information
            sev_info = host.sev_info(hypervisor)

            if not sev_info.sev_supported():
                util.print_error("Selected hypervisor ({}) does not support SEV".format(hypervisor.name))
                return

            # BasicConfiguration
            scenario = s.Scenarios()
            securevm = scenario.secure_vm(sev_info)
            cfg_store = configstore.create_config_store(self, securevm, hypervisor)

            # do not create the SEV xml config if this is not supported...
            if sev_info.sev_supported is True:
                self.security = guest.create_security(securevm.security)
                # TOFIX: if not supported we need to stop all stuff...
                self.security = guest.create_security(securevm.security)

            # Check user setting
            self.check_user_settings(securevm)

            self.callsign = securevm.name['VM_name']
            self.name = guest.create_name(securevm.name)
            self.cpumode = guest.create_cpumode_pass(securevm.cpumode)
            self.power = guest.create_power(securevm.power)
            self.ondef = guest.create_ondef(securevm.ondef)
            self.network = guest.create_interface(securevm.network)
            self.tpm = guest.create_tpm(securevm.tpm)
            self.features = guest.create_features(securevm.features)
            self.clock = guest.create_clock(securevm.clock)
            self.iothreads = guest.create_iothreads(securevm.iothreads)
            self.video = guest.create_video(securevm.video)
            self.controller = guest.create_controller(self.listosdef)
            self.custom = ["loader",]

            # recommended setting for storage
            self.STORAGE_DATA_REC['path'] = self.diskpath['path']
            self.STORAGE_DATA_REC['preallocation'] = "metadata"
            self.STORAGE_DATA_REC['encryption'] = "on"
            self.STORAGE_DATA_REC['disk_cache'] = "writethrough"
            self.STORAGE_DATA_REC['lazy_refcounts'] = "on"
            self.STORAGE_DATA_REC['format'] = "qcow2"
            self.STORAGE_DATA['storage_name'] = self.callsign
            self.check_storage()
            self.disk = guest.create_disk(self.STORAGE_DATA)

            # no hugepages
            self.hugepages = ""

            # Find matching firmware
            if sev_info.es_supported():
                fw_features = ['amd-sev-es']
            else:
                fw_features = ['amd-sev']

            firmware = fw.find_firmware(self.fw_info, arch=self.listosdef['arch'], features=fw_features, interface='uefi')
            if len(firmware) > 0:
                self.loader = firmware

            # XML File path
            self.filename = securevm.name['VM_name']+".xml"
            if self.mode != "host" or self.mode == "both":
                final_step_guest(cfg_store, self)

            if self.mode != "guest" or self.mode == "both":
                util.print_summary("Host Section")
                # Create the Virtual Disk image
                host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                if sev_info.sev_supported is True:
                    host.kvm_amd_sev(sev_info)
                host.manage_ksm("disable", "")
                host.swappiness("0")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                if sev_info.sev_supported is True:
                # TOFIX
                    hostname = input("hostname of the SEV host? ")
                    # What is expected here?
                    policy = "--policy {}".format(hex(sev_info.get_policy()))
                    path_to_ca = self.config+"/"+hostname
                    host.sev_ex_val_gen(self.filename, path_to_ca, hostname, securevm.name['VM_name'], policy)
                # END of the config
                host.host_end(self.filename, self.toreport, self.conffile)

    def do_name(self, args):
        """
        define the machine name
        """
        if args == "":
            print("Please select a correct Virtual Machine name")
        else:
            name = {
                'name': args,
                }
            self.dataprompt.update({'name': name['name']})
            self.update_prompt(name['name'])

    def help_name(self):
        """
        help about the machine name
        """
        print("Define the Virtual Machine name")

    def do_machine(self, args):
        """
        select machine
        """
        if args not in qemulist.LIST_MACHINETYPE:
            print("Please select a correct machine Type")
        else:
            machine = {
                'machine': args,
                }
            self.dataprompt.update({'machine': machine['machine']})
            self.update_prompt(machine['machine'])

    def complete_machine(self, text, line, begidx, endidx):
        """
        auto completion machine type
        """
        if not text:
            completions = qemulist.LIST_MACHINETYPE[:]
        else:
            completions = [f for f in qemulist.LIST_MACHINETYPE if f.startswith(text)]
        return completions

    def help_machine(self):
        """
        help machine
        """
        print("Define the machine type")

    def do_vcpu(self, args):
        """
        vcpu number
        """
        if args.isdigit() is False:
            print("Please select a correct vcpu number")
            print(args)
        else:
            print(args)
            vcpu = {
                'vcpu': args,
                }
            self.dataprompt.update({'vcpu': vcpu['vcpu']})
            self.update_prompt(vcpu['vcpu'])

    def help_vcpu(self):
        """
        help vcpu
        """
        print("Set the VCPU for the VM definition")

    def do_diskpath(self, args):
        """
        define the disk path of the virtual image
        """
        if os.path.isdir(args):
            path = args
            diskpath = {
                'path': path,
                }
            self.dataprompt.update({'path': diskpath['path']})
            self.update_prompt(diskpath['path'])
        else:
            util.print_error('Please select a corrent path dir')

    def help_diskpath(self):
        """
        help about disk path
        """
        print("Define the path directory to store the Virtual Machine image")

    def do_bootdev(self, args):
        """
        boot device
        """
        if args not in qemulist.LIST_BOOTDEV:
            print("Please select a correct boot devices")
        else:
            bootdev = {
                'bootdev': args,
                }
            self.dataprompt.update({'bootdev': bootdev['bootdev']})
            self.update_prompt(bootdev['bootdev'])

    def complete_bootdev(self, text, line, begidx, endidx):
        """
        auto completion boot devices type
        """
        if not text:
            completions = qemulist.LIST_BOOTDEV[:]
        else:
            completions = [f for f in qemulist.LIST_BOOTDEV if f.startswith(text)]
        return completions

    def help_bootdev(self):
        """
        help bootdev
        """
        print("Select the boot device")

    def do_memory(self, args):
        """
        memory
        """
        if args.isdigit() is False:
            print("Please select a correct memory value (GiB)")
        else:
            memory = {
                'memory': args,
            }
            self.dataprompt.update({'memory': memory['memory']})
            self.update_prompt(memory['memory'])

    def help_memory(self):
        """
        help memory
        """
        print("Memory should be in Gib")

    def yaml_complete(self, text, line, begidx, endidx):
        """
        auto completion to find yaml file in current path
        """
        all_files = find_yaml_file()
        if not text:
            completions = all_files[:]
        else:
            completions = [f for f in all_files if f.startswith(text)]
        return completions

    def complete_conf(self, text, line, begidx, endidx):
        return self.yaml_complete(text, line, begidx, endidx)

    def complete_hvconf(self, text, line, begidx, endidx):
        return self.yaml_complete(text, line, begidx, endidx)

    def do_mode(self, args):
        """
        select if guest only should be done, or host
        default host and guest are done
        """
        mode = args
        if mode not in self.all_modes:
            print("Dont know this mode...")
        else:
            self.mode = mode

    def complete_mode(self, text, line, begidx, endidx):
        """
        auto completion for mode
        """
        if not text:
            completions = self.all_modes[:]
        else:
            completions = [f for f in self.all_modes if f.startswith(text)]
        return completions

    def do_conf(self, args):
        """
        select the conf yaml file
        """
        file = args
        if os.path.isfile(file):
            Cmd.file = file
            util.validate_file(Cmd.file)
            self.conffile = file
        else:
            util.print_error("File " +file +" Doesnt exist!")

    def do_hvconf(self, args):
        """
        Load Hypervisor configuration
        """
        file = args
        if os.path.isfile(file):
            util.validate_file(file)
            self.hvfile = file
        hv.load_hypervisors(self.hvfile)

    def help_conf(self):
        """
        help about conf file selection
        """
        print("Select the yaml configuration file")

    def do_quit(self, args):
        """
        Exit the application
        """
        # French Flag :)
        print(util.esc('44')+'Bye'+util.esc('107')+'Bye'+util.esc('41')+'Bye'+util.esc(0))
        return True

    def help_quit(self):
        """
        Quit virt-scenario
        """
        print('Exit the application. Shorthand: Ctrl-D.')

    do_EOF = do_quit
    help_EOF = help_quit
