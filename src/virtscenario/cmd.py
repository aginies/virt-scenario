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
Interactive mode for virt-scenario
"""

import os
from cmd import Cmd
import virtscenario.util as util
import virtscenario.scenario as scena
import virtscenario.qemulist as qemulist
import virtscenario.hypervisors as hv
import virtscenario.configuration as configuration

######
# Interactive command
# ####

class Interactive(Cmd):
    """
    Interactive Cmd
    """

    def __init__(self, config):
        """
        Init the Cmd
        """
        self.conf = config
        Cmd.__init__(self)
        self.force_sev = False
        self.gtk = False

        self.promptline = '_________________________________________\n'
        self.prompt = self.promptline +'> '
        self.prompt = 'virt-scenario > '
        lines = []
        lines.append("\n"+util.esc('green') +" virt-scenario "+util.esc('reset')+ "Interactive Terminal!\n\n")
        lines.append(" Setting the virt-scenario Configuration: "+util.esc('blue')+"conf"+util.esc('reset')+"\n")
        lines.append(" Guest/Host/Both mode could be selected using: "+util.esc('blue')+"mode"+util.esc('reset')+"\n")
        lines.append(" Force overwrite previous setting: "+util.esc('blue')+"overwrite"+util.esc('reset')+"\n")
        lines.append("\n Prepare a Libvirt XML guest config and the host to run a customized guest:\n")
        lines.append(util.esc('blue')+" computation | desktop | securevm"+util.esc('reset')+"\n")
        lines.append("\n Possible User Settings For VM are:\n")
        lines.append(util.esc('blue')+" name | vcpu | memory | machine | bootdev | vnet | cdrom | vmimage"+util.esc('reset')+"\n")
        lines.append("\n Hypervisors parameters:\n")
        lines.append(util.esc('blue')+" hconf | hvselect | hvlist | force_sev"+util.esc('reset')+"\n")
        lines.append("\n Storage parameters:\n")
        lines.append(util.esc('blue')+" diskpath| capacity | encryption | format | cache"+util.esc('reset')+"\n")
        lines.append("\n"+" You can overwrite some recommended VM settings editing: "+config.conffile+"\n")
        lines.append("\n Please read the manpage or the README.md file:\n")
        lines.append(" https://github.com/aginies/virt-scenario/blob/main/README.md\n")
        #lines.append(util.esc('red')+"\n WARNING:"+util.esc('reset')+" This is under Devel...\n")
        lines.append(" Source code: https://github.com/aginies/virt-scenario\n")
        lines.append(" Report bug: https://github.com/aginies/virt-scenario/issues\n")

        self.intro = ''.join(lines)
        # show which configuration is used by default
        line1 = line2 = ""
        if os.path.isfile(self.conf.conffile):
            line1 = util.esc('green')+'Main Configuration: '+util.esc('reset')+self.conf.conffile+'\n'
        if os.path.isfile(self.conf.hvfile):
            line2 = util.esc('green')+'Hypervisor Configuration: '+util.esc('reset')+self.conf.hvfile+'\n'
        self.prompt = self.promptline+line1+line2+'\n'+'> '

        hv.load_hypervisors(self.conf.hvfile)
        self.HV_LIST = hv.list_all_hypervisors()

    def update_prompt(self):
        """
        update prompt with value set by user
        """
        options = [('Name', 'name'),
                   ('Vcpu', 'vcpu'),
                   ('Memory', 'memory'),
                   #('Memory Backing', 'memory_backing'),
                   ('Disk Image Format', 'format'),
                   ('Disk Image Size', 'capacity'),
                   ('Disk Cache Mode', 'cache'),
                   ('Image Encryption', 'encryption'),
                   ('Machine Type', 'machine'),
                   ('Boot Device', 'boot_dev'),
                   ('Disk Path', 'path'),
                   ('Force SEV PDH extraction', 'force_sev'),
                   ('Virtual Network', 'vnet'),
                   ('Main Configuration', 'mainconf'),
                   ('Hypervisor Configuration', 'hvconf'),
                   ('Hypervisor Selected', 'hvselected'),
                   ('Overwrite', 'overwrite'),
                   ('CD/DVD File ', 'dvd'),
                   ('VM Image file', 'vmimage')
                  ]

        lines = []
        self.promptline = '---------- User Settings ----------\n'

        for option_name, option_key in options:
            option_value = self.conf.dataprompt.get(option_key)
            if option_value is not None:
                line = util.esc('green') + option_name + ': ' + util.esc('reset') + option_value + '\n'
                if option_key == 'dvd':
                    self.conf.listosdef.update({'boot_dev': 'cdrom'})
                # append to the main line
                lines.append(line)

        output = ''.join(lines)

        self.prompt = self.promptline+output+'\n'+'> '

    def do_computation(self, _args):
        """
        Will prepare the System for a Computation VM
        """
        scena.Scenarios.do_computation(self, True)
        if self.nothing_to_report is False:
            util.to_report(self.toreport, self.conf.conffile)
        util.show_how_to_use(self.callsign)

    def do_securevm(self, _args):
        """
        Will prepare the System for a secure VM
        """
        scena.Scenarios.do_securevm(self, True)
        if self.nothing_to_report is False:
            util.to_report(self.toreport, self.conf.conffile)
        util.show_how_to_use(self.callsign)

    def do_desktop(self, _args):
        """
        Will prepare the System for a desktop VM
        """
        scena.Scenarios.do_desktop(self, True)
        if self.nothing_to_report is False:
            util.to_report(self.toreport, self.conf.conffile)
        util.show_how_to_use(self.callsign)

    def do_shell(self, args):
        """
        Execute a System Command
        """
        out, errs = util.system_command(args)
        if errs:
            print(errs)
        if not out:
            util.print_error(' No output... seems weird...')
        else:
            print(out)

    def do_info(self, _args):
        """
        Show System Info
        """
        import psutil
        util.print_data("Number of Physical cores", str(psutil.cpu_count(logical=False)))
        util.print_data("Number of Total cores", str(psutil.cpu_count(logical=True)))
        cpu_frequency = psutil.cpu_freq()
        util.print_data("Max Frequency", str(cpu_frequency.max)+"Mhz")
        virtual_memory = psutil.virtual_memory()
        util.print_data("Total Memory present", str(util.bytes_to_gibibytes(virtual_memory.total))+"Gb")

    def do_name(self, args):
        """
        Define the Virtual Machine name
        """
        if args == "":
            util.print_error("Please select a correct Virtual Machine name")
            return
        if util.check_name(args):
            name = {
                'name': args,
                }
            self.conf.dataprompt.update({'name': name['name']})
            self.update_prompt()
        else:
            util.print_error("Only AlphaNumeric as Virtual Machine name")

    def do_machine(self, args):
        """
        Define the machine type
        """
        hvselected = self.conf.dataprompt.get('hvselected')
        if hvselected != None:
            self.hypervisor = hv.select_hypervisor()
            self.hypervisor.name = hvselected
            if not self.hypervisor.is_connected():
                util.print_error("No connection to LibVirt, I can not list machine type available.")
                return
            list_m = self.hypervisor.get_all_machine_type()
            if args not in list_m:
                util.print_error("Please select a correct machine Type:")
                print(str(list_m))
            else:
                machine = {
                    'machine': args,
                    }
                self.conf.dataprompt.update({'machine': machine['machine']})
                self.update_prompt()
        else:
            util.print_error("Please select an Hypervisor with 'hvselect'")

    def complete_machine(self, text, _line, _begidx, _endidx):
        """
        auto completion machine type
        """
        list_m = self.hypervisor.get_all_machine_type()
        if not text:
            completions = list_m[:]
        else:
            completions = [f for f in list_m if f.startswith(text)]
        return completions

    def do_vcpu(self, args):
        """
        Set the vCPU for the VM definition
        """
        if args.isdigit() is False:
            util.print_error("Please select a correct vCPU number")
        else:
            vcpu = {
                'vcpu': args,
                }
            self.conf.dataprompt.update({'vcpu': vcpu['vcpu']})
            self.update_prompt()

    def do_diskpath(self, args):
        """
        Define the path directory to store the Virtual Machine image
        """
        if os.path.isdir(args):
            path = args
            diskpath = {
                'path': path,
                }
            self.conf.dataprompt.update({'path': diskpath['path']})
            self.update_prompt()
        else:
            util.print_error('Please select a corrent path dir')

    def do_bootdev(self, args):
        """
        Select the boot device
        """
        if args not in qemulist.LIST_BOOTDEV:
            util.print_error("Please select a correct boot devices")
        else:
            boot_dev = {
                'boot_dev': args,
                }
            self.conf.dataprompt.update({'boot_dev': boot_dev['boot_dev']})
            self.update_prompt()

    def complete_bootdev(self, text, _line, _begidx, _endidx):
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
            dvd = {
                'source_file': file,
            }
            self.conf.dataprompt.update({'dvd': dvd['source_file']})
            self.update_prompt()
        else:
            util.print_error("CDROM/DVD ISO source file " +file +" Doesnt exist!")

    def do_vmimage(self, args):
        """
        Select an VM image to use
        """
        file = args
        if os.path.isfile(file):
            vmimage = {
                'source_file': file,
            }
            self.conf.dataprompt.update({'vmimage': vmimage['source_file']})
            self.update_prompt()
        else:
            util.print_error("Please select an VM image file, " +file +" Doesnt exist!")

    def do_vnet(self, args):
        """
        Select the virtual network
        """
        hvselected = self.conf.dataprompt.get('hvselected')
        if hvselected != None:
            self.hypervisor = hv.select_hypervisor()
            self.hypervisor.name = hvselected
            if not self.hypervisor.is_connected():
                util.print_error("No connection to LibVirt")
                return

            net_list = self.hypervisor.network_list()
            if args not in net_list:
                util.print_error("Please select a Virtual Network name from:")
                print(net_list)
            else:
                config = {
                    'vnet': args,
                }
                self.conf.dataprompt.update({'vnet': config['vnet']})
                self.update_prompt()
        else:
            util.print_error("Please select an Hypervisor with 'hvselect'")

    def do_memory(self, args):
        """
        Set Memory size, should be (Gib)
        """
        if args.isdigit() is False:
            util.print_error("Please select a correct memory value (GiB)")
        else:
            memory = {
                'memory': args,
            }
            self.conf.dataprompt.update({'memory': memory['memory']})
            self.update_prompt()

    def file_complete(self, text, _line, _begidx, _endidx, ext):
        """
        auto completion to find ext files in current path
        """
        all_files = util.find_ext_file(ext)
        if not text:
            completions = all_files[:]
        else:
            completions = [f for f in all_files if f.startswith(text)]
        return completions

    def complete_conf(self, text, line, begidx, endidx):
        """ return yaml list"""
        return self.file_complete(text, line, begidx, endidx, ".yaml")

    def complete_hvconf(self, text, line, begidx, endidx):
        """ return yaml list"""
        return self.file_complete(text, line, begidx, endidx, ".yaml")

    def complete_cdrom(self, text, line, begidx, endidx):
        """ return iso list"""
        return self.file_complete(text, line, begidx, endidx, ".iso")

    def do_mode(self, args):
        """
        Mode available are::
        - guest: only XML guest configuration
        - host: only host configuration
        - both should be done (default)

        Note: in case of disk image encryption, "both" mode will be forced
        as this is mandatory to create the VM image to retrieve the uuid
        """
        mode = args
        if mode not in self.conf.all_modes:
            util.print_error("Dont know this mode: help mode")
        else:
            self.conf.mode = mode

    def complete_mode(self, text, _line, _begidx, _endidx):
        """
        auto completion for mode
        """
        if not text:
            completions = self.conf.all_modes[:]
        else:
            completions = [f for f in self.conf.all_modes if f.startswith(text)]
        return completions

    def do_force_sev(self, args):
        """
        Force the extract of a localhost PDH file
        This is NOT secure as this file should be stored in a secure place!
        """
        force = args
        if force not in self.conf.on_off_options:
            util.print_error("Available options are: on / off")
        else:
            if force == "on":
                util.print_warning("This is NOT secure as the PDH should be stored in a secure place!")
                self.force_sev = True
            else:
                self.force_sev = False
            config = {
                'force_sev': force,
                }
            self.conf.dataprompt.update({'force_sev': config['force_sev']})
            self.update_prompt()

    def do_overwrite(self, args):
        """
        Overwrite mode allow you to overwrite previous config (XML and config store),
        This will also undefine any previous VM with the same name on current Hypervisor
        """
        overwrite = args
        if overwrite not in self.conf.on_off_options:
            util.print_error("Available options are: on / off")
        else:
            config = {'overwrite': overwrite,}
            self.conf.dataprompt.update({'overwrite': config['overwrite']})
            self.update_prompt()

    #def do_memory_backing(self, args):
    #    # https://blog.reds.ch/?p=1379
    #    """
    #    Anonymous memory file backend
    #    """
    #    mbacking = args
    #    if mbacking not in self.conf.on_off_options:
    #        util.print_error("Available options are: on / off")
    #    else:
    #        mbacking = args
    #        config = {'memory_backing': mbacking,}
    #        self.conf.dataprompt.update({'memory_backing': config['memory_backing']})
    #        self.update_prompt()

    def do_conf(self, args):
        """
        Select the yaml configuration file
        """
        file = args
        if os.path.isfile(file):
            Cmd.file = file
            util.validate_yaml_file(Cmd.file)
            self.conf.conffile = file
            config = {
                'mainconf': file,
            }
            self.conf.dataprompt.update({'mainconf': config['mainconf']})
            self.update_prompt()
        else:
            util.print_error("File " +file +" Doesnt exist!")

    def do_hvconf(self, args):
        """
        Load Hypervisor configuration
        """
        file = args
        if os.path.isfile(file):
            util.validate_yaml_file(file)
            self.conf.hvfile = file
            hv.load_hypervisors(self.conf.hvfile)
            config = {
                'hvconf': file,
            }
            self.conf.dataprompt.update({'hvconf': config['hvconf']})
            self.update_prompt()
        else:
            util.print_error("File " +file +" Doesnt exist!")

    def do_hvlist(self, _args):
        """
        List available hypervisor configurations
        """
        if configuration.check_conffile(self.conf.hvfile) is not False:
            configuration.Configuration.basic_config(self)
            hv.list_hypervisors()

    def do_hvselect(self, args):
        """
        Set hypervisor for which VMs are configured
        """
        if configuration.check_conffile(self.conf.hvfile) is not False:
            configuration.Configuration.basic_config(self)
            name = args.strip()
            config = {
                'hvselected': name,
            }
            if not hv.set_default_hv(name):
                util.print_error("Setting hypervisor failed")
                return
            self.conf.dataprompt.update({'hvselected': config['hvselected']})
            self.update_prompt()

    def complete_hvselect(self, text, _line, _begidx, _endidx):
        """
        auto completion list of hypervisor
        """
        if not text:
            completions = self.HV_LIST
        else:
            completions = [f for f in self.HV_LIST if f.startswith(text)]
        return completions

    def do_capacity(self, args):
        """
        Disk Size image in GiB
        """
        if args.isdigit() is False:
            util.print_error("Capacity must be an Int (GiB)")
        else:
            capacity = args
            config = {'capacity': capacity,}
            self.conf.dataprompt.update({'capacity': config['capacity']})
            self.update_prompt()

    def do_format(self, args):
        """
        Select the Disk Image format (qcow2/raw)
        """
        if args not in qemulist.DISK_FORMAT:
            util.print_error("Disk Image format must be: "+str(qemulist.DISK_FORMAT))
        else:
            dformat = args
            config = {'format': dformat,}
            self.conf.dataprompt.update({'format': config['format']})
            self.update_prompt()

    def complete_format(self, text, _line, _begidx, _endidx):
        """
        auto completion format type
        """
        if not text:
            completions = qemulist.DISK_FORMAT
        else:
            completions = [f for f in qemulist.DISK_FORMAT if f.startswith(text)]
        return completions

    def do_encryption(self, args):
        """
        Enable encryption of the Disk Image
        """
        if args not in self.conf.on_off_options:
            util.print_error("Should be: "+str(self.conf.on_off_options))
        else:
            encryption = args
            config = {'encryption': encryption,}
            self.conf.dataprompt.update({'encryption': config['encryption']})
            self.update_prompt()

    def do_cache(self, args):
        """
        Disk Cache mode
        """
        if args not in qemulist.DISK_CACHE:
            util.print_error("Should be: "+str(qemulist.DISK_CACHE))
        else:
            cache = args
            config = {'cache': cache,}
            self.conf.dataprompt.update({'cache': config['cache']})
            self.update_prompt()

    def complete_cache(self, text, _line, _begidx, _endidx):
        """
        auto completion cache mode
        """
        if not text:
            completions = qemulist.DISK_CACHE
        else:
            completions = [f for f in qemulist.DISK_CACHE if f.startswith(text)]
        return completions

    def do_quit(self, _args):
        """
        Exit the application
        Shorthand: Ctrl-D
        """
        # French Flag :)
        print(util.esc('blue')+'Bye'+util.esc('white')+'Bye'+util.esc('red')+'Bye'+util.esc('reset'))
        return True

    do_EOF = do_quit
