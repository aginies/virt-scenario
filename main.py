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
import util
import guest
import scenario as s
import configuration as c
import immutable as immut
import qemulist
import xmlutil
import host

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

def create_xml_config(data):
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
    xml_all += data.features+data.cpumode+data.clock
    xml_all += data.ondef+data.power+data.iothreads
    # all below must be in devices section
    xml_all += "\n  <devices>"
    xml_all += data.emulator+data.CONTROLLER
    xml_all += data.disk+data.network+data.CONSOLE
    xml_all += data.CHANNEL+data.input1+data.input2
    xml_all += data.GRAPHICS+data.video+data.RNG+data.watchdog
    xml_all += data.usb+data.tpm
    # close the device section
    xml_all += "</devices>\n"
    # close domain section
    xml_all += "</domain>\n"

    # create the file from the template and setting
    create_from_template(data.filename, xml_all)
    if "loader" in data.custom:
        xmlutil.add_loader_nvram(data.filename, qemulist.OVMF_PATH+"/ovmf-x86_64-smm-opensuse-code.bin", qemulist.OVMF_VARS+"/"+data.callsign+".VARS")
    ### if "XXXX" in data.custom:
    # TODO

def final_step_guest(data):
    """
    show setting from xml
    create the XML config
    validate the XML file
    """
    xmlutil.show_from_xml(data.filename)
    create_xml_config(data)
    validate_xml(data.filename)
    util.print_summary_ok("Guest XML Configuration is done")

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
    MyPrompt().cmdloop()

