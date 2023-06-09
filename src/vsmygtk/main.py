# aginies@suse.com
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
python GTK3 interface for virt-scenario
"""

import os
import gi
import yaml
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango # Gdk
import virtscenario.qemulist as qemulist
import virtscenario.hypervisors as hv
import virtscenario.util as util
import virtscenario.configuration as configuration
import virtscenario.scenario as scenario
import vsmygtk.gtkhelper as gtk

# DEBUG
#from pprint import pprint

def create_filter(name, list_ext):
    """
    create a filter for filechooser
    """
    gfilter = Gtk.FileFilter()
    gfilter.set_name(name+" Files")
    for ext in list_ext:
        gfilter.add_pattern("*."+ext)
    return gfilter

class MyWizard(Gtk.Assistant):
    """
    The wizard itself
    """

    def __init__(self, conf):

        Gtk.Assistant.__init__(self)
        self.set_title("virt-scenario")
        self.set_default_size(500, 400)
        self.items_scenario = ["Desktop", "Computation", "Secure VM"]
        # set selected scenario to none by default
        self.selected_scenario = None
        self.show_storage_window = "off"
        # default all expert page not displayed
        self.expert = "off"
        self.force_sev = "off"
        self.howto = self.xml_show_config = ""
        self.overwrite = "off"
        self.gtk = True
        self.conf = conf
        self.STORAGE_DATA = {}
        self.STORAGE_DATA_REC = {}
        self.liststore = self.userpathincaseof = self.mdialog = self.switch_expert = ""
        self.vfilechooser_conf = self.hfilechooser_conf = self.main_scenario = self.scenario_combobox = ""
        self.window_storage = self.main_svbox = self.combobox_disk_target = self.spinbutton_cluster = ""
        self.combobox_disk_cache = self.combobox_lazyref = self.combobox_prealloc = ""
        self.combobox_encryption = self.entry_name = self.spinbutton_vcpu = self.spinbutton_mem = ""
        self.combobox_bootdev = self.combobox_machinet = self.combobox_vnet = ""
        self.label_spinbutton_capacity = self.spinbutton_capacity = self.filechooser_vmimage = ""
        self.filechooser_cd = self.textview_cmd = self.textbuffer_cmd = self.button_start = ""
        self.textbuffer_xml = ""

        self.conffile = configuration.find_conffile()
        self.hvfile = configuration.find_hvfile()

        if configuration.check_conffile(self.conffile) is not False:
            configuration.Configuration.basic_config(self)

        self.dataprompt = conf.dataprompt
        self.listosdef = conf.listosdef
        self.mode = conf.mode
        #self.conf.STORAGE_DATA = conf.STORAGE_DATA
        self.vm_config_store = self.conf.vm_config_store
        self.vm_list = os.listdir(self.vm_config_store)

        self.hypervisor = hv.select_hypervisor()
        if not self.hypervisor.is_connected():
            print("No connection to LibVirt")
            return
        else:
            self.items_vnet = self.hypervisor.network_list()

        # Connect signals
        self.connect("cancel", main_quit)
        self.connect("close", main_quit)
        self.connect("prepare", self.on_prepare)
        self.connect("apply", self.on_apply)

        self.page_intro() # 0
        self.page_virtscenario() # 1
        self.page_hypervisors() # 2
        self.page_scenario() # 3
        self.page_forcesev() # 4
        self.page_configuration() # 5
        self.page_end() # 6
        self.show_all()
        Gtk.main()

    def on_storage_ok_button_clicked(self, _widget):
        """
        store value
        """
        selected_prealloc = gtk.find_value_in_combobox(self.combobox_prealloc)
        self.STORAGE_DATA['preallocation'] = selected_prealloc
        selected_encryption = gtk.find_value_in_combobox(self.combobox_encryption)
        self.STORAGE_DATA['encryption'] = selected_encryption
        self.STORAGE_DATA['cluster_size'] = int(self.spinbutton_cluster.get_value())
        selected_disk_cache = gtk.find_value_in_combobox(self.combobox_disk_cache)
        self.STORAGE_DATA['disk_cache'] = selected_disk_cache
        selected_lazyref = gtk.find_value_in_combobox(self.combobox_lazyref)
        self.STORAGE_DATA['lazy_refcounts'] = selected_lazyref
        selected_disk_target = gtk.find_value_in_combobox(self.combobox_disk_target)
        self.STORAGE_DATA['disk_target'] = selected_disk_target
        selected_disk_format = gtk.find_value_in_combobox(self.combobox_disk_format)
        self.STORAGE_DATA['format'] = selected_disk_format

        selected_disk_format = gtk.find_value_in_combobox(self.combobox_disk_format)
        if selected_encryption == "on":
            self.conf.password = self.entry_password.get_text()
            self.conf.password_check = self.entry_password_check.get_text()
            if self.conf.password == "":
                text_mdialog = "Password can not be empty!"
                self.dialog_message("Error!", text_mdialog)
                return
            if self.conf.password != self.conf.password_check:
                text_error = "Password do <b>NOT</b> match!"
                self.dialog_message("Error!", text_error)
                return
        if selected_disk_format == "raw" and selected_prealloc == "metadata":
            text_error = "Raw format doesnt support preallocation = metadata"
            self.dialog_message("Error!", text_error)
            return

        self.window_storage.hide()
        return self.STORAGE_DATA

    def on_storage_cancel_button_clicked(self, _widget):
        """
        cancel
        """
        self.window_storage.destroy()

    def start_vm(self, _widget):
        """
        use virt-scenario-launch to start the VM
        """
        import subprocess
        if util.cmd_exists("virt-scenario-launch") is False:
            text_error = "<b>virt-scenario-launch</b> is not available on this system"
            self.dialog_message("Error!", text_error)
            return

        win_launch = Gtk.Window(title="Start VM log")
        win_launch.set_default_size(550, 500)
        win_launch.set_resizable(True)

        scrolled_window = Gtk.ScrolledWindow()
        text_view = Gtk.TextView()

        # Set the buffer and set editable to False
        buffer = text_view.get_buffer()
        text_view.set_editable(False)

        # Set markup text in the buffer
        markup_text = "<b>Command Log:</b>\n"+self.howto+"\n"
        buffer.insert_markup(buffer.get_end_iter(), markup_text, -1)

        try:
            command = self.howto.split()
            output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
            buffer.insert(buffer.get_end_iter(), output)

        except subprocess.CalledProcessError as err:
            error_message = f"Command execution failed with error code {err.returncode}: {err.output.decode()}"
            buffer.insert(buffer.get_end_iter(), error_message)

        scrolled_window.add(text_view)
        win_launch.add(scrolled_window)
        win_launch.show_all()


    def show_yaml_config(self, _widget, whichfile):
        """
        show the YAML file
        """
        yamlconf = ""
        if whichfile == "vs":
            yamlconf = self.vfilechooser_conf.get_filename()
            print("Show virt-scenario config:"+yamlconf)
        elif whichfile == "hv":
            yamlconf = self.hfilechooser_conf.get_filename()
            print("Show hypervisor config: "+yamlconf)
        if os.path.isfile(yamlconf) is False:
            text_error = "Yaml file not found ("+yamlconf+")"
            self.dialog_message("Error!", text_error)
            return

        with open(yamlconf, 'r') as fic:
            config = yaml.safe_load(fic)

        # Create a Gtk window and a vertical box to hold the frames
        window = Gtk.Window(title="virtscenario configuration")
        window.set_default_size(400, 400)
        window.set_resizable(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scrolled = gtk.create_scrolled()
        scrolled.add_with_viewport(box)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        window.add(scrolled)

        for item, value in config.items():
            grid = Gtk.Grid(column_spacing=12, row_spacing=6)
            grid.set_column_homogeneous(True)
            frame = gtk.create_frame(item)
            box.pack_start(frame, False, False, 0)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

            # grid row is 0
            row = 0
            for key in value:
                if isinstance(key, dict):
                    for kav, vav in key.items():
                        print(str(kav)+" "+str(vav))
                        label = gtk.create_label(kav, Gtk.Align.END)
                        entry = gtk.create_entry(vav, Gtk.Align.START)
                        grid.attach(label, 0, row, 1, 1)
                        grid.attach(entry, 1, row, 1, 1)
                        row += 1

            print(item)
            if isinstance(value, dict):
                row = 0
                for kav in value.keys():
                    print(kav)
                    label = gtk.create_label(kav, Gtk.Align.END)
                    grid.attach(label, 0, row, 1, 1)
                    row += 1
                row = 0
                for vav in value.values():
                    print(vav)
                    entry = gtk.create_entry(vav, Gtk.Align.START)
                    grid.attach(entry, 1, row, 1, 1)
                    row += 1

            frame.add(vbox)
            vbox.pack_start(grid, False, False, 0)

        window.show_all()
        window.connect("delete-event", on_delete_event)

    def apply_user_data_on_scenario(self):
        """ Now use the wizard data to overwrite some vars"""

        self.conf.overwrite = self.overwrite
        self.conf.force_sev = self.force_sev
        self.conffile = self.vfilechooser_conf.get_filename()
        self.conf.hvfile = self.hfilechooser_conf.get_filename()

        # VM definition
        self.conf.callsign = self.entry_name.get_text()
        # Get Name
        self.conf.dataprompt.update({'name': self.conf.callsign})
        # Get VCPU
        self.conf.dataprompt.update({'vcpu': int(self.spinbutton_vcpu.get_value())})
        # Get MEMORY
        self.conf.dataprompt.update({'memory': int(self.spinbutton_mem.get_value())})
        # Get bootdev
        selected_boot_dev_item = gtk.find_value_in_combobox(self.combobox_bootdev)
        self.conf.dataprompt.update({'boot_dev': selected_boot_dev_item})
        # Get machine type
        selected_machinet = gtk.find_value_in_combobox(self.combobox_machinet)
        self.conf.dataprompt.update({'machine': selected_machinet})
        # Get vnet
        selected_vnet = gtk.find_value_in_combobox(self.combobox_vnet)
        self.conf.dataprompt.update({'vnet': selected_vnet})
        # Get vmimage
        if self.filechooser_vmimage.get_filename() is not None:
            self.conf.dataprompt.update({'vmimage': self.filechooser_vmimage.get_filename()})
        # Get CD/DVD
        if self.filechooser_cd.get_filename() is not None:
            self.conf.dataprompt.update({'dvd': self.filechooser_cd.get_filename()})
            # self.conf.listosdef.update({'boot_dev': "cdrom"})

        ## STORAGE
        if self.show_storage_window == "on":
            self.conf.dataprompt.update({'preallocation': gtk.find_value_in_combobox(self.combobox_prealloc)})
            self.conf.dataprompt.update({'encryption': gtk.find_value_in_combobox(self.combobox_encryption)})
            self.conf.dataprompt.update({'disk_cache': gtk.find_value_in_combobox(self.combobox_disk_cache)})
            self.conf.dataprompt.update({'lazy_refcounts': gtk.find_value_in_combobox(self.combobox_lazyref)})
            self.conf.dataprompt.update({'disk_target': gtk.find_value_in_combobox(self.combobox_disk_target)})
            self.conf.dataprompt.update({'format': gtk.find_value_in_combobox(self.combobox_disk_format)})
            self.conf.dataprompt.update({'cluster_size': int(self.spinbutton_cluster.get_value())})
            selected_encryption = gtk.find_value_in_combobox(self.combobox_encryption)
            if selected_encryption == "on":
                self.conf.password = self.entry_password.get_text()
        self.conf.dataprompt.update({'capacity': int(self.spinbutton_capacity.get_value())})

        #return self
        #print("DEBUG DEBUG -------------------------------------------------------")
        #pprint(vars(self.conf))
        #print("END DEBUG DEBUG -----------------------------------------------")

    def on_apply(self, _current_page):
        """
        Apply all user setting to config and do XML config and Host preparation
        """
        self.apply_user_data_on_scenario()

        # launch the correct scenario
        if self.selected_scenario is not None:
            if self.selected_scenario == "securevm":
                scenario.Scenarios.do_securevm(self, False)
            elif self.selected_scenario == "desktop":
                scenario.Scenarios.do_desktop(self, False)
            elif self.selected_scenario == "computation":
                scenario.Scenarios.do_computation(self, False)
            else:
                print("Unknow selected Scenario!")

        if self.nothing_to_report is False:
            self.show_to_report(self.toreport)

    def show_to_report(self, toreport):
        """
        window to show to report value
        """
        window = Gtk.Window(title="Warning")
        window.set_default_size(450, 300)
        window.set_resizable(True)
        grid = Gtk.Grid(column_spacing=0, row_spacing=6)
        grid.set_column_homogeneous(True)

        label_title = gtk.create_label("Comparison table between user and recommended settings", Gtk.Align.START)
        gtk.margin_top_left(label_title)
        label_info = gtk.create_label("Overwrite are from file:\n"+self.conffile+"\nor from Storage settings dialog box\n", Gtk.Align.START)
        label_info.set_line_wrap(True)

        self.liststore = Gtk.ListStore(str, str, str)
        total = len(toreport)+1
        for number in range(1, int(total)):
            self.liststore.append([toreport[number]["title"], toreport[number]["rec"], str(toreport[number]["set"])])

        treeview = Gtk.TreeView(model=self.liststore)
        treeview.get_selection().set_mode(Gtk.SelectionMode.NONE)

        renderer_parameter = Gtk.CellRendererText()
        renderer_parameter.set_property("editable", False)
        renderer_parameter.set_property("weight", Pango.Weight.BOLD)
        column_parameter = Gtk.TreeViewColumn("Parameter", renderer_parameter, text=0)
        treeview.append_column(column_parameter)

        renderer_recommended = Gtk.CellRendererText()
        renderer_recommended.set_property("editable", False)
        renderer_recommended.set_property("alignment", Pango.Alignment.CENTER)
        column_recommended = Gtk.TreeViewColumn("Recommended", renderer_recommended, text=1)
        treeview.append_column(column_recommended)
        #recommended_color = Gdk.RGBA()
        #recommended_color.parse("#00FF00")  # green
        #renderer_recommended.set_property("foreground-rgba", recommended_color)

        renderer_user = Gtk.CellRendererText()
        renderer_user.set_property("editable", False)
        renderer_user.set_property("alignment", Pango.Alignment.CENTER)
        column_user = Gtk.TreeViewColumn("User Settings", renderer_user, text=2)
        treeview.append_column(column_user)
        #user_color = Gdk.RGBA()
        #user_color.parse("#FF0000")  # Red
        #renderer_user.set_property("foreground-rgba", user_color)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(treeview)

        grid.attach(label_title, 0, 0, 1, 1)
        grid.attach(label_info, 0, 2, 1, 1)
        grid.attach(scrolled_window, 0, 5, 1, 1)
        window.add(grid)
        window.show_all()

    def on_prepare(self, current_page, page):
        """
        remove some unwated pages in case of unneeded
        """
        #print("Show page:", self.get_current_page())
        #print("Expert mode: "+self.expert)
        #print("Force SEV mode: "+self.force_sev)
        #print("#found: "+str(self.get_n_pages())+ " pages")

        # remove virt scenario config and hypervisor if not expert mode
        if page == self.get_nth_page(1) and self.expert == "off":
            # skip virtscenario page
            self.set_page_complete(current_page, True)
            self.next_page()
            # skip hypervisor page
            self.set_page_complete(current_page, True)
            self.next_page()
            self.commit()

        # check previous config file already exist
        if page > self.get_nth_page(4) and self.overwrite == "off":
            if self.entry_name.get_text() in self.vm_list:
                self.conf.callsign = self.entry_name.get_text()
                tocheck = self.vm_config_store+"/"+self.conf.callsign
                self.userpathincaseof = os.path.expanduser(tocheck)
                print("Error! previous config found")
                text_mdialog = "A configuration for VM: \""+self.conf.callsign+"\" already exist in the directory:\n\""+self.userpathincaseof+"\"\nPlease change the name of the VM \nor use the <b>overwrite</b> option."
                self.dialog_message("Error!", text_mdialog)
                # force page 3
                self.set_current_page(3)

        # after scenario check if secure vm and allow force SEV
        if page > self.get_nth_page(2):
            self.commit()
            if self.selected_scenario != "securevm": # or self.expert == "off":
                #print("Bypassing force SEV page")
                if page == self.get_nth_page(4):
                    self.set_page_complete(current_page, True)
                    self.next_page()
            elif self.expert == "on":
                print("Force SEV page available")

        # post configuration, show the XML data
        if page >= self.get_nth_page(6):
            if os.path.isfile(self.filename):
                self.xml_show_config = self.show_data_from_xml()
                self.textbuffer_xml.set_text(self.xml_show_config)
                util.to_report(self.toreport, self.conf.conffile)

        if page > self.get_nth_page(5):
            self.howto = "virt-scenario-launch --start "+(self.conf.callsign)
            self.textbuffer_cmd.set_text(self.howto)

        if page > self.get_nth_page(5):
            if self.STORAGE_DATA_REC['encryption'] == "on" and self.show_storage_window == "off":
                text_mdialog = "In this scenario Virtual Machine Image <b>encryption = on</b>\n"
                text_mdialog += "Please set a <b>password</b> or set <b>encryption = off</b>\n"
                text_mdialog += "\nClick on the <b>Advanced Storage Configuration</b>\n"
                self.dialog_message("Error!", text_mdialog)
                self.set_current_page(4)

    def show_data_from_xml(self):
        """
        show xml data
        """
        with open(self.filename, 'r') as file:
            dump = file.read().rstrip()
        return dump

    def dialog_message(self, title, message):
        """
        message dialog
        """
        self.mdialog = Gtk.MessageDialog(parent=self.get_toplevel(),
                                         flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                         buttons=Gtk.ButtonsType.OK,
                                         type=Gtk.MessageType.INFO)

        self.mdialog.set_transient_for(self)
        self.mdialog.set_title(title)
        self.mdialog.set_markup(message)

        def on_response(_mdialog, _response_id):
            """ on response destroy"""
            _mdialog.destroy()
            return True

        self.mdialog.connect("response", on_response)
        self.mdialog.connect("close", on_response)
        self.mdialog.connect("delete-event", on_response)
        self.mdialog.show()

    def page_intro(self):
        """ PAGE Intro"""
        print("Load Page Intro")
        box_intro = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        grid_intro = Gtk.Grid(column_spacing=0, row_spacing=0)
        grid_intro.set_column_homogeneous(True)
        box_intro.pack_start(grid_intro, False, False, 0)

        label_title = gtk.create_label("virt-scenario", Gtk.Align.CENTER)
        label_title.override_font(Pango.FontDescription("Sans Bold 24"))
        label_intro = Gtk.Label()
        gtk.margin_all(label_intro)
        text_intro = "\nGenerate a customized <b>libvirt XML</b> guest and prepare the host.\n\n"
        text_intro += "The idea is to improve the experience usage compared to a basic setting.\n"
        text_intro += "This tool also simplifies the creation of a secure VM (AMD SEV).\n"
        text_intro += "\nThis tool does <b>NOT guarantee</b> anything."
        label_intro.set_markup(text_intro)
        label_intro.set_line_wrap(True)
        url = Gtk.LinkButton.new_with_label(uri="https://www.github.com/aginies/virt-scenario", label="virt-scenario Homepage")
        url.set_halign(Gtk.Align.CENTER)
        gtk.margin_left(url)

        grid_a = Gtk.Grid(column_spacing=0, row_spacing=6)

        label_expert = gtk.create_label("Advanced Mode", Gtk.Align.END)
        self.switch_expert = Gtk.Switch()
        gtk.margin_left(self.switch_expert)
        self.switch_expert.set_tooltip_text("Add some pages with expert configuration.\n(You can choose configurations files)")
        self.switch_expert.connect("notify::active", self.on_switch_expert_activated)
        self.switch_expert.set_active(False)
        self.switch_expert.set_halign(Gtk.Align.START)
        gtk.margin_all(grid_a)

        grid_a.attach(label_expert, 0, 0, 1, 1)
        grid_a.attach(self.switch_expert, 1, 0, 1, 1)

        grid_intro.attach(label_title, 0, 0, 4, 1)
        grid_intro.attach(url, 0, 1, 4, 2)
        grid_intro.attach(label_intro, 0, 4, 4, 4)
        grid_intro.attach(grid_a, 0, 8, 2, 1)

        self.append_page(box_intro)
        self.set_page_type(box_intro, Gtk.AssistantPageType.INTRO)
        self.set_page_complete(box_intro, True)

    def page_virtscenario(self):
        """ PAGE: virt scenario"""
        print("Load Page virtscenario")
        box_vscenario = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(box_vscenario)
        self.set_page_type(box_vscenario, Gtk.AssistantPageType.CONTENT)
        frame_vconf = gtk.create_frame("Virtscenario configuration")

        # Create a grid layout for virt-scenario configuration file
        grid_vconf = Gtk.Grid(column_spacing=0, row_spacing=6)
        grid_vconf.set_column_homogeneous(True)
        frame_vconf.add(grid_vconf)
        box_vscenario.pack_start(frame_vconf, False, False, 0)
        label_vconf = gtk.create_label("virt-scenario Configuration file", Gtk.Align.END)
        gtk.margin_top_left(label_vconf)
        self.vfilechooser_conf = Gtk.FileChooserButton(title="Select virt-scenario Configuration File")
        self.vfilechooser_conf.set_filename(self.conffile)
        self.vfilechooser_conf.set_halign(Gtk.Align.START)
        gtk.margin_top_left_right(self.vfilechooser_conf)
        yaml_f = create_filter("yaml/yml", ["yaml", "yml"])
        self.vfilechooser_conf.add_filter(yaml_f)
        button_vshow = Gtk.Button(label="Show configuration")
        gtk.margin_bottom_left_right(button_vshow)
        button_vshow.connect("clicked", lambda widget: self.show_yaml_config(button_vshow, "vs"))

        grid_vconf.attach(label_vconf, 0, 0, 1, 1)
        grid_vconf.attach(self.vfilechooser_conf, 1, 0, 1, 1)
        grid_vconf.attach(button_vshow, 1, 1, 1, 1)

        self.set_page_complete(box_vscenario, True)

    def page_hypervisors(self):
        """ PAGE: hypervisor"""
        print("Load Page hypervisor")
        box_hyper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(box_hyper)
        self.set_page_type(box_hyper, Gtk.AssistantPageType.CONTENT)
        frame_hconf = gtk.create_frame("Hypervisor configuration")

        grid_conf = Gtk.Grid(column_spacing=0, row_spacing=6)
        grid_conf.set_column_homogeneous(True)
        frame_hconf.add(grid_conf)
        box_hyper.pack_start(frame_hconf, False, False, 0)
        label_hconf = gtk.create_label("Hypervisor Configuration file", Gtk.Align.END)
        gtk.margin_top_left(label_hconf)
        self.hfilechooser_conf = Gtk.FileChooserButton(title="Select Hypervisor Configuration File")
        self.hfilechooser_conf.set_filename(self.hvfile)
        self.hfilechooser_conf.set_halign(Gtk.Align.START)
        gtk.margin_top_left_right(self.hfilechooser_conf)
        yaml_f = create_filter("yaml/yml", ["yaml", "yml"])
        self.hfilechooser_conf.add_filter(yaml_f)
        button_show = Gtk.Button(label="Show configuration")
        gtk.margin_bottom_left_right(button_show)
        button_show.connect("clicked", lambda widget: self.show_yaml_config(button_show, "hv"))
        gtk.margin_bottom_left(button_show)

        grid_conf.attach(label_hconf, 0, 0, 1, 1)
        grid_conf.attach(self.hfilechooser_conf, 1, 0, 1, 1)
        grid_conf.attach(button_show, 1, 1, 1, 1)

        self.set_page_complete(box_hyper, True)

    def page_scenario(self):
        """ PAGE: scenario"""
        print("Load Page Scenario")
        self.main_scenario = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(self.main_scenario)
        #self.set_page_title(self.main_scenario, "Scenario Selection")
        self.set_page_type(self.main_scenario, Gtk.AssistantPageType.CONTENT)

        frame_scena = gtk.create_frame("Scenario")
        grid_scena = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_scena.set_column_homogeneous(True)

        urltoinfo = Gtk.LinkButton.new_with_label(
            uri="https://github.com/aginies/virt-scenario/blob/main/DEFAULT_SETTINGS.md",
            label="Scenarios Settings Comparison Table"
        )
        gtk.margin_top_left_right(urltoinfo)
        frame_scena.add(grid_scena)
        self.main_scenario.pack_start(frame_scena, False, False, 0)

        label_scenario = gtk.create_label("Select Scenario", Gtk.Align.END)
        gtk.margin_left(label_scenario)
        self.scenario_combobox = Gtk.ComboBoxText()
        gtk.margin_right(self.scenario_combobox)
        self.scenario_combobox.set_tooltip_text("Will preload an optimized VM configration")
        self.scenario_combobox.set_entry_text_column(0)

        # Add some items to the combo box
        for item in self.items_scenario:
            self.scenario_combobox.append_text(item)
        # dont select anything by default
        self.scenario_combobox.set_active(-1)

        grid_scena.attach(urltoinfo, 0, 0, 2, 1)
        grid_scena.attach(label_scenario, 0, 2, 1, 1)
        grid_scena.attach(self.scenario_combobox, 1, 2, 1, 1)

        #Create a horizontal box for overwrite config option

        label_overwrite = gtk.create_label("Overwrite Previous Config", Gtk.Align.END)
        gtk.margin_bottom_left(label_overwrite)
        switch_overwrite = Gtk.Switch()
        gtk.margin_bottom_right(switch_overwrite)
        switch_overwrite.set_halign(Gtk.Align.START)
        switch_overwrite.connect("notify::active", self.on_switch_overwrite_activated)
        switch_overwrite.set_tooltip_text("This will overwrite any previous VM configuration!\nThis will also undefine any previous VM with the same name on current Hypervisor")
        switch_overwrite.set_active(False)
        grid_scena.attach(label_overwrite, 0, 3, 1, 1)
        grid_scena.attach(switch_overwrite, 1, 3, 1, 1)

        # Handle scenario selection
        self.scenario_combobox.connect("changed", self.on_scenario_changed)
        if self.scenario_combobox.get_active() != -1:
            self.set_page_complete(self.main_scenario, True)

    def show_storage(self, _widget):
        """ PAGE storage"""
# disk_type: file
# disk cache: writeback, writethrough, none, unsafe, directsync
# disk_target: vda
# disk_bus: virtio
# path: /var/lib/libvirt/images
# format: qcow2, raw
# host side: qemu-img creation options (-o), qemu-img --help
# capacity: 20
# cluster_size: 1024k
# lazy_refcounts: on
# preallocation: off, metadata (qcow2), falloc, full
# compression_type: zlib
# encryption: on, off
        self.show_storage_window = "on"

        self.window_storage = Gtk.Window(title="Storage configuration")
        self.window_storage.set_default_size(400, 400)
        self.window_storage.set_resizable(True)

        self.main_svbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame_scfg = gtk.create_frame("Storage Configuration")

        vbox_scfg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        grid_sto = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_sto.set_column_homogeneous(True)

        label_disk_target = gtk.create_label("Disk Target (Linux)", Gtk.Align.END)
        gtk.margin_top_left(label_disk_target)
        self.combobox_disk_target = Gtk.ComboBoxText()
        self.combobox_disk_target.set_tooltip_text("Select the disk target name inside the VM")
        gtk.margin_top_right(self.combobox_disk_target)
        self.combobox_disk_target.set_margin_top(18)

        items_disk_target = ['vda', 'vdb', 'vdc', 'vdd']
        for item in items_disk_target:
            self.combobox_disk_target.append_text(item)
        self.combobox_disk_target.set_active(0)
        #self.combobox_disk_target.connect("changed", self.on_disk_target_changed)

        label_disk_format = gtk.create_label("Disk format", Gtk.Align.END)
        gtk.margin_left(label_disk_format)
        self.combobox_disk_format = Gtk.ComboBoxText()
        gtk.margin_right(self.combobox_disk_format)
        self.combobox_disk_format.set_entry_text_column(0)

        items_disk_format = qemulist.DISK_FORMAT
        for item in items_disk_format:
            self.combobox_disk_format.append_text(item)
        self.combobox_disk_format.set_active(0)
        self.combobox_disk_format.connect("changed", self.on_disk_format_changed)

        label_spinbutton_cluster = gtk.create_label("Cluster Size (KiB)", Gtk.Align.END)
        gtk.margin_left(label_spinbutton_cluster)
        self.spinbutton_cluster = Gtk.SpinButton()
        self.spinbutton_cluster.set_tooltip_text(qemulist.CLUSTER_SIZE)
        gtk.margin_right(self.spinbutton_cluster)
        self.spinbutton_cluster.set_range(512, 2048)
        self.spinbutton_cluster.set_increments(512, 1)

        label_disk_cache = gtk.create_label("Disk Cache", Gtk.Align.END)
        gtk.margin_left(label_disk_cache)
        # bigger right margin to put the help button
        label_disk_cache.set_margin_right(36)
        hbutton_storage = Gtk.Button.new_from_icon_name("dialog-question", Gtk.IconSize.BUTTON)
        hbutton_storage.set_relief(Gtk.ReliefStyle.NONE)
        hbutton_storage.set_size_request(16, 16)
        hbutton_storage.set_halign(Gtk.Align.END)
        hbutton_storage.connect("clicked", lambda widget: show_storage_help(hbutton_storage))
        self.combobox_disk_cache = Gtk.ComboBoxText()
        gtk.margin_right(self.combobox_disk_cache)
        self.combobox_disk_cache.set_entry_text_column(0)

        items_disk_cache = qemulist.DISK_CACHE
        for item in items_disk_cache:
            self.combobox_disk_cache.append_text(item)
        self.combobox_disk_cache.set_active(0)
        #self.combobox_bootdev.connect("changed", self.on_disk_cache_changed)

        label_lazyref = gtk.create_label("Lazy Ref Count", Gtk.Align.END)
        gtk.margin_left(label_lazyref)
        self.combobox_lazyref = Gtk.ComboBoxText()
        self.combobox_lazyref.set_tooltip_text(qemulist.LAZY_REFCOUNTS)
        gtk.margin_right(self.combobox_lazyref)
        self.combobox_lazyref.set_entry_text_column(0)

        for item in ['on', 'off']:
            self.combobox_lazyref.append_text(item)
        self.combobox_lazyref.set_active(1)

        label_prealloc = gtk.create_label("Pre-allocation", Gtk.Align.END)
        gtk.margin_left(label_prealloc)
        self.combobox_prealloc = Gtk.ComboBoxText()
        self.combobox_prealloc.set_tooltip_text(qemulist.PREALLOCATION)
        gtk.margin_right(self.combobox_prealloc)
        self.combobox_prealloc.set_entry_text_column(0)

        items_prealloc = qemulist.PRE_ALLOCATION
        for item in items_prealloc:
            self.combobox_prealloc.append_text(item)
        self.combobox_prealloc.set_active(0)

        label_encryption = gtk.create_label("Encryption", Gtk.Align.END)
        gtk.margin_left(label_encryption)
        self.combobox_encryption = Gtk.ComboBoxText()
        self.combobox_encryption.set_tooltip_text("qcow2 payload will be encrypted using the LUKS format")
        self.combobox_encryption.connect("changed", self.on_encryption_changed)
        gtk.margin_right(self.combobox_encryption)
        self.combobox_encryption.set_entry_text_column(0)

        for item in ['on', 'off']:
            self.combobox_encryption.append_text(item)
        self.combobox_encryption.set_active(1)

        grid_expander = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_expander.set_column_homogeneous(True)
        label_password = gtk.create_label("Encryption Password", Gtk.Align.END)
        gtk.margin_left(label_password)
        self.entry_password = gtk.create_entry_password()
        gtk.margin_right(self.entry_password)
        label_password_check = gtk.create_label("Confirm Password", Gtk.Align.END)
        gtk.margin_bottom_left(label_password_check)
        self.entry_password_check = gtk.create_entry_password()
        gtk.margin_bottom_right(self.entry_password_check)
        self.text_expander = Gtk.Expander()
        gtk.margin_left(self.text_expander)

        grid_expander.attach(label_password, 0, 0, 1, 1)
        grid_expander.attach(self.entry_password, 1, 0, 1, 1)
        grid_expander.attach(label_password_check, 0, 1, 1, 1)
        grid_expander.attach(self.entry_password_check, 1, 1, 1, 1)
        self.text_expander.add(grid_expander)
        gtk.margin_bottom(self.text_expander)

        grid_sto.attach(label_disk_target, 0, 0, 1, 1)
        grid_sto.attach(self.combobox_disk_target, 1, 0, 1, 1)
        grid_sto.attach(label_disk_format, 0, 2, 1, 1)
        grid_sto.attach(self.combobox_disk_format, 1, 2, 1, 1)
        grid_sto.attach(label_spinbutton_cluster, 0, 3, 1, 1)
        grid_sto.attach(self.spinbutton_cluster, 1, 3, 1, 1)
        grid_sto.attach(label_disk_cache, 0, 4, 1, 1)
        grid_sto.attach(hbutton_storage, 0, 4, 1, 1)
        grid_sto.attach(self.combobox_disk_cache, 1, 4, 1, 1)
        grid_sto.attach(label_lazyref, 0, 5, 1, 1)
        grid_sto.attach(self.combobox_lazyref, 1, 5, 1, 1)
        grid_sto.attach(label_prealloc, 0, 6, 1, 1)
        grid_sto.attach(self.combobox_prealloc, 1, 6, 1, 1)
        grid_sto.attach(label_encryption, 0, 7, 1, 1)
        grid_sto.attach(self.combobox_encryption, 1, 7, 1, 1)
        grid_sto.attach(self.text_expander, 0, 8, 2, 1)

        grid_button = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_button.set_column_homogeneous(True)
        ok_button = Gtk.Button.new_with_label("OK")
        ok_button.set_halign(Gtk.Align.END)
        gtk.margin_all(ok_button)
        ok_button.connect("clicked", self.on_storage_ok_button_clicked)
        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.set_halign(Gtk.Align.START)
        gtk.margin_all(cancel_button)
        cancel_button.connect("clicked", self.on_storage_cancel_button_clicked)
        grid_button.attach(cancel_button, 0, 0, 1, 1)
        grid_button.attach(ok_button, 1, 0, 1, 1)

        ## STORAGE
        ## pre load data
        search_prealloc = self.STORAGE_DATA_REC['preallocation']
        search_in_comboboxtext(self.combobox_prealloc, search_prealloc)
        ## set encryption
        search_encryption = self.STORAGE_DATA_REC['encryption']
        search_in_comboboxtext(self.combobox_encryption, search_encryption)
        if search_encryption == "on":
            self.toggle_edit_focus("on", self.entry_password)
            self.toggle_edit_focus("on", self.entry_password_check)
            self.text_expander.set_expanded(True)
        else:
            self.toggle_edit_focus("off", self.entry_password)
            self.toggle_edit_focus("off", self.entry_password_check)
            self.text_expander.set_expanded(False)
            self.window_storage.resize(400, 400)
        ## set disk_cache
        search_disk_cache = self.STORAGE_DATA_REC['disk_cache']
        search_in_comboboxtext(self.combobox_disk_cache, search_disk_cache)
        ## set lazy_ref_count
        search_lazyref = self.STORAGE_DATA_REC['lazy_refcounts']
        search_in_comboboxtext(self.combobox_lazyref, search_lazyref)
        ## set cluster_size
        cluster_size = self.STORAGE_DATA['cluster_size']
        self.spinbutton_cluster.set_value(int(cluster_size))
        ## set disk target
        search_disk_target = self.STORAGE_DATA['disk_target']
        search_in_comboboxtext(self.combobox_disk_target, search_disk_target)
        ## disk format
        search_disk_format = self.STORAGE_DATA_REC['format']
        search_in_comboboxtext(self.combobox_disk_format, search_disk_format)

        vbox_scfg.pack_start(grid_sto, False, False, 0)
        frame_scfg.add(vbox_scfg)
        self.main_svbox.pack_start(frame_scfg, False, False, 0)
        self.main_svbox.pack_start(grid_button, False, False, 0)
        self.window_storage.add(self.main_svbox)
        self.window_storage.show_all()
        self.window_storage.connect("delete_event", on_delete_event)

    def page_configuration(self):
        """ PAGE configuration"""
        print("Load Page configuration")
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(main_vbox)
        #self.set_page_title(main_vbox, "Configuration")
        self.set_page_type(main_vbox, Gtk.AssistantPageType.CONFIRM)
        self.set_page_complete(main_vbox, True)

        frame_cfg = gtk.create_frame("Configuration")
        vbox_cfg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        grid_cfg = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_cfg.set_column_homogeneous(True)

        label_name = gtk.create_label("Virtual Machine Name", Gtk.Align.END)
        gtk.margin_top_left(label_name)
        self.entry_name = Gtk.Entry()
        gtk.margin_top_right(self.entry_name)
        self.entry_name.set_text("VMname")
        self.entry_name.set_tooltip_text("Virtual Machine Name")

        label_spinbutton_vcpu = gtk.create_label("Virtual CPU", Gtk.Align.END)
        gtk.margin_left(label_spinbutton_vcpu)
        self.spinbutton_vcpu = Gtk.SpinButton()
        gtk.margin_right(self.spinbutton_vcpu)
        self.spinbutton_vcpu.set_range(1, 64)
        self.spinbutton_vcpu.set_increments(1, 1)

        label_spinbutton_mem = gtk.create_label("Memory (GiB)", Gtk.Align.END)
        gtk.margin_left(label_spinbutton_mem)
        self.spinbutton_mem = Gtk.SpinButton()
        gtk.margin_right(self.spinbutton_mem)
        self.spinbutton_mem.set_range(1, 256)
        self.spinbutton_mem.set_increments(1, 1)

        label_bootdev = gtk.create_label("Boot device", Gtk.Align.END)
        gtk.margin_left(label_bootdev)
        self.combobox_bootdev = Gtk.ComboBoxText()
        self.combobox_bootdev.set_tooltip_text("Select the boot device")
        gtk.margin_right(self.combobox_bootdev)
        self.combobox_bootdev.set_entry_text_column(0)

        items_bootdev = qemulist.LIST_BOOTDEV
        for item in items_bootdev:
            self.combobox_bootdev.append_text(item)
        self.combobox_bootdev.set_active(0)
        # Handle bootdev selection
        #self.combobox_bootdev.connect("changed", on_bootdev_changed)

        label_machinet = gtk.create_label("Machine Type", Gtk.Align.END)
        gtk.margin_left(label_machinet)
        self.combobox_machinet = Gtk.ComboBoxText()
        self.combobox_machinet.set_tooltip_text("Using a recent machine type is higly recommended")
        gtk.margin_right(self.combobox_machinet)

        items_machinet = qemulist.LIST_MACHINETYPE
        for item in items_machinet:
            self.combobox_machinet.append_text(item)
        # Handle machine type selection
        #self.combobox_machinet.connect("changed", on_machinet_changed)

        label_vnet = gtk.create_label("Virtual Network", Gtk.Align.END)
        gtk.margin_bottom_left(label_vnet)
        self.combobox_vnet = Gtk.ComboBoxText()
        self.combobox_vnet.set_tooltip_text("Select a Virtual Network on current Hypervisor")
        gtk.margin_bottom_right(self.combobox_vnet)
        self.combobox_vnet.set_entry_text_column(0)

        for item in self.items_vnet:
            self.combobox_vnet.append_text(item)
        self.combobox_vnet.set_active(0)

        self.label_spinbutton_capacity = gtk.create_label("Disk Size (GiB)", Gtk.Align.END)
        gtk.margin_left(self.label_spinbutton_capacity)
        self.spinbutton_capacity = Gtk.SpinButton()
        gtk.margin_right(self.spinbutton_capacity)
        self.spinbutton_capacity.set_range(1, 32)
        self.spinbutton_capacity.set_increments(1, 1)

        grid_cfg.attach(label_name, 0, 0, 1, 1)
        grid_cfg.attach(self.entry_name, 1, 0, 1, 1)
        grid_cfg.attach(label_spinbutton_vcpu, 0, 1, 1, 1)
        grid_cfg.attach(self.spinbutton_vcpu, 1, 1, 1, 1)
        grid_cfg.attach(label_spinbutton_mem, 0, 2, 1, 1)
        grid_cfg.attach(self.spinbutton_mem, 1, 2, 1, 1)
        grid_cfg.attach(self.label_spinbutton_capacity, 0, 3, 1, 1)
        grid_cfg.attach(self.spinbutton_capacity, 1, 3, 1, 1)
        grid_cfg.attach(label_bootdev, 0, 4, 1, 1)
        grid_cfg.attach(self.combobox_bootdev, 1, 4, 1, 1)
        grid_cfg.attach(label_machinet, 0, 5, 1, 1)
        grid_cfg.attach(self.combobox_machinet, 1, 5, 1, 1)
        grid_cfg.attach(label_vnet, 0, 6, 1, 1)
        grid_cfg.attach(self.combobox_vnet, 1, 6, 1, 1)
        vbox_cfg.pack_start(grid_cfg, False, False, 0)
        frame_cfg.add(vbox_cfg)
        main_vbox.pack_start(frame_cfg, False, False, 0)

        #vbox_cfgplus = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame_cfgplus = gtk.create_frame("Image / CD / DVD / Storage")
        grid_cfgplus = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_cfgplus.set_column_homogeneous(True)

        label_vmimage = gtk.create_label("Virtual Machine Image", Gtk.Align.END)
        gtk.margin_top_left(label_vmimage)
        self.filechooser_vmimage = Gtk.FileChooserButton(title="VM Image Selection")
        gtk.margin_top_right(self.filechooser_vmimage)
        image_f = create_filter("raw/qcow2", ["raw", "qcow2"])
        self.filechooser_vmimage.add_filter(image_f)

        label_cd = gtk.create_label("CD/DVD", Gtk.Align.END)
        gtk.margin_bottom_left(label_cd)
        self.filechooser_cd = Gtk.FileChooserButton(title="CD/DVD Selection")
        gtk.margin_bottom_right(self.filechooser_cd)
        iso_f = create_filter("ISO", ["iso"])
        self.filechooser_cd.add_filter(iso_f)

        button_storage = Gtk.Button(label="Advanced Storage Configuration")
        button_storage.connect("clicked", lambda widget: self.show_storage(button_storage))
        gtk.margin_bottom_left_right(button_storage)

        grid_cfgplus.attach(label_vmimage, 0, 0, 1, 1)
        grid_cfgplus.attach(self.filechooser_vmimage, 1, 0, 1, 1)
        grid_cfgplus.attach(label_cd, 0, 1, 1, 1)
        grid_cfgplus.attach(self.filechooser_cd, 1, 1, 1, 1)
        grid_cfgplus.attach(button_storage, 0, 2, 2, 1)
        frame_cfgplus.add(grid_cfgplus)
        main_vbox.pack_start(frame_cfgplus, False, False, 0)

        # Handle vnet selection
        #self.combobox_vnet.connect("changed", on_vnet_changed)

        ## set capacity
        capacity = self.STORAGE_DATA['capacity']
        self.spinbutton_capacity.set_value(int(capacity))

    def page_end(self):
        """ PAGE : End"""
        print("Load Page End")
        box_end = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        grid_end = Gtk.Grid(column_spacing=12, row_spacing=6)
        frame_launch = gtk.create_frame("Launch VM")
        # hbox to store launch info
        hbox_launch = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label_launch = Gtk.Label()
        label_launch.set_halign(Gtk.Align.START)
        text_start = "Use the <b>virt-scenario-launch</b> tool:"
        label_launch.set_markup(text_start)
        label_launch.set_line_wrap(False)
        hbox_launch.pack_start(label_launch, False, False, 0)
        gtk.margin_top_left(hbox_launch)

        self.textview_cmd = Gtk.TextView()
        self.textview_cmd.set_editable(False)
        self.textbuffer_cmd = self.textview_cmd.get_buffer()
        hbox_launch.pack_start(self.textview_cmd, False, False, 0)

        self.button_start = Gtk.Button(label="Start the Virtual Machine")
        self.button_start.connect("clicked", self.start_vm)
        gtk.margin_bottom_left_right(self.button_start)
        hbox_launch.pack_start(self.button_start, False, False, 0)

        label_vm = Gtk.Label()
        text_end = "(You can also use <b>virt-manager</b>)"
        label_vm.set_markup(text_end)
        gtk.margin_top_left(label_vm)
        label_vm.set_alignment(0, 0)
        #hbox_launch.pack_start(label_vm, False, False, 0)

        # store everything in the frame
        frame_launch.add(hbox_launch)
        grid_end.attach(frame_launch, 0, 0, 1, 1)

        frame_xml = gtk.create_frame("XML")
        hbox_xml = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        scrolledwin_xml = gtk.create_scrolled()
        textview_xml = Gtk.TextView()
        textview_xml.set_editable(False)
        self.textbuffer_xml = textview_xml.get_buffer()
        scrolledwin_xml.add(textview_xml)
        hbox_xml.pack_start(scrolledwin_xml, True, True, 0)
        gtk.margin_all(hbox_xml)

        frame_xml.add(hbox_xml)
        grid_end.attach(frame_xml, 0, 1, 1, 1)
        # add the grid to the main box
        box_end.pack_start(grid_end, True, True, 0)

        self.append_page(box_end)
        #self.set_page_title(box_end, "HowTo")
        self.set_page_type(box_end, Gtk.AssistantPageType.SUMMARY)
        self.set_page_complete(box_end, True)

    def page_forcesev(self):
        """ sev page """
        print("Load Page SEV")
        # force SEV: for secure VM
        box_forcesev = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(box_forcesev)
        self.set_page_type(box_forcesev, Gtk.AssistantPageType.CONTENT)

        frame_forcesev = gtk.create_frame("Force PDH extraction")
        grid_forcesev = Gtk.Grid(column_spacing=12, row_spacing=6)
        grid_forcesev.set_column_homogeneous(True)

        label_warning = Gtk.Label()
        text_warning = "This option Force the extract of a localhost PDH file.\n"
        text_warning += "This is <b>NOT secure</b>!\nPDH file should be stored in a secure place.\n"
        label_warning.set_markup(text_warning)
        label_warning.set_line_wrap(True)
        gtk.margin_top_left_right(label_warning)

        label_forcesev = gtk.create_label("Force PDH extraction", Gtk.Align.END)
        gtk.margin_bottom_left(label_forcesev)
        switch_forcesev = Gtk.Switch()
        gtk.margin_bottom_right(switch_forcesev)
        switch_forcesev.connect("notify::active", self.on_switch_forcesev_activated)
        switch_forcesev.set_halign(Gtk.Align.START)
        switch_forcesev.set_active(False)

        grid_forcesev.attach(label_warning, 0, 0, 2, 4)
        grid_forcesev.attach(label_forcesev, 0, 4, 1, 1)
        grid_forcesev.attach(switch_forcesev, 1, 4, 1, 1)
        frame_forcesev.add(grid_forcesev)
        box_forcesev.pack_start(frame_forcesev, False, False, 0)

        self.set_page_complete(box_forcesev, True)

    def on_scenario_changed(self, combo_box):
        """
        some actions in case of scenario change
        """
        # add the page only if secure VM is selected
        # Get the selected scenario
        tree_iter = combo_box.get_active_iter()
        if tree_iter is not None:
            model = combo_box.get_model()
            selected_item = model[tree_iter][0]
            print("Selected item: {}".format(selected_item))
            # enable the next button now
            self.set_page_complete(self.main_scenario, True)

        if selected_item == "Secure VM":
            print("Secure vm selected")
            self.force_sev = "on"
            self.selected_scenario = "securevm"
            sev_info = scenario.host.sev_info(self.hypervisor)
            if not sev_info.sev_supported:
                util.print_error("Selected hypervisor ({}) does not support SEV".format(self.hypervisor.name))
                self.set_page_complete(self.main_scenario, False)
                text_mdialog = "Selected hypervisor ({}) does not support SEV".format(self.hypervisor.name)
                text_mdialog += "\nPlease select another scenario"
                self.dialog_message("Error!", text_mdialog)
                return

            self.conf = scenario.Scenarios.pre_secure_vm(self, "securevm", sev_info)
            self.conf.memory_pin = True
        elif selected_item == "Desktop":
            print("Desktop scenario")
            self.force_sev = "off"
            self.selected_scenario = "desktop"
            self.conf = scenario.Scenarios.pre_desktop(self, "desktop")
            self.conf.memory_pin = False
        elif selected_item == "Computation":
            print("Computation scenario")
            self.force_sev = "off"
            self.selected_scenario = "computation"
            self.conf = scenario.Scenarios.pre_computation(self, "computation")
            self.conf.memory_pin = False

        ## update data with the selected scenario
        self.entry_name.set_text(self.conf.name['VM_name'])
        self.spinbutton_vcpu.set_value(int(self.conf.vcpu['vcpu']))
        self.spinbutton_mem.set_value(int(self.conf.memory['max_memory']))
        ## set machine type
        search_machinet = self.conf.osdef['machine']
        search_in_comboboxtext(self.combobox_machinet, search_machinet)
        ## set boot dev
        search_bootdev = self.conf.osdef['boot_dev']
        search_in_comboboxtext(self.combobox_bootdev, search_bootdev)
        ## STORAGE
        search_prealloc = self.STORAGE_DATA_REC['preallocation']
        search_in_comboboxtext(self.combobox_prealloc, search_prealloc)
        search_encryption = self.STORAGE_DATA_REC['encryption']
        search_in_comboboxtext(self.combobox_encryption, search_encryption)
        search_disk_cache = self.STORAGE_DATA_REC['disk_cache']
        search_in_comboboxtext(self.combobox_disk_cache, search_disk_cache)
        search_lazyref = self.STORAGE_DATA_REC['lazy_refcounts']
        search_in_comboboxtext(self.combobox_lazyref, search_lazyref)
        cluster_size = self.STORAGE_DATA['cluster_size']
        self.spinbutton_cluster.set_value(int(cluster_size))
        capacity = self.STORAGE_DATA['capacity']
        self.spinbutton_capacity.set_value(int(capacity))
        search_disk_target = self.STORAGE_DATA['disk_target']
        search_in_comboboxtext(self.combobox_disk_target, search_disk_target)
        search_disk_format = self.STORAGE_DATA['format']
        search_in_comboboxtext(self.combobox_disk_format, search_disk_format)


    def on_switch_expert_activated(self, switch, _gparam):
        """ display status of the switch """
        if switch.get_active():
            self.expert = "on"
        else:
            self.expert = "off"
        #print("Switch Expert was turned", self.expert)

    def on_switch_forcesev_activated(self, switch, _gparam):
        """ display status of the switch """
        if switch.get_active():
            self.force_sev = "on"
        else:
            self.force_sev = "off"
        #print("Switch Force SEV was turned", self.force_sev)

    def on_switch_overwrite_activated(self, switch, _gparam):
        """ display status of the switch """
        if switch.get_active():
            self.overwrite = "on"
        else:
            self.overwrite = "off"
        #print("Switch Overwrite Config was turned", self.overwrite)

    def toggle_edit_focus(self, todo, widget):
        """ get entry edit and focus on or off"""
        if todo == "on":
            widget.set_editable(1)
            widget.set_can_focus(True)
        else:
            widget.set_editable(0)
            widget.set_can_focus(False)

    def on_encryption_changed(self, combo_box):
        """ Get the selected item """
        selected_item = gtk.find_value_in_combobox(combo_box)
        #print("Encryption is: {}".format(selected_item))
        if selected_item == "on":
            self.toggle_edit_focus("on", self.entry_password)
            self.toggle_edit_focus("on", self.entry_password_check)
            self.text_expander.set_expanded(True)
        else:
            self.toggle_edit_focus("off", self.entry_password)
            self.toggle_edit_focus("off", self.entry_password_check)
            self.text_expander.set_expanded(False)
            self.window_storage.resize(400, 400)

    def on_disk_format_changed(self, combo_box):
        """ some action are needed !"""
        selected_item = gtk.find_value_in_combobox(combo_box)
        if selected_item == "qcow2":
            # enable encryption stuff
            self.combobox_encryption.set_sensitive(1)
            self.text_expander.set_sensitive(1)
        else:
            # disable encryption stuff
            self.combobox_encryption.set_sensitive(0)
            self.text_expander.set_sensitive(0)

def show_storage_help(_widget):
    """
    show help on storage option
    """
    mdialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.OK, type=Gtk.MessageType.INFO)
    mdialog.set_title("Storage Help")
    disk_help = qemulist.STORAGE_HELP
    mdialog.set_markup(disk_help)

    def on_response(_dialog, _response_id):
        """ on response dfestroy"""
        _dialog.destroy()

    mdialog.connect("response", on_response)
    mdialog.show()

def search_in_comboboxtext(combobox, search_string):
    """
    search text in combobox list
    """
    matching_item = None
    #print("Search string: "+search_string)
    for iva in range(combobox.get_model().iter_n_children(None)):
        itera = combobox.get_model().iter_nth_child(None, iva)
        if combobox.get_model().get_value(itera, 0) == search_string:
            matching_item = itera
            break
    if matching_item is not None:
        combobox.set_active_iter(matching_item)
    else:
        util.print_error("Can not find: "+str(search_string))

def on_bootdev_changed(combo_box):
    """ Get the selected item """
    selected_item = gtk.find_value_in_combobox(combo_box)
    print("Selected Boot device: {}".format(selected_item))


def on_machinet_changed(combo_box):
    """ Get the selected item """
    selected_item = gtk.find_value_in_combobox(combo_box)
    print("Selected machine type: {}".format(selected_item))

def on_vnet_changed(combo_box):
    """ Get the selected item"""
    selected_item = gtk.find_value_in_combobox(combo_box)
    print("Selected Virtual Network: {}".format(selected_item))

def on_delete_event(widget, _event):
    """ destroy """
    widget.destroy()
    return True

def main_quit(_widget):
    """
    close all window
    """
    Gtk.main_quit()

def main():
    """
    Main GTK
    """
    conf = configuration.Configuration()
    MyWizard(conf)
