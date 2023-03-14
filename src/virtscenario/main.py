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
    print(finalfile)
    with open(finalfile, 'w') as file_h:
        file_h.write(xml_all)

def validate_xml(xmlfile):
    """
    validate the generated file
    """
    util.print_summary("\nValidation of the XML file")
    cmd = "virt-xml-validate "+xmlfile
    out, errs = util.system_command(cmd)
    if errs:
        print(errs)
    print(out)

def create_xml_config(filename, data):
    """
    draft xml create step
    create the xml file
    """
    util.print_summary("\nCreate the XML file")
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
    xml_all += data.hostfs+data.usb+data.tpm+data.cdrom
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
        xmlutil.add_loader_nvram(filename, executable, qemulist.OVMF_VARS+"/"+data.callsign+".VARS", data.loader_type)
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

def show_how_to_use(filename):
    """
    show the virsh define command
    """
    util.print_summary_ok("How to use this on your system")
    util.print_ok("virsh define "+filename+"\n")

def find_ext_file(ext):
    """
    Show all extension files in current path
    """
    files_list = []
    for files in os.listdir('.'):
        if files.endswith(ext):
            files_list.append(files)
    return files_list

conffile_locations = [
    '/etc/virt-scenario',
    '/etc',
    '~/.local/etc',
    '.'
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
            #print("configuration found: "+filename)
            return filename

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
    loader = loader_type = config = fw_info = vm_config = ""
    # prompt Cmd
    prompt = 'virt-scenario > '
    introl = {}
    introl[0] = "\n"+util.esc('green') +" virt-scenario "+util.esc('reset')+ "Interactive Terminal!\n\n"
    introl[1] = " Setting the virt-scenario Configuration: "+util.esc('blue')+"conf"+util.esc('reset')+"\n"
    introl[2] = " Guest/Host/Both mode could be selected using: "+util.esc('blue')+"mode"+util.esc('reset')+"\n"
    introl[3] = " Force overwrite previous setting: "+util.esc('blue')+"overwrite"+util.esc('reset')+"\n"
    introl[4] = "\n Prepare a Libvirt XML guest config and the host to run a customized guest:\n"
    introl[5] = util.esc('blue')+" computation | desktop | securevm"+util.esc('reset')+"\n"
    introl[6] = "\n Possible User Settings For VM are:\n"
    introl[7] = util.esc('blue')+" name | vcpu | memory | machine | bootdev | diskpath | cdrom"+util.esc('reset')+"\n"
    introl[8] = "\n Hypervisors parameters:\n"
    introl[9] = util.esc('blue')+" hconf | hv_select | hvlist"+util.esc('reset')+"\n"
    introl[10] = "\n"+" You can overwrite some recommended VM settings editing: "+conffile+"\n"
    introl[11] = "\n Please read the manpage and the README.md file:\n"
    introl[12] = " https://github.com/aginies/virt-scenario/blob/main/README.md\n"
    introl[13] = util.esc('red')+"\n WARNING:"+util.esc('reset')+" This is under Devel...\n"
    introl[14] = " Source code: https://github.com/aginies/virt-scenario\n"
    introl[15] = " Report bug: https://github.com/aginies/virt-scenario/issues\n"
    intro = ''
    for line in range(16):
        intro += introl[line]

    # There is some Immutable in dict for the moment...
    #IMMUT = immut.Immutable()
    CONSOLE = guest.create_console()#IMMUT.console_data)
    CHANNEL = guest.create_channel()#IMMUT.channel_data)
    GRAPHICS = guest.create_graphics()#IMMUT.graphics_data)
    #MEMBALLOON = guest.create_memballoon()#IMMUT.memballoon_data)
    RNG = guest.create_rng()#IMMUT.rng_data)
    #METADATA = guest.create_metadata()#IMMUT.metadata_data)

    promptline = '_________________________________________\n'
    prompt = promptline +'> '

    # what kind of configuration should be done
    mode = "both"
    all_modes = ['guest', 'host', 'both']
    overwrite = "off"
    overwrite_options = ['on', 'off']

    dataprompt = {
        'name': None,
        'vcpu': None,
        'memory': None,
        'machine': None,
        'bootdev': None,
        'cdrom': None,
        'mainconf': conffile,
        'hvconf': hvfile,
        'hvselected': None,
        'path': '/var/lib/libvirt/images',
        'orverwrite': 'off',
        }

    # default os
    listosdef = ({
        'arch': "x86_64",
        'machine': "pc-q35-6.2",
        'boot_dev': 'hd',
    })

    # show which configuration is used by default
    line1 = line2 = ""
    if os.path.isfile(conffile):
        line1 = util.esc('green')+'Main Configuration: '+util.esc('reset')+conffile+'\n'
    if os.path.isfile(hvfile):
        line2 = util.esc('green')+'Hypervisor Configuration: '+util.esc('reset')+hvfile+'\n'

    prompt = promptline+line1+line2+'\n'+'> '

    def check_user_settings(self, virtum):
        """
        Check if the user as set some stuff, if yes use it
        only usefull for Guest setting
        """
        vcpuuser = self.dataprompt.get('vcpu')
        if vcpuuser != None:
            self.vcpu = guest.create_cpu({'vcpu': vcpuuser})
        else:
            self.vcpu = guest.create_cpu(virtum.vcpu)

        nameuser = self.dataprompt.get('name')
        if nameuser != None:
            self.name = guest.create_name({'VM_name': nameuser})
            self.callsign = nameuser
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

        cdrom = self.dataprompt.get('cdrom')
        if cdrom != None:
            self.cdrom = guest.create_cdrom({'source_file': cdrom})

        overwrite = self.dataprompt.get('overwrite')
        if overwrite != None:
            self.overwrite = overwrite

    def update_prompt(self, args):
        """
        update prompt with value set by user
        """
        line1 = line2 = line3 = line4 = line5 = line6 = line7 = line8 = line9 = line10 = line11 = ""
        self.promptline = '---------- User Settings ----------\n'

        # update prompt with all values
        name = self.dataprompt.get('name')
        if name != None:
            line1 = util.esc('green')+'Name: '+util.esc('reset')+name+'\n'

        vcpu = self.dataprompt.get('vcpu')
        if vcpu != None:
            line2 = util.esc('green')+'Vcpu: '+util.esc('reset')+vcpu+'\n'

        memory = self.dataprompt.get('memory')
        if memory != None:
            line3 = util.esc('green')+'Memory: '+util.esc('reset')+memory+' Gib\n'

        machine = self.dataprompt.get('machine')
        if machine != None:
            line4 = util.esc('green')+'Machine Type: '+util.esc('reset')+machine+'\n'

        bootdev = self.dataprompt.get('bootdev')
        if bootdev != None:
            line5 = util.esc('green')+'Boot Device: '+util.esc('reset')+bootdev+'\n'

        diskpath = self.dataprompt.get('path')
        if diskpath != None:
            line6 = util.esc('green')+'Disk Path: '+util.esc('reset')+diskpath+'\n'

        mainconf = self.dataprompt.get('mainconf')
        if mainconf != None:
            line7 = util.esc('green')+'Main Configuration: '+util.esc('reset')+mainconf+'\n'

        hvconf = self.dataprompt.get('hvconf')
        if hvconf != None:
            line8 = util.esc('green')+'Hypervisor Configuration: '+util.esc('reset')+hvconf+'\n'

        hvselected = self.dataprompt.get('hvselected')
        if hvselected != None:
            line9 = util.esc('green')+'Hypervisor Selected: '+util.esc('reset')+hvselected+'\n'

        overwrite = self.dataprompt.get('overwrite')
        if overwrite != None:
            line10 = util.esc('green')+'Overwrite: '+util.esc('reset')+overwrite+'\n'

        cdrom = self.dataprompt.get('cdrom')
        if cdrom != None:
            line11 = util.esc('green')+'CD/DVD File: '+util.esc('reset')+cdrom+'\n'
            # switch to bootdev cdrom if an iso is selected
            bootdev = "cdrom"
            line5 = util.esc('green')+'Boot Device: '+util.esc('reset')+bootdev+'\n'
            self.dataprompt.update({'bootdev': bootdev})

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
        if args == 'mainconf':
            self.dataprompt.update({'config': mainconf})
        if args == 'hvconf':
            self.dataprompt.update({'config': hvconf})
        if args == 'hvselected':
            self.dataprompt.update({'config': hvselected})
        if args == 'overwrite':
            self.dataprompt.update({'overwrite': overwrite})
        if args == 'cdrom':
            self.dataprompt.update({'cdrom': cdrom})

        self.prompt = self.promptline+line7+line8+line9+line10+line1
        self.prompt += line2+line3+line4+line5+line11+line6+'\n'+'> '

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
        self.hostfs = ""
        self.cdrom = ""
        self.fw_info = fw.default_firmware_info()

        # prefile STORAGE_DATA in case of...
        self.STORAGE_DATA = {
            # XML part
            'disk_type': 'file',
            'disk_cache': '',
            'disk_target': 'vda',
            'disk_bus': 'virtio',
            'format': '',
            'unit': 'G',
            'capacity': '20',
            'cluster_size': '1024k',
            'lazy_refcounts': '',
            'preallocation': '',
            'compression_type': 'zlib',
            'encryption': '',
            #'password': '',
        }
        # This dict is the recommended settings for storage
        self.STORAGE_DATA_REC = {}

        # prefile host_filesystem
        self.host_filesystem = {
            'fmode': '644',
            'dmode': '755',
            'target_dir': '/tmp/',
            'source_dir': '/tmp/host',
        }

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
                elif item == "host_filesystem":
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == "fmode":
                                self.host_filesystem['fmode'] = valuei
                            elif datai == "dmode":
                                self.host_filesystem['dmode'] = valuei
                            elif datai == "source_dir":
                                self.host_filesystem['source_dir'] = valuei
                            elif datai == "target_dir":
                                self.host_filesystem['target_dir'] = valuei
                            else:
                                util.print_error("Unknow parameter in host_filesystem section")
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
            # there is no diff if no user setting
            if self.STORAGE_DATA['encryption'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk Encryption"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA_REC['encryption']
                self.toreport[nestedindex]['set'] = self.STORAGE_DATA['encryption']
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
            for _count in range(1, 6):
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
        util.print_data("Total Memory present", str(util.bytes_to_gibibytes(virtual_memory.total))+"Gb")

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

            name = self.dataprompt.get('name')

            # computation setup
            scenario = s.Scenarios()
            computation = scenario.computation(name)

            self.callsign = computation.name['VM_name']
            self.name = guest.create_name(computation.name)

            # Check user setting
            self.check_user_settings(computation)
            cfg_store = configstore.create_config_store(self, computation, hypervisor, self.overwrite)
            if cfg_store is None:
                return

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
            fw_features = ['secure-boot']
            firmware = fw.find_firmware(self.fw_info, arch=self.listosdef['arch'], features=fw_features, interface='uefi')
            if firmware:
                self.loader = firmware

            self.STORAGE_DATA['storage_name'] = self.callsign
            self.STORAGE_DATA_REC['path'] = self.diskpath['path']
            self.STORAGE_DATA_REC['preallocation'] = "off"
            self.STORAGE_DATA_REC['encryption'] = "off"
            self.STORAGE_DATA_REC['disk_cache'] = "unsafe"
            self.STORAGE_DATA_REC['lazy_refcounts'] = "on"
            self.STORAGE_DATA_REC['format'] = "raw"
            self.filename = self.callsign+".xml"
            self.check_storage()
            self.disk = guest.create_xml_disk(self.STORAGE_DATA)

            # transparent hugepages doesnt need any XML config
            self.hugepages = ""

            if (self.mode != "guest" or self.mode == "both") and util.check_iam_root() is True:
                util.print_summary("Host Section")
                # Create the Virtual Disk image
                host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                host.transparent_hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("enable", "disable")
                host.swappiness("0")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                host.host_end(self.toreport, self.conffile)

            if self.mode != "host" or self.mode == "both":
                final_step_guest(cfg_store, self)

            show_how_to_use(cfg_store.get_path()+"domain.xml")

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

            name = self.dataprompt.get('name')

            # BasicConfiguration
            scenario = s.Scenarios()
            desktop = scenario.desktop(name)

            self.callsign = desktop.name['VM_name']
            self.name = guest.create_name(desktop.name)

            # Check user setting
            self.check_user_settings(desktop)

            cfg_store = configstore.create_config_store(self, desktop, hypervisor, self.overwrite)
            if cfg_store is None:
                return

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
            fw_features = ['secure-boot']
            firmware = fw.find_firmware(self.fw_info, arch=self.listosdef['arch'], features=fw_features, interface='uefi')

            self.STORAGE_DATA['storage_name'] = self.callsign
            self.STORAGE_DATA_REC['path'] = self.diskpath['path']
            self.STORAGE_DATA_REC['preallocation'] = "metadata"
            self.STORAGE_DATA_REC['encryption'] = "off"
            self.STORAGE_DATA_REC['disk_cache'] = "none"
            self.STORAGE_DATA_REC['lazy_refcounts'] = "off"
            self.STORAGE_DATA_REC['format'] = "qcow2"
            self.filename = desktop.name['VM_name']+".xml"
            self.check_storage()
            self.disk = guest.create_xml_disk(self.STORAGE_DATA)

            # host filesystem
            self.hostfs = guest.create_host_filesystem(self.host_filesystem)

            # transparent hugepages doesnt need any XML config
            self.hugepages = ""

            if (self.mode != "guest" or self.mode == "both") and util.check_iam_root() is True:
                util.print_summary("Host Section")
                # Create the Virtual Disk image
                host.create_storage_image(self.STORAGE_DATA)
                # Prepare the host system
                host.transparent_hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("enable", "enable")
                host.swappiness("35")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("mq-deadline")
                host.host_end(self.toreport, self.conffile)

            if self.mode != "host" or self.mode == "both":
                final_step_guest(cfg_store, self)

            show_how_to_use(cfg_store.get_path()+"domain.xml")

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

            if util.cmd_exists("sevctl") is False:
                util.print_error("Please install sevctl tool")
                return

            hypervisor = hv.select_hypervisor()
            if not hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            # SEV information
            sev_info = host.sev_info(hypervisor)

            if not sev_info.sev_supported:
                util.print_error("Selected hypervisor ({}) does not support SEV".format(hypervisor.name))
                return

            name = self.dataprompt.get('name')

            # BasicConfiguration
            scenario = s.Scenarios()
            securevm = scenario.secure_vm(name, sev_info)

            self.callsign = securevm.name['VM_name']
            self.name = guest.create_name(securevm.name)

            # Check user setting
            self.check_user_settings(securevm)

            cfg_store = configstore.create_config_store(self, securevm, hypervisor, self.overwrite)
            if cfg_store is None:
                return

            self.cpumode = guest.create_cpumode_pass(securevm.cpumode)
            self.power = guest.create_power(securevm.power)
            self.ondef = guest.create_ondef(securevm.ondef)
            self.network = guest.create_interface(securevm.network)
            self.tpm = guest.create_tpm(securevm.tpm)
            self.features = guest.create_features(securevm.features)
            self.clock = guest.create_clock(securevm.clock)
            #self.iothreads = guest.create_iothreads(securevm.iothreads)
            # disable as this permit run some stuff on some other host CPU
            self.iothreads = ""
            self.video = guest.create_video(securevm.video)
            self.controller = guest.create_controller(self.listosdef)
            self.inputkeyboard = guest.create_input(securevm.inputkeyboard)
            self.inputmouse = ""

            # recommended setting for storage
            self.STORAGE_DATA_REC['path'] = self.diskpath['path']
            self.STORAGE_DATA_REC['preallocation'] = "metadata"
            self.STORAGE_DATA_REC['encryption'] = "on"
            self.STORAGE_DATA_REC['disk_cache'] = "writethrough"
            self.STORAGE_DATA_REC['lazy_refcounts'] = "on"
            self.STORAGE_DATA_REC['format'] = "qcow2"
            self.STORAGE_DATA['storage_name'] = self.callsign
            self.check_storage()
            self.disk = guest.create_xml_disk(self.STORAGE_DATA)

            # transparent hugepages doesnt need any XML config
            self.hugepages = ""

            self.custom = ["loader",]
            # Find matching firmware
            if sev_info.es_supported():
                fw_features = ['amd-sev-es']
            else:
                fw_features = ['amd-sev']

            firmware = fw.find_firmware(self.fw_info, arch=self.listosdef['arch'], features=fw_features, interface='uefi')
            if firmware:
                self.custom = ["loader"]
                self.loader = firmware
                self.loader_type = 'efi'

            # XML File path
            self.filename = self.callsign+".xml"

            if (self.mode != "guest" or self.mode == "both") and util.check_iam_root() is True:
                util.print_summary("Host Section")
                # Create the Virtual Disk image
                host.create_storage_image(self.STORAGE_DATA)
                # Deal with SEV
                util.print_summary("Prepare SEV attestation")
                if sev_info.sev_supported is True:
                    host.kvm_amd_sev(sev_info)

                    #session = None
                    dh_params = None
                    if hypervisor.has_sev_cert():
                        # A host certificate is configured, try to enable remote attestation
                        cert_file = hypervisor.sev_cert_file()
                        policy = sev_info.get_policy()
                        if not sev.sev_prepare_attestation(cfg_store, policy, cert_file):
                            util.print_error("Creation of attestation keys failed!")
                            return
                        session_key = sev.sev_load_session_key(cfg_store)
                        dh_params = sev.sev_load_dh_params(cfg_store)
                        sev_info.set_attestation(session_key, dh_params)
                        securevm.secure_vm_update(sev_info)

                    self.security = guest.create_security(securevm.security)

                # Prepare the host system
                # Transparent hugepages
                host.transparent_hugepages()
                # enable/disable ksm | enable/disable merge across
                host.manage_ksm("disable", "")
                host.swappiness("0")
                # mq-deadline / kyber / bfq / none
                host.manage_ioscheduler("bfq")
                # END of the config
                host.host_end(self.toreport, self.conffile)

            if self.mode != "host" or self.mode == "both":
                final_step_guest(cfg_store, self)

            show_how_to_use(cfg_store.get_path()+"domain.xml")

    def do_name(self, args):
        """
        Define the Virtual Machine name
        """
        if args == "":
            print("Please select a correct Virtual Machine name")
        else:
            name = {
                'name': args,
                }
            self.dataprompt.update({'name': name['name']})
            self.update_prompt(name['name'])

    def do_machine(self, args):
        """
        Define the machine type
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

    def do_vcpu(self, args):
        """
        Set the VCPU for the VM definition
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

    def do_diskpath(self, args):
        """
        Define the path directory to store the Virtual Machine image
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

    def do_bootdev(self, args):
        """
        Select the boot device
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

    def do_cdrom(self, args):
        """
        Select the Source file to the CDROM/DVD ISO file
        """
        file = args
        if os.path.isfile(file):
            cdrom = {
                'source_file': file,
            }
            self.dataprompt.update({'cdrom': cdrom['source_file']})
            self.update_prompt(cdrom['source_file'])
        else:
            util.print_error("CDROM/DVD ISO source file " +file +" Doesnt exist!")

    def do_memory(self, args):
        """
        Set Memory size, should be in Gib
        """
        if args.isdigit() is False:
            print("Please select a correct memory value (GiB)")
        else:
            memory = {
                'memory': args,
            }
            self.dataprompt.update({'memory': memory['memory']})
            self.update_prompt(memory['memory'])

    def file_complete(self, text, line, begidx, endidx, ext):
        """
        auto completion to find ext files in current path
        """
        all_files = find_ext_file(ext)
        if not text:
            completions = all_files[:]
        else:
            completions = [f for f in all_files if f.startswith(text)]
        return completions

    def complete_conf(self, text, line, begidx, endidx):
        return self.file_complete(text, line, begidx, endidx, ".yaml")

    def complete_hvconf(self, text, line, begidx, endidx):
        return self.file_complete(text, line, begidx, endidx, ".yaml")

    def complete_cdrom(self, text, line, begidx, endidx):
        return self.file_complete(text, line, begidx, endidx, ".iso")

    def do_mode(self, args):
        """
        Select if:
        - XML guest configuration should be done
        - host configuration
        - both should be done (default)
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

    def do_overwrite(self, args):
        """
        Overwrite mode allow you to overwrite previous config (XML and config store)
        """
        overwrite = args
        if overwrite not in self.overwrite_options:
            print("on / off")
        else:
            overwrite = args
            config = {'overwrite': overwrite,}
            self.dataprompt.update({'overwrite': config['overwrite']})
            self.update_prompt(config['overwrite'])

    def do_conf(self, args):
        """
        Select the yaml configuration file
        """
        file = args
        if os.path.isfile(file):
            Cmd.file = file
            util.validate_yaml_file(Cmd.file)
            self.conffile = file
            config = {
                'mainconf': file,
            }
            self.dataprompt.update({'mainconf': config['mainconf']})
            self.update_prompt(config['mainconf'])
        else:
            util.print_error("File " +file +" Doesnt exist!")

    def do_hvconf(self, args):
        """
        Load Hypervisor configuration
        """
        file = args
        if os.path.isfile(file):
            util.validate_yaml_file(file)
            self.hvfile = file
            hv.load_hypervisors(self.hvfile)
            config = {
                'hvconf': file,
            }
            self.dataprompt.update({'hvconf': config['hvconf']})
            self.update_prompt(config['hvconf'])
        else:
            util.print_error("File " +file +" Doesnt exist!")

    def do_hvlist(self, args):
        """
        List available hypervisor configurations
        """
        if self.check_conffile() is not False:
            self.basic_config()
            hv.list_hypervisors()

    def do_hvselect(self, args):
        """
        Set hypervisor for which VMs are configured
        """
        if self.check_conffile() is not False:
            self.basic_config()
            name = args.strip()
            config = {
                'hvselected': name,
            }
            if not hv.set_default_hv(name):
                util.print_error("Setting hypervisor failed")
                return
            self.dataprompt.update({'hvselected': config['hvselected']})
            self.update_prompt(config['hvselected'])

    def do_quit(self, args):
        """
        Exit the application
        Shorthand: Ctrl-D
        """
        # French Flag :)
        print(util.esc('blue')+'Bye'+util.esc('white')+'Bye'+util.esc('red')+'Bye'+util.esc('reset'))
        return True

    do_EOF = do_quit
