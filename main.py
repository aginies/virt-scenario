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
import os
import util
import proto_guest as guest
import scenario as s
import immutable as immut
import qemulist
#import summary

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
    util.print_summary("\nCreate Then XML VM configuration")
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

def final_step(data):
    """
    final step
    create the file and check it is ok
    """
    # final XML creation
    # start the domain definition
    xml_all = ""
    # first line must be a warning, kvm by default
    xml_all = "<!-- WARNING: THIS IS A GENERATED FILE FROM VIRT-SCENARIO -->\n"
    xml_all += "<domain type='kvm'>\n"
    xml_all += data.name+data.memory+data.vcpu+data.osdef
    xml_all += data.features+data.cpumode+data.clock
    xml_all += data.ondef+data.power+data.iothreads
    # all below must be in devices section
    xml_all += "<devices>\n"
    xml_all += data.emulator+data.disk+data.network+data.CONSOLE
    xml_all += data.CHANNEL+data.input1+data.input2
    xml_all += data.GRAPHICS+data.VIDEO+data.RNG+data.watchdog
    # close the device section
    xml_all += "</devices>\n"
    # close domain section
    xml_all += "</domain>\n"

    create_from_template(data.filename, xml_all)
    #summary.show_from_xml(data.filename)
    validate_xml(data.filename)

