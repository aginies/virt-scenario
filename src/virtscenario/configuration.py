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
configuration
"""

import os
import yaml
import subprocess
import virtscenario.firmware as fw
import virtscenario.dict as c
import virtscenario.util as util
import virtscenario.guest as guest
import virtscenario.hypervisors as hv

conffile_locations = [
    '/etc/virt-scenario',
    '/etc',
    '~/.local/etc',
    '.'
]

conffile_name = 'virtscenario.yaml'
hvfile_name = 'virthosts.yaml'

def find_file(name):
    """
    find file
    """
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

class Configuration():
    """
    all stuff relative to configuration
    """
    conffile = find_conffile()
    hvfile = find_hvfile()

    # TOLOOK AFTER MARCH PROTO
    if util.check_iam_root():
        vm_config_store = '/etc/virt-scenario/vmconfig'
    else:
        vm_config_store = '~/.local/virtscenario/'
    emulator = None
    inputkeyboard = ""
    inputmouse = ""
    xml_all = None
    vcpu = name = diskpath = memory = osdef = ondef = cpumode = power = watchdog = ""
    audio = usb = disk = features = clock = network = filename = tpm = iothreads = ""
    callsign = custom = security = video = controller = hugepages = toreport = ""
    loader = config = fw_info = vm_config = cdrom = vnet = hostfs = vmimage = ""
    STORAGE_DATA = STORAGE_DATA_REC = host_filesystem = ""
    memory_pin = False

    # There is some Immutable in dict for the moment...
    #IMMUT = immut.Immutable()
    CONSOLE = guest.create_console()#IMMUT.console_data)
    CHANNEL = guest.create_channel()#IMMUT.channel_data)
    GRAPHICS = guest.create_graphics()#IMMUT.graphics_data)
    #MEMBALLOON = guest.create_memballoon()#IMMUT.memballoon_data)
    RNG = guest.create_rng()#IMMUT.rng_data)
    #METADATA = guest.create_metadata()#IMMUT.metadata_data)

    # what kind of configuration should be done; default is both mode
    mode = "both"
    all_modes = ['guest', 'host', 'both']
    # by default set some value as off
    overwrite = force_sev = "off"
    on_off_options = ['on', 'off']

    dataprompt = {
        'name': None,
        'vcpu': None,
        'memory': None,
        'machine': None,
        'boot_dev': None,
        'vnet': None,
        'cdrom': None,
        'mainconf': conffile,
        'hvconf': hvfile,
        'hvselected': None,
        'path': '/var/lib/libvirt/images',
        'orverwrite': 'off',
        'cluster_size': None,
        'disk_target': None,
        'lazy_refcounts': None,
        'disk_cache': None,
        'preallocation': None,
        'encryption': None,
        'capacity': None,
        }

    # default os
    listosdef = {
        'arch': "x86_64",
        'machine': "pc-q35-6.2",
        'boot_dev': 'hd',
    }

    def check_conffile(self):
        """
        check if the configuration file is present
        """
        if os.path.isfile(self.conf.conffile) is False:
            util.print_error(self.conf.conffile+" configuration Yaml file Not found!")
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
        self.network = ""
        self.vnet = "default"
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
        self.xmldata = ""
        self.fw_info = fw.default_firmware_info()
        self.nothing_to_report = True

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
            'cluster_size': '1024',
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

        CONSOLE = guest.create_console()#IMMUT.console_data)
        CHANNEL = guest.create_channel()#IMMUT.channel_data)
        GRAPHICS = guest.create_graphics()#IMMUT.graphics_data)
        #MEMBALLOON = guest.create_memballoon()#IMMUT.memballoon_data)
        RNG = guest.create_rng()#IMMUT.rng_data)

        # BasicConfiguration
        # pre filed in case of...
        data = c.BasicConfiguration()
        self.emulator = guest.create_emulator(data.emulator("/usr/bin/qemu-system-x86_64"))
        self.inputkeyboard = guest.create_input(data.input("keyboard", "virtio"))
        self.inputmouse = guest.create_input(data.input("mouse", "virtio"))

        # Using virtscenario.yaml to file some VAR
        with open(self.conf.conffile) as file:
            config = yaml.full_load(file)
            # parse all section of the yaml file
            for item, value in config.items():
                # check mathing section
                if item == "hypervisors":
                    for dall in value:
                        for datai, valuei in dall.items():
                            if datai == 'hvconf':
                                self.conf.hvfile = valuei
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
                                self.conf.listosdef.update({'arch': valuei})
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

        hv.load_hypervisors(self.conf.hvfile)

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
            self.STORAGE_DATA['path'] = self.conf.diskpath['path']
        # if path differ grab data to report
        if self.conf.diskpath['path'] != self.STORAGE_DATA['path']:
            # there is no diff is no user setting
            if self.STORAGE_DATA['path'] != "":
                nestedindex += 1
                self.toreport[nestedindex]['title'] = "Disk path"
                self.toreport[nestedindex]['rec'] = self.STORAGE_DATA['path']
                self.toreport[nestedindex]['set'] = self.conf.diskpath['path']

        # PREALLOCATION
        if self.STORAGE_DATA['preallocation'] is False:
            self.STORAGE_DATA['preallocation'] = "off"
        # no preallocation has been set, using recommended
        # if they differ grab data to report
        if self.STORAGE_DATA['preallocation'] != self.STORAGE_DATA_REC['preallocation']:
            # there is no diff if no user setting
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
            if self.conf.vmimage is None:
                password = util.input_password()
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

        # user specify an image to use
        if self.conf.vmimage is not None:
            output = subprocess.check_output(["qemu-img", "info", self.conf.vmimage])
            output = output.decode("utf-8")
            format_line = [line for line in output.splitlines() if "file format:" in line][0]
            image_format = format_line.split(":")[1].strip()
            self.STORAGE_DATA['format'] = image_format
            self.STORAGE_DATA['source_file'] = self.conf.vmimage
        else:
            self.STORAGE_DATA['source_file'] = self.STORAGE_DATA['path']+"/"+self.callsign+"."+self.STORAGE_DATA['format']

        # Remove index in dict which are empty
        if nestedindex >= 1:
            for _count in range(1, 6):
                if len(self.toreport) != nestedindex:
                    self.toreport.pop(len(self.toreport))
            self.nothing_to_report = False
        else:
            self.nothing_to_report = True

    def set_memory_pin(self, value):
        self.memory_pin = value

    def check_user_settings(self, virtum):
        """
        Check if the user as set some stuff, if yes use it
        only usefull for Guest setting
        """
        #from pprint import pprint; pprint(vars(virtum))
        vcpuuser = self.conf.dataprompt.get('vcpu')
        if vcpuuser != None:
            self.vcpu = guest.create_cpu({'vcpu': vcpuuser})
        else:
            self.vcpu = guest.create_cpu(virtum.vcpu)

        nameuser = self.conf.dataprompt.get('name')
        if nameuser != None:
            self.name = guest.create_name({'VM_name': nameuser})
            self.callsign = nameuser
        else:
            self.name = guest.create_name(virtum.name)

        diskpathuser = self.conf.dataprompt.get('path')
        if diskpathuser != None:
            self.conf.diskpath = {'path': diskpathuser}

        clustersize = self.conf.dataprompt.get('cluster_size')
        if clustersize != None:
            self.conf.STORAGE_DATA.update({'cluster_size': clustersize})

        preallocation = self.conf.dataprompt.get('preallocation')
        if preallocation != None:
            self.conf.STORAGE_DATA.update({'preallocation': preallocation })

        encryption = self.conf.dataprompt.get('encryption')
        if encryption != None:
            self.conf.STORAGE_DATA.update({'encryption': encryption })

        disk_cache = self.conf.dataprompt.get('disk_cache')
        if disk_cache != None:
            self.conf.STORAGE_DATA.update({'disk_cache': disk_cache })

        lazy_refcounts = self.conf.dataprompt.get('lazy_refcounts')
        if lazy_refcounts != None:
            self.conf.STORAGE_DATA.update({'lazy_refcounts': lazy_refcounts })

        disk_target = self.conf.dataprompt.get('disk_target')
        if disk_target != None:
            self.conf.STORAGE_DATA.update({'disk_target': disk_target })

        capacity = self.conf.dataprompt.get('capacity')
        if capacity != None:
            self.conf.STORAGE_DATA.update({'capacity': capacity })

        memoryuser = self.conf.dataprompt.get('memory')
        if memoryuser != None:
            mem_dict = {
                'mem_unit': 'Gib',
                'max_memory': memoryuser,
                'current_mem_unit': 'Gib',
                'memory': memoryuser,
                }
            if virtum.memory_pin:
                mem_dict['pin'] = virtum.memory_pin
            self.memory = guest.create_memory(mem_dict)
        else:
            self.memory = guest.create_memory(virtum.memory)

        cdrom = self.conf.dataprompt.get('dvd')
        if cdrom != None:
            self.cdrom = guest.create_cdrom({'source_file': cdrom})
            # if CD/DVD selected swith boot dev to cdrom by default
            self.conf.listosdef.update({'boot_dev': 'cdrom'})

        vmimage = self.conf.dataprompt.get('vmimage')
        if vmimage != "":
            self.conf.vmimage = vmimage

        machineuser = self.conf.dataprompt.get('machine')
        bootdevuser = self.conf.dataprompt.get('boot_dev')
        if machineuser != None:
            self.conf.listosdef.update({'machine': machineuser})
        if bootdevuser != None:
            self.conf.listosdef.update({'boot_dev': bootdevuser})
        self.osdef = guest.create_osdef(self.conf.listosdef)

        vnet = self.conf.dataprompt.get('vnet')
        if vnet != None:
            self.vnet = vnet

        overwrite = self.conf.dataprompt.get('overwrite')
        if overwrite != None:
            self.conf.overwrite = overwrite

        return self