class MyPrompt(Cmd):
    """
    prompt Cmd
    """
    # define some None
    emulator = None
    input1 = ""
    input2 = ""
    xml_all = None
    # prompt Cmd
    prompt = 'virt-scenario > '
    introl = {}
    introl[0] = "\n"+util.esc('32;1;1') +" virt-scenario "+util.esc(0)+ "Interactive Terminal!\n\n"
    introl[1] = " Prepare a Libvirt XML guest config and the host to run a customized guest:\n"
    introl[2] = util.esc('34;1;1')+" computation | desktop | securevm"+util.esc(0)+"\n"
    introl[3] = "\n Possible User Settings:\n"
    introl[4] = util.esc('34;1;1')+" name|vcpu|memory|machine|bootdev|diskpath"+util.esc(0)+"\n"
    introl[5] = util.esc('31;1;1')+"\n WARNING:"+util.esc(0)+" This is under Devel...\n"
    introl[6] = " Source code: https://github.com/aginies/virt-scenario\n"
    introl[7] = " Report bug: https://github.com/aginies/virt-scenario/issues\n"
    intro = ''
    for line in range(8):
        intro += introl[line]

    # There is some Immutable in dict for the moment...
    IMMUT = immut.Immutable()
    CONSOLE = guest.create_console()#IMMUT.console_data)
    CHANNEL = guest.create_channel()#IMMUT.channel_data)
    GRAPHICS = guest.create_graphics()#IMMUT.graphics_data)
    MEMBALLOON = guest.create_memballoon()#IMMUT.memballoon_data)
    RNG = guest.create_rng()#IMMUT.rng_data)
    METADATA = guest.create_metadata()#IMMUT.metadata_data)
    CONTROLLER = guest.create_controller()


    promptline = '_________________________________________\n'
    prompt = promptline +'> '

    dataprompt = {
        'name': None,
        'vcpu': None,
        'memory': None,
        'machine': None,
        'bootdev': None,
        'path': '/tmp',
        }

    def check_user_settings(self, vm):
        """
        Check if the user as set some stuff, if yes use it
        """
        vcpuuser = self.dataprompt.get('vcpu')
        if vcpuuser != None:
            self.vcpu = guest.create_cpu({'vcpu': vcpuuser})
        else:
            self.vcpu = guest.create_cpu(vm.vcpu)

        nameuser = self.dataprompt.get('name')
        if nameuser != None:
            self.name = guest.create_name({'VM_name': nameuser})
        else:
            self.name = guest.create_name(vm.name)

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
            self.memory = guest.create_memory(vm.memory)

        # default os
        listosdef = ({
            'arch': "x86_64",
            'machine': "pc-i440fx-6.2",
            'boot_dev': 'hd',
        })

        machineuser = self.dataprompt.get('machine')
        bootdevuser = self.dataprompt.get('bootdev')
        if machineuser != None:
            listosdef.update({'machine': machineuser})
        if bootdevuser != None:
            listosdef.update({'boot_dev': bootdevuser})
        self.osdef = guest.create_osdef(listosdef)

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

    def basic_config(self):
        """
        init the basic configuration
        """
        self.vcpu = ""
        self.memory = ""
        self.osdef = ""
        self.name = ""
        self.ondef = ""
        self.osdef = ""
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
        self.security = ""
        self.video = ""

        # BasicConfiguration
        util.print_summary("Guest Section")
        data = c.BasicConfiguration()
        self.emulator = guest.create_emulator(data.emulator("/usr/bin/qemu-system-x86_64"))
        self.input1 = guest.create_input(data.input("keyboard", "virtio"))
        self.input2 = guest.create_input(data.input("mouse", "virtio"))

        # pre XML file for storage with some value
        self.STORAGE_DATA = {
           # XML part
            'disk_type': 'file',
            'disk_cache': 'none',
            'disk_target': 'vda',
            'disk_bus': 'virtio',
            'format': 'qcow2',
            # host side: qemu-img creation options (-o)
            'allocation': '0',
            'unit': 'G',
            'capacity': '20',
            'cluster_size': '2M',
            'lazy_refcounts': 'on',
            'preallocation': 'off',
            'compression_type': 'zlib',
            'encryption': 'off',
            'password': '',
        }

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
        self.basic_config()
        # computation setup
        scenario = s.Scenarios()
        computation = scenario.computation()
        self.callsign = computation.name['VM_name']
        self.name = guest.create_name(computation.name)
        self.cpumode = guest.create_cpumode_pass(computation.cpumode)
        self.power = guest.create_power(computation.power)
        self.osdef = guest.create_osdef(computation.osdef)
        self.ondef = guest.create_ondef(computation.ondef)
        self.watchdog = guest.create_watchdog(computation.watchdog)
        self.network = guest.create_interface(computation.network)
        self.features = guest.create_features(computation.features)
        self.clock = guest.create_clock(computation.clock)
        self.video = guest.create_video(computation.video)
        self.iothreads = guest.create_iothreads(computation.iothreads)
        self.custom = ["loader",]

        # Check user setting
        self.check_user_settings(computation)

        self.STORAGE_DATA['storage_name'] = self.callsign
        self.STORAGE_DATA['path'] = self.diskpath['path']
        self.STORAGE_DATA['preallocation'] = "off"
        self.STORAGE_DATA['encryption'] = "off"
        self.disk = guest.create_disk(self.STORAGE_DATA)

        self.filename = self.callsign+".xml"
        final_step_guest(self)
        # Create the Virtual Disk image
        host.create_storage_image(self.STORAGE_DATA)
        host.host_end()

    def help_desktop(self):
        """
        show some help on desktop scenario
        """
        print("Will prepare a Guest XML config for Desktop VM")

    def do_desktop(self, args):
        """
        desktop
        """
        self.basic_config()
        # BasicConfiguration
        scenario = s.Scenarios()
        desktop = scenario.desktop()
        self.callsign = desktop.name['VM_name']
        self.name = guest.create_name(desktop.name)
        self.cpumode = guest.create_cpumode_pass(desktop.cpumode)
        self.power = guest.create_power(desktop.power)
        self.osdef = guest.create_osdef(desktop.osdef)
        self.ondef = guest.create_ondef(desktop.ondef)
        self.disk = guest.create_disk(desktop.disk)
        self.network = guest.create_interface(desktop.network)
        self.audio = guest.create_audio(desktop.audio)
        self.usb = guest.create_usb(desktop.usb)
        self.tpm = guest.create_tpm(desktop.tpm)
        self.features = guest.create_features(desktop.features)
        self.clock = guest.create_clock(desktop.clock)
        self.video = guest.create_video(desktop.video)
        self.iothreads = guest.create_iothreads(desktop.iothreads)

        # Check user setting
        self.check_user_settings(desktop)

        self.STORAGE_DATA['storage_name'] = self.callsign
        self.STORAGE_DATA['path'] = self.diskpath['path']
        self.STORAGE_DATA['preallocation'] = "metadata"
        self.STORAGE_DATA['encryption'] = "off"
        self.disk = guest.create_disk(self.STORAGE_DATA)

        self.filename = desktop.name['VM_name']+".xml"
        final_step_guest(self)
        # Create the Virtual Disk image
        host.create_storage_image(self.STORAGE_DATA)
        host.host_end()

    def help_securevm(self):
        """
        show some help on secure VM scenario
        """
        print("Will prepare a Guest XML config and Host for Secure VM")

    def do_securevm(self, args):
        """
        desktop
        """
        self.basic_config()
        # BasicConfiguration
        scenario = s.Scenarios()
        securevm = scenario.secure_vm()
        self.callsign = securevm.name['VM_name']
        self.name = guest.create_name(securevm.name)
        self.cpumode = guest.create_cpumode_pass(securevm.cpumode)
        self.power = guest.create_power(securevm.power)
        self.osdef = guest.create_osdef(securevm.osdef)
        self.ondef = guest.create_ondef(securevm.ondef)
        self.network = guest.create_interface(securevm.network)
        self.tpm = guest.create_tpm(securevm.tpm)
        self.features = guest.create_features(securevm.features)
        self.clock = guest.create_clock(securevm.clock)
        self.iothreads = guest.create_iothreads(securevm.iothreads)
        self.security = guest.create_security(securevm.security)
        self.video = guest.create_video(securevm.video)
        self.custom = ["loader",]

        # Check user setting
        self.check_user_settings(securevm)

        # Ask for the disk password
        password = getpass.getpass("Please enter password to encrypt the VM image: ")
        # Create the XML disk part
        self.STORAGE_DATA['storage_name'] = self.callsign
        self.STORAGE_DATA['path'] = self.diskpath['path']
        self.STORAGE_DATA['encryption'] = "on"
        self.STORAGE_DATA['preallocation'] = "metadata"
        self.STORAGE_DATA['password'] = password
        self.disk = guest.create_disk(self.STORAGE_DATA)

        # XML File path
        self.filename = securevm.name['VM_name']+".xml"
        final_step_guest(self)

        # Prepare the host system
        host.kvm_amd_sev()
        # Create the Virtual Disk image
        host.create_storage_image(self.STORAGE_DATA)
        host.host_end()

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

# call main
main()
