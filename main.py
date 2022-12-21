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
import util
import proto_guest as guest
import scenario as s
import immutable as immut

def create_default_domain_xml(xmlfile):
    """
    create the VM domain XML
    """
    cmd1 = "virt-install --print-xml --virt-type kvm --arch x86_64 --machine pc-q35-6.2 "
    cmd2 = "--osinfo sles12sp5 --rng /dev/urandom --network test_net >" +xmlfile
    util.system_command(cmd1 + cmd2)

def create_from_template(finalfile, xml_all):
    """
    create the VM domain XML from all template input given
    """
    print("Create Then XML VM configuration " +finalfile)
    with open(finalfile, 'w') as file_h:
        file_h.write(xml_all)


def validate_xml(xmlfile):
    """
    validate the generated file
    """
    cmd = "virt-xml-validate "+xmlfile
    out, errs = util.system_command(cmd)
    if errs:
        print(errs)
    print(out)


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
    prompt = 'virt-scenario > '
    introl = {}
    introl[0] = "\n"+util.esc('32;1;1') +"virt-scenario "+util.esc(0)+ "Interactive Terminal!\n"
    introl[1] = " Prepare a Libvirt XML guest config and the host to run a customized guest\n"
    introl[2] = util.esc('31;1;1')+"\n WARNING:"+util.esc(0)+" not yet ready at all......\n\n"
    introl[3] = " Source code: https://github.com/aginies/virt-scenario\n"
    intro = ''
    for line in range(4):
        intro += introl[line]

    # There is some Immutable in dict for the moment...
    IMMUT = s.Immutable()
    CONSOLE = guest.create_console(IMMUT.console_data)
    CHANNEL = guest.create_channel(IMMUT.channel_data)
    GRAPHICS = guest.create_graphics(IMMUT.graphics_data)
    VIDEO = guest.create_video(IMMUT.video_data)
    MEMBALLOON = guest.create_memballoon(IMMUT.memballoon_data)
    RNG = guest.create_rng(IMMUT.rng_data)
    METADATA = guest.create_metadata(IMMUT.metadata_data)

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

    def help_computation(self):
        """
        show some help on computation scenario
        """
        print("Will prepare a Guest XML config for computation")

    def do_computation(self, args):
        """
        computation
        """
        # BasicConfiguration
        data = s.BasicConfiguration()
        scenario = s.Scenario()
        computation = scenario.computation()
        name = guest.create_name(computation.name)
        memory = guest.create_memory(computation.memory)
        vcpu = guest.create_cpu(computation.vcpu)
        cpumode = guest.create_cpumode(computation.cpumode)
        power = guest.create_power(computation.power)

        # need to declare all other stuff
        osdef = guest.create_os(immut.OS_DATA)
        features = guest.create_features(immut.FEATURES_DATA)
        clock = guest.create_clock(immut.CLOCK_DATA)
        ondef = guest.create_on(immut.ON_DATA)
        emulator = guest.create_emulator(data.emulator("/usr/bin/qemu-system-x86_64"))
        disk = guest.create_disk(immut.DISK_DATA)
        interface = guest.create_interface(immut.INTERFACE_DATA)
        input1 = guest.create_input(data.input("keyboard", "virtio"))
        input2 = guest.create_input(data.input("mouse", "virtio"))
        audio = guest.create_audio(data.audio("ac97"))
        watchdog = guest.create_watchdog(data.watchdog("i6300esb", "poweroff"))
        tpm = guest.create_tpm(immut.TPM_DATA)

        # final XML creation
        xml_all = "<!-- WARNING: THIS IS A GENERATED FILE FROM VIRT-SCENARIO -->\n"
        # start the domain definition
        xml_all += "<domain type='kvm'>\n"
        xml_all += name+self.METADATA+memory+vcpu+osdef+features+cpumode+clock+ondef+power
        # all below must be in devices section
        xml_all += "<devices>\n"
        xml_all += emulator+disk+interface+self.CONSOLE+self.CHANNEL+input1+input2
        xml_all += self.GRAPHICS+audio+self.VIDEO+watchdog+self.MEMBALLOON+self.RNG+tpm
        # close the device section
        xml_all += "</devices>\n"
        # close domain section
        xml_all += "</domain>\n"

        create_from_template("VMb.xml", xml_all)
        validate_xml("VMb.xml")

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
