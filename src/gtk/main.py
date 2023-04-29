#!/usr/bin/env python3
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

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk

import virtscenario.qemulist as qemulist
import virtscenario.hypervisors as hv
import virtscenario.util as util
import virtscenario.configuration as configuration
import virtscenario.scenario as scenario
import virtscenario.host as host
import virtscenario.guest as guest
import virtscenario.configstore as configstore
# debug
from pprint import pprint

class MyWizard(Gtk.Assistant):

    class MyFilter():
        """
        create a filter for filechooser
        """
        def create_filter(name, list_ext):
            filter = Gtk.FileFilter()
            filter.set_name(name+" Files")
            for ext in list_ext:
                filter.add_pattern("*."+ext)
            return filter

    def __init__(self, conf):

        Gtk.Assistant.__init__(self)
        self.set_title("virt-scenario")
        self.set_default_size(500, 400)
        self.items_scenario = ["Desktop", "Computation", "Secure VM"]
        # set selected scenario to none by default
        self.selected_scenario = None
        # default all expert page not displayed
        self.expert = "on"
        self.force_sev = "off"
        self.overwrite = "on"
        self.conf = conf
        self.conf.callsign = "VMname"
        self.vm_config_store = self.conf.vm_config_store
        # prefiled data with desktop (better than empty data)
        self.data = scenario.Scenarios.desktop(self, "desktop")
        #pprint(vars(self.data))

        self.hypervisor = hv.select_hypervisor()
        if not self.hypervisor.is_connected():
           print("No connection to LibVirt")
           return

        # Connect signals
        self.connect("cancel", Gtk.main_quit)
        self.connect("close", Gtk.main_quit)
        self.connect("prepare", self.on_prepare)
        self.connect("apply", self.on_apply)

        # create all the wizard pages
        self.page_intro()
        self.page_virtscenario()
        self.page_hypervisors()
        self.page_scenario()
        self.page_configuration()
        #self.page_test()
        self.page_forcesev()
        self.page_end()

    def sync_data_with_scenario(self, page):
        # inherit from default config
        # Now use the wizard data to overwrite some vars
        self.conf.overwrite = self.overwrite
        self.conf.force_sev = self.force_sev
        self.conf.conffile = self.vfilechooser_conf.get_filename()
        self.conf.hvfile = self.hfilechooser_conf.get_filename()

        # VM definition
        self.conf.callsign = self.entry_name.get_text()
        self.conf.name = guest.create_name({'VM_name': self.conf.callsign})
        self.conf.vcpu = guest.create_cpu({'vcpu': self.spinbutton_vcpu.get_value()})
        # TO FIX GRAB MEMORY
        #self.spinbutton_memory.get_value()
        # get bootdev
        tree_iter_bootdev = self.combobox_bootdev.get_active_iter()
        model_bootdev = self.combobox_bootdev.get_model()
        selected_boot_dev_item = model_bootdev[tree_iter_bootdev][0]
        self.conf.listosdef.update({'boot_dev': selected_boot_dev_item})
        # get machine type
        tree_iter_machinet  = self.combobox_machinet.get_active_iter()
        model_machinet = self.combobox_machinet.get_model()
        selected_machinet  = model_machinet[tree_iter_machinet][0]
        self.conf.listosdef.update({'machine': selected_machinet})
        # get vnet
        tree_iter_vnet  = self.combobox_vnet.get_active_iter()
        model_vnet = self.combobox_vnet.get_model()
        selected_vnet  = model_vnet[tree_iter_vnet][0]
        self.conf.vnet = selected_vnet
        # vmimage
        self.conf.vmimage = self.filechooser_vmimage.get_filename()
        if self.filechooser_cd.get_filename() is not None:
            self.conf.cdrom = guest.create_cdrom({'source_file': self.filechooser_cd.get_filename()})
            self.conf.listosdef.update({'boot_dev': "cdrom"})

    def on_apply(self, current_page):
        #util.final_step_guest(cfg_store, self)
        self.sync_data_with_scenario(self)

        # launch the correct scenario
        cfg_store = configstore.create_config_store(self, self.data, self.hypervisor, self.conf.overwrite)
        if cfg_store is None:
            util.print_error("No config store found...")
            return

        if self.selected_scenario is not None:
            if self.selected_scenario == "securevm":
                scenario.Scenarios.do_securevm(self)
            elif self.selected_scenario == "desktop":
                scenario.Scenarios.do_desktop(self)
            elif self.selected_scenario == "computation":
                scenario.Scenarios.do_computation(self)
            else:
                print("Unknow scenario selected?")

    def on_prepare(self, current_page, page):
        print("Preparing to show page:", self.get_current_page())
        print("Expert mode: "+self.expert)
        print("Force SEV mode: "+self.force_sev)

        # remove virt scenario config and hypervisor if not expert mode
        if page == self.get_nth_page(1) and self.expert == "off":
            # skip virtscenario page
            self.set_page_complete(current_page, True)
            self.next_page()
            # skip hypervisor page
            self.set_page_complete(current_page, True)
            self.next_page()

        if page == self.get_nth_page(5) and self.force_sev == "off":
            self.set_page_complete(current_page, True)
            self.next_page()

    def page_intro(self):
    # PAGE Intro
        box_intro = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label_intro = Gtk.Label(label="Virt-scenario")
        label_warning = Gtk.Label("WARNING: under devel ...")
        label_warning.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("red"))
        label_warning.modify_font(Pango.FontDescription("Sans Bold 12"))
        urltocode = Gtk.LinkButton.new_with_label(
            uri="https://www.github.com/aginies/virt-scenario",
            label="virt-scenario Homepage"
        )

        hbox_expert = Gtk.Box(spacing=6)
        label_expert = Gtk.Label(label="Expert Mode")
        switch_expert = Gtk.Switch()
        switch_expert.set_tooltip_text("Add some pages with expert configuration\n\t!Not recommended!")
        switch_expert.connect("notify::active", self.on_switch_expert_activated)
        switch_expert.set_active(True)
        hbox_expert.pack_start(label_expert, False, False, 0)
        hbox_expert.pack_start(switch_expert, False, False, 0)

        box_intro.pack_start(label_intro, True, False, 0)
        box_intro.pack_start(label_warning, True, True, 0)
        box_intro.pack_start(urltocode, True, True, 0)
        box_intro.pack_start(hbox_expert, False, False, 0)

        self.append_page(box_intro)
        self.set_page_type(box_intro, Gtk.AssistantPageType.INTRO)
        self.set_page_complete(box_intro, True)

    def page_virtscenario(self):
        # PAGE: virt scenario 
        box_vscenario = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label_vscenario = Gtk.Label(label="Virt Scenario")
        box_vscenario.pack_start(label_vscenario, False, False, 0)
        self.append_page(box_vscenario)
        #self.set_page_title(box_vscenario, "Virt Scenario")
        self.set_page_type(box_vscenario, Gtk.AssistantPageType.CONTENT)

        #Create a horizontal box for virt-scenario configuration file
        hbox_conf = Gtk.Box(spacing=6)
        box_vscenario.pack_start(hbox_conf, False, False, 0)
        label_conf = Gtk.Label(label="Configuration file")
        self.vfilechooser_conf = Gtk.FileChooserButton(title="Select virt-scenario Configuration File")
        self.vfilechooser_conf.set_filename(self.conf.conffile)
        yaml_f = self.MyFilter.create_filter("yaml/yml", ["yaml", "yml"])
        self.vfilechooser_conf.add_filter(yaml_f)
        hbox_conf.pack_start(label_conf, False, False, 0)
        hbox_conf.pack_start(self.vfilechooser_conf, False, False, 0)

        #Create a horizontal box for overwrite config option
        hbox_overwrite = Gtk.Box(spacing=6)
        box_vscenario.pack_start(hbox_overwrite, False, False, 0)
        label_overwrite = Gtk.Label(label="Overwrite Previous Config")
        switch_overwrite = Gtk.Switch()
        switch_overwrite.connect("notify::active", self.on_switch_overwrite_activated)
        switch_overwrite.set_tooltip_text("This will overwrite any previous VM configuration!")
        switch_overwrite.set_active(True)
        hbox_overwrite.pack_start(label_overwrite, False, False, 0)
        hbox_overwrite.pack_start(switch_overwrite, False, False, 0)

        self.set_page_complete(box_vscenario, True)

    def page_hypervisors(self):
        # PAGE: hypervisor 
        box_hyper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label_hyper = Gtk.Label(label="Hypervisor")
        box_hyper.pack_start(label_hyper, False, False, 0)
        self.append_page(box_hyper)
        #self.set_page_title(box_hyper, "Hypervisor")
        self.set_page_type(box_hyper, Gtk.AssistantPageType.CONTENT)

        #Create a horizontal box for hypervisor configuration
        hbox_conf = Gtk.Box(spacing=6)
        box_hyper.pack_start(hbox_conf, False, False, 0)
        label_conf = Gtk.Label(label="Hypervisor Configuration file")
        self.hfilechooser_conf = Gtk.FileChooserButton(title="Select Hypervisor Configuration File")
        self.hfilechooser_conf.set_filename(self.conf.hvfile)
        yaml_f = self.MyFilter.create_filter("yaml/yml", ["yaml", "yml"])
        self.hfilechooser_conf.add_filter(yaml_f)
        hbox_conf.pack_start(label_conf, False, False, 0)
        hbox_conf.pack_start(self.hfilechooser_conf, False, False, 0)

        self.set_page_complete(box_hyper, True)
        return box_hyper

    def page_scenario(self):
        # PAGE: scenario 
        self.box_scenario = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label_scenario = Gtk.Label(label="Scenario selection")
        self.box_scenario.pack_start(label_scenario, False, False, 0)
        self.append_page(self.box_scenario)
        self.set_page_title(self.box_scenario, "Scenario")
        self.set_page_type(self.box_scenario, Gtk.AssistantPageType.CONTENT)

        urltoinfo = Gtk.LinkButton.new_with_label(
            uri="https://github.com/aginies/virt-scenario#default-settings-comparison",
            label="Scenarios Settings Comparison"
        )

        self.scenario_combobox = Gtk.ComboBoxText()
        self.scenario_combobox.set_entry_text_column(0)
        self.box_scenario.pack_start(urltoinfo, False, False, 0)
        self.box_scenario.pack_start(self.scenario_combobox, False, False, 0)

        # Add some items to the combo box
        for item in self.items_scenario:
            self.scenario_combobox.append_text(item)
        # dont select anything by default
        self.scenario_combobox.set_active(-1)

        hbox_scenario = Gtk.Box(spacing=6)
        self.box_scenario.pack_start(hbox_scenario, True, True, 0)

        # Handle scenario selection
        self.scenario_combobox.connect("changed", self.on_scenario_changed)
        if self.scenario_combobox.get_active() != -1:
            self.set_page_complete(self.box_scenario, True)


    def page_configuration(self):
        # PAGE configuration
        print("DEBUG DEBUG -------------------------------------------------------")
        print("END END DEBUG DEBUG -----------------------------------------------")

        # Create a vertical box to hold the file selection button and the entry box
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(vbox2)
        self.set_page_title(vbox2, "Configuration")
        self.set_page_type(vbox2, Gtk.AssistantPageType.PROGRESS)
        self.set_page_complete(vbox2, True)

        # Create a horizontal box to hold the name and label
        hbox_name = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_name, False, False, 0)
        label_name = Gtk.Label(label="VM Name")
        self.entry_name = Gtk.Entry()
        hbox_name.pack_start(label_name, True, True, 1)
        hbox_name.pack_start(self.entry_name, True, True, 1)

        # Create a horizontal box vcpu spin
        hbox_spin_vcpu = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_spin_vcpu, False, False, 0)
        label_spinbutton = Gtk.Label(label="Vcpu")
        self.spinbutton_vcpu = Gtk.SpinButton()
        self.spinbutton_vcpu.set_range(1, 32)
        self.spinbutton_vcpu.set_increments(1, 1)
        self.spinbutton_vcpu.set_numeric(4)
        hbox_spin_vcpu.pack_start(label_spinbutton, True, True, 1)
        hbox_spin_vcpu.pack_start(self.spinbutton_vcpu, True, True, 1)
    
        # Create a horizontal box memory spin
        hbox_spin_mem = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_spin_mem, False, False, 0)
        label_spinbutton_mem = Gtk.Label(label="Memory in GiB")
        self.spinbutton_mem = Gtk.SpinButton()
        self.spinbutton_mem.set_range(1, 32)
        self.spinbutton_mem.set_increments(1, 1)
        self.spinbutton_mem.set_numeric(1)
        self.spinbutton_mem.set_value(4)
        hbox_spin_mem.pack_start(label_spinbutton_mem, True, True, 0)
        hbox_spin_mem.pack_start(self.spinbutton_mem, True, True, 0)

        # Create a horizontal box for bootdev
        hbox_bootdev = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_bootdev, False, False, 0)
        label_bootdev = Gtk.Label(label="Bootdev")
        self.combobox_bootdev = Gtk.ComboBoxText()
        self.combobox_bootdev.set_entry_text_column(0)
        hbox_bootdev.pack_start(label_bootdev, True, True, 0)
        hbox_bootdev.pack_start(self.combobox_bootdev, True, True, 0)

        items_bootdev = qemulist.LIST_BOOTDEV
        for item in items_bootdev:
            self.combobox_bootdev.append_text(item)
        self.combobox_bootdev.set_active(0)

        # Handle bootdev selection
        self.combobox_bootdev.connect("changed", self.on_bootdev_changed)

        # Create a horizontal box for machine type
        hbox_machinet = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_machinet, False, False, 0)
        label_machinet = Gtk.Label(label="Machine")
        self.combobox_machinet = Gtk.ComboBoxText()
        self.combobox_machinet.set_entry_text_column(0)
        hbox_machinet.pack_start(label_machinet, True, True, 0)
        hbox_machinet.pack_start(self.combobox_machinet, True, True, 0)

        items_machinet = qemulist.LIST_MACHINETYPE
        for item in items_machinet:
            self.combobox_machinet.append_text(item)
        self.combobox_machinet.set_active(0)

        # Handle machine type selection
        self.combobox_machinet.connect("changed", self.on_machinet_changed)

        #Create a horizontal box for vmimage selection
        hbox_vmimage = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_vmimage, False, False, 0)
        label_vmimage = Gtk.Label(label="VM Image")
        self.filechooser_vmimage = Gtk.FileChooserButton(title="Select The VM Image")
        image_f = self.MyFilter.create_filter("raw/qcow2", ["raw", "qcow2"])
        self.filechooser_vmimage.add_filter(image_f)
        hbox_vmimage.pack_start(label_vmimage, True, True, 0)
        hbox_vmimage.pack_start(self.filechooser_vmimage, True, True, 0)

        #Create a horizontal box for CD/DVD
        hbox_cd = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_cd, False, False, 0)
        label_cd = Gtk.Label(label="CD/DVD")
        self.filechooser_cd = Gtk.FileChooserButton(title="Select The CD/DVD Image")
        iso_f = self.MyFilter.create_filter("ISO", ["iso"])
        self.filechooser_cd.add_filter(iso_f)
        hbox_cd.pack_start(label_cd, True, True, 0)
        hbox_cd.pack_start(self.filechooser_cd, True, True, 0)

        # Create a horizontal box for vnet
        hbox_vnet = Gtk.Box(spacing=6)
        vbox2.pack_start(hbox_vnet, False, False, 0)
        label_vnet = Gtk.Label(label="Virtual Network")
        self.combobox_vnet = Gtk.ComboBoxText()
        self.combobox_vnet.set_entry_text_column(0)
        hbox_vnet.pack_start(label_vnet, True, True, 0)
        hbox_vnet.pack_start(self.combobox_vnet, True, True, 0)

        items_vnet = self.hypervisor.network_list()
        for item in items_vnet:
            self.combobox_vnet.append_text(item)
        self.combobox_vnet.set_active(0)

        # Handle vnet selection
        self.combobox_vnet.connect("changed", self.on_vnet_changed)

    def page_test(self):
        print("DEBUG DEBUG -------------------------------------------------------")
        print("END END DEBUG DEBUG -----------------------------------------------")

        # PAGE : test
        box_t = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(box_t)
        self.set_page_type(box_t, Gtk.AssistantPageType.PROGRESS)
        label_t = Gtk.Label(label="TEST")
        box_t.pack_start(label_t, False, False, 0)
        self.set_page_title(box_t, "test")
        self.set_page_complete(box_t, True)

        # Create a horizontal box to hold the name and label
        hbox_name = Gtk.Box(spacing=6)
        box_t.pack_start(hbox_name, False, False, 0)
        label_name = Gtk.Label(label="VM Name")
        self.entry_name = Gtk.Entry()
        hbox_name.pack_start(label_name, True, True, 1)
        hbox_name.pack_start(self.entry_name, True, True, 1)

    def page_end(self):
        # PAGE : End
        box_end = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label_end = Gtk.Label(label="Confirm")
        box_end.pack_start(label_end, False, False, 0)

        hbox_end = Gtk.Box(spacing=6)
        textview = Gtk.TextView()
        textview.set_editable(0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(textview)
        textview.set_size_request(300, 300)
        buffer = textview.get_buffer()
        pprint(vars(self.conf))
        buffer.set_text("plop")
        hbox_end.pack_start(scroll, True, True, 0)
        box_end.pack_start(hbox_end, False, False, 0)

        self.append_page(box_end)
        self.set_page_title(box_end, "Confirm")
        self.set_page_type(box_end, Gtk.AssistantPageType.CONFIRM)
        self.set_page_complete(box_end, True)

    def page_forcesev(self):
        # force SEV: for secure VM
        box_forcesev = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.append_page(box_forcesev)
        #self.set_page_title(box_forcesev, "Force SEV")
        self.set_page_type(box_forcesev, Gtk.AssistantPageType.PROGRESS)
        hbox_forcesev = Gtk.Box(spacing=6)
        label_forcesev = Gtk.Label(label="Force SEV")
        switch_forcesev = Gtk.Switch()
        switch_forcesev.connect("notify::active", self.on_switch_forcesev_activated)
        switch_forcesev.set_active(False)
        hbox_forcesev.pack_start(label_forcesev, True, True, 0)
        hbox_forcesev.pack_start(switch_forcesev, False, False, 0)
        box_forcesev.pack_start(hbox_forcesev, False, False, 0)
        self.set_page_complete(box_forcesev, True)

    def on_scenario_changed(self, combo_box):
        # add the page only if secure VM is selected
        # Get the selected item
        tree_iter = combo_box.get_active_iter()
        if tree_iter is not None:
            model = combo_box.get_model()
            selected_item = model[tree_iter][0]
            print("Selected item: {}".format(selected_item))
            # enable the next button now :)
            self.set_page_complete(self.box_scenario, True)

        if selected_item == "Secure VM":
            print("Secure vm selected")
            self.force_sev = "on"
            self.selected_scenario = "securevm"
            sev_info = scenario.host.sev_info(self.hypervisor)
            self.data = scenario.Scenarios.secure_vm(self, "securevm", sev_info)
        elif selected_item == "Desktop":
            print("Desktop scenario")
            self.force_sev = "off"
            self.selected_scenario = "desktop"
            self.data = scenario.Scenarios.desktop(self, "desktop")
        elif selected_item == "Computation":
            print("Computation scenario")
            self.force_sev = "off"
            self.selected_scenario = "computation"
            self.data = scenario.Scenarios.computation(self, "computation")
        #pprint(vars(self.data))
        # update data with the selected scenario
        self.entry_name.set_text(self.data.name_data['VM_name'])

    def on_bootdev_changed(self, combo_box):
        # Get the selected item
        tree_iter = combo_box.get_active_iter()
        if tree_iter is not None:
            model = combo_box.get_model()
            selected_item = model[tree_iter][0]
            print("Selected Boot device: {}".format(selected_item))

    def on_machinet_changed(self, combo_box):
        # Get the selected item
        tree_iter = combo_box.get_active_iter()
        if tree_iter is not None:
            model = combo_box.get_model()
            selected_item = model[tree_iter][0]
            print("Selected machine type: {}".format(selected_item))

    def on_vnet_changed(self, combo_box):
        # Get the selected item
        tree_iter = combo_box.get_active_iter()
        if tree_iter is not None:
            model = combo_box.get_model()
            selected_item = model[tree_iter][0]
            print("Selected Virtual Network: {}".format(selected_item))

    def on_switch_expert_activated(self, switch, gparam):
        if switch.get_active():
            self.expert = "on"
        else:
            self.expert = "off"
        print("Switch Expert was turned", self.expert)

    def on_switch_forcesev_activated(self, switch, gparam):
        if switch.get_active():
            state = "on"
        else:
            state = "off"
        print("Switch Force SEV was turned", state)

    def on_switch_overwrite_activated(self, switch, gparam):
        if switch.get_active():
            self.overwrite = "on"
        else:
            self.overwrite = "off"
        print("Switch Overwrite Config was turned", self.overwrite)

    def on_destroy(self, widget, data=None):
        Gtk.main_quit()

def main():
    """
    Main GTK 
    """
    conf = configuration.Configuration()
    win = MyWizard(conf)
    win.show_all()
    Gtk.main()