def show_summary_before(data):
    """
    Show the XML config
    """
    util.print_data("Name", str(data.name))
    util.print_data("Vcpu", str(data.vcpu))
    data.iothreads and util.print_data("Iothreads", str(data.iothreads))
    util.print_data("Memory", str(data.memory))
    util.print_data("OS", str(data.osdef))
    data.features and util.print_data("Features", str(data.features))
    util.print_data("Clock", str(data.clock))
    data.ondef and util.print_data("On", str(data.ondef))
    data.power and util.print_data("Power", str(data.power))
    # devices
    util.print_data("Emulator", str(data.emulator))
    data.CHANNEL and util.print_data("Channel", str(data.CHANNEL))
    util.print_data("Input", str(data.input1)+str(data.input2))
    data.GRAPHICS and util.print_data("Graphics", str(data.GRAPHICS))
    data.VIDEO and util.print_data("Video", str(data.VIDEO))
    data.audio and util.print_data("Audio", str(data.audio))
    data.RNG and util.print_data("Random", str(data.RNG))
    data.disk and util.print_data("Disk", str(data.disk))
    data.network and util.print_data("Network", str(data.network))
    data.CONSOLE and util.print_data("Console", str(data.CONSOLE))
    data.watchdog and util.print_data("Watchdog", str(data.watchdog))
    data.tpm and util.print_data("TPM", str(data.tpm))

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
    introl[0] = "\n"+util.esc('32;1;1') +" virt-scenario "+util.esc(0)+ "Interactive Terminal!\n"
    introl[1] = " Prepare a Libvirt XML guest config and the host to run a customized guest\n"
    introl[2] = "\n"+" Only computation and desktop are available for now\n"
    introl[3] = util.esc('31;1;1')+"\n WARNING:"+util.esc(0)+" This is under Heavy Devel...\n\n"
    introl[4] = " Source code: https://github.com/aginies/virt-scenario\n"
    introl[5] = " Report bug: https://github.com/aginies/virt-scenario/issues\n"
    intro = ''
    for line in range(6):
        intro += introl[line]

    # There is some Immutable in dict for the moment...
    IMMUT = immut.Immutable()
    CONSOLE = guest.create_console(IMMUT.console_data)
    CHANNEL = guest.create_channel(IMMUT.channel_data)
    GRAPHICS = guest.create_graphics(IMMUT.graphics_data)
    VIDEO = guest.create_video(IMMUT.video_data)
    MEMBALLOON = guest.create_memballoon(IMMUT.memballoon_data)
    RNG = guest.create_rng(IMMUT.rng_data)
    METADATA = guest.create_metadata(IMMUT.metadata_data)

    promptline = '_________________________________________\n'
    prompt = promptline +'> '

    dataprompt = {
        'vcpu': None,
        'memory': None,
        'machine': None,
        }

    def check_user_settings(self, desktop):
        """
        Check if the user as set some stuff, if yes use it
        """
        vcpuuser = self.dataprompt.get('vcpu')
        if vcpuuser != None:
            self.vcpu = guest.create_cpu({'vcpu': vcpuuser})
        else:
            self.vcpu = guest.create_cpu(desktop.vcpu)

        memoryuser = self.dataprompt.get('memory')
        if memoryuser != None:
            self.memory = guest.create_memory({
                'mem_unit': 'Gib',
                'max_memory': memoryuser,
                'current_mem_unit': 'Gib',
                'memory': memoryuser,
                })
        else:
            self.memory = guest.create_memory(desktop.memory)

        machineuser = self.dataprompt.get('machine')
        if machineuser != None:
            self.osdef = guest.create_osdef({
                'arch': "x86_64",
                'machine': machineuser,
                'boot_dev': 'hd',
                })
        else:
            self.osdef = guest.create_osdef(desktop.osdef)


    def update_prompt(self, args):
        """
        update prompt with value set by user
        """
        line1 = line2 = line3 = ""
        self.promptline = '---------- User Settings ----------\n'

        # update prompt with all values
        vcpu = self.dataprompt.get('vcpu')
        if vcpu != None:
            line1 = util.esc('32;1;1')+'Vcpu: '+util.esc(0)+vcpu+'\n'

        memory = self.dataprompt.get('memory')
        if memory != None:
            line2 = util.esc('32;1;1')+'Memory: '+util.esc(0)+memory+' Gib\n'

        machine = self.dataprompt.get('machine')
        if machine != None:
            line3 = util.esc('32;1;1')+'Machine Type: '+util.esc(0)+machine+'\n'

        if args == 'vcpu':
            self.dataprompt.update({'vcpu': vcpu})
        if args == 'memory':
            self.dataprompt.update({'memory': memory})
        if args == 'machine':
            self.dataprompt.update({'machine': machine})

        self.prompt = self.promptline+line1+line2+line3+'\n'+'> '

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
        self.disk = ""
        self.features = ""
        self.clock = ""
        self.ondef = ""
        self.network = ""
        self.filename = ""
        self.tpm = ""
        self.iothreads = ""

        # BasicConfiguration
        data = s.BasicConfiguration()
        self.emulator = guest.create_emulator(data.emulator("/usr/bin/qemu-system-x86_64"))
        self.input1 = guest.create_input(data.input("keyboard", "virtio"))
        self.input2 = guest.create_input(data.input("mouse", "virtio"))


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
        self.name = guest.create_name(computation.name)
        self.cpumode = guest.create_cpumode(computation.cpumode)
        self.power = guest.create_power(computation.power)
        self.osdef = guest.create_osdef(computation.osdef)
        self.ondef = guest.create_ondef(computation.ondef)
        self.watchdog = guest.create_watchdog(computation.watchdog)
        self.disk = guest.create_disk(computation.disk)
        self.network = guest.create_interface(computation.network)
        self.features = guest.create_features(computation.features)
        self.clock = guest.create_clock(computation.clock)
        self.iothreads = guest.create_iothreads(computation.iothreads)

        # Check user setting
        self.check_user_settings(computation)

        self.filename = computation.name['VM_name']+".xml"
        show_summary_before(self)
        final_step(self)

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
        self.name = guest.create_name(desktop.name)
        self.cpumode = guest.create_cpumode(desktop.cpumode)
        self.power = guest.create_power(desktop.power)
        self.osdef = guest.create_osdef(desktop.osdef)
        self.ondef = guest.create_ondef(desktop.ondef)
        self.disk = guest.create_disk(desktop.disk)
        self.network = guest.create_interface(desktop.network)
        self.audio = guest.create_audio(desktop.audio)
        self.tpm = guest.create_tpm(desktop.tpm)
        self.features = guest.create_features(desktop.features)
        self.clock = guest.create_clock(desktop.clock)
        self.iothreads = guest.create_iothreads(desktop.iothreads)

        # Check user setting
        self.check_user_settings(desktop)

        # need to declare all other stuff

        self.filename = desktop.name['VM_name']+".xml"
        show_summary_before(self)
        final_step(self)

    def do_machinetype(self, args):
        """
        select machine
        """
        machine = {
            'machine': args,
            }
        self.dataprompt.update({'machine': machine['machine']})
        self.update_prompt(machine['machine'])

    def complete_machinetype(self, text, line, begidx, endidx):
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
        vcpu number
        """
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

    def do_memory(self, args):
        """
        memory
        """
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
        Quit pvirsh
        """
        print('Exit the application. Shorthand: Ctrl-D.')

    do_EOF = do_quit
    help_EOF = help_quit

# call main
main()
