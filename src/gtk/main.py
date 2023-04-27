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
python GTK3 interface to deal with virt-scenario
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import virtscenario.qemulist as qemulist
import virtscenario.hypervisors as hv

class MyWizard(Gtk.Assistant):

    def __init__(self):

        Gtk.Assistant.__init__(self)
        self.set_title("virt-scenario")
        self.set_default_size(500, 400)
        self.expert = "off"

        def page_intro(self):
        # PAGE Intro
            box_intro = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            label_intro = Gtk.Label(label="Virt-scenario")
            urltocode = Gtk.LinkButton.new_with_label(
                uri="https://www.github.com/aginies/virt-scenario",
                label="virt-scenario Homepage"
            )

            hbox_expert = Gtk.Box(spacing=6)
            label_expert = Gtk.Label(label="Expert Mode")
            switch_expert = Gtk.Switch()
            switch_expert.connect("notify::active", self.on_switch_expert_activated)
            switch_expert.set_active(False)
            hbox_expert.pack_start(label_expert, False, False, 0)
            hbox_expert.pack_start(switch_expert, False, False, 0)

            box_intro.pack_start(label_intro, True, True, 0)
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
            self.set_page_title(box_vscenario, "Virt Scenario")
            self.set_page_type(box_vscenario, Gtk.AssistantPageType.PROGRESS)

            #Create a horizontal box for configuration
            hbox_conf = Gtk.Box(spacing=6)
            box_vscenario.pack_start(hbox_conf, False, False, 0)
            label_conf = Gtk.Label(label="Configuration file")
            filechooser_conf = Gtk.FileChooserButton(title="Select configuration file")
            hbox_conf.pack_start(label_conf, True, True, 0)
            hbox_conf.pack_start(filechooser_conf, True, True, 0)

            self.set_page_complete(box_vscenario, True)
    
        def page_hypervisors(self):
            # PAGE: hypervisor 
            box_hyper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            label_hyper = Gtk.Label(label="Hypervisor")
            box_hyper.pack_start(label_hyper, False, False, 0)
            self.append_page(box_hyper)
            self.set_page_title(box_hyper, "Hypervisor")
            self.set_page_type(box_hyper, Gtk.AssistantPageType.PROGRESS)

            #Create a horizontal box for configuration
            hbox_conf = Gtk.Box(spacing=6)
            box_hyper.pack_start(hbox_conf, False, False, 0)
            label_conf = Gtk.Label(label="Hypervisor Configuration file")
            filechooser_conf = Gtk.FileChooserButton(title="Select configuration file")
            hbox_conf.pack_start(label_conf, True, True, 0)
            hbox_conf.pack_start(filechooser_conf, True, True, 0)

            self.set_page_complete(box_hyper, True)

        def page_scenario(self):
            # PAGE: scenario 
            box_scenario = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            label_scenario = Gtk.Label(label="Scenario selection")
            box_scenario.pack_start(label_scenario, False, False, 0)
            self.append_page(box_scenario)
            self.set_page_title(box_scenario, "Scenario")
            self.set_page_type(box_scenario, Gtk.AssistantPageType.PROGRESS)
            scenario_combobox = Gtk.ComboBoxText()
            scenario_combobox.set_entry_text_column(0)
            box_scenario.pack_start(scenario_combobox, False, False, 0)

            # Add some items to the combo box
            items_scenario = ["Desktop", "Computation", "Secure VM"]
            for item in items_scenario:
                scenario_combobox.append_text(item)
            scenario_combobox.set_active(0)

            # Handle scenario selection
            scenario_combobox.connect("changed", self.on_scenario_changed)
            self.set_page_complete(box_scenario, True)

        def page_forcesev(self):
            # force SEV: for secure VM
            box_forcesev = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            self.add(box_forcesev)
            self.append_page(box_forcesev)
            self.set_page_title(box_forcesev, "Force SEV")
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

        def page_configuration(self):
            # PAGE configuration
            # Create a vertical box to hold the file selection button and the entry box
            vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            self.add(vbox2)
            self.set_page_title(vbox2, "Configuration")
            self.set_page_type(vbox2, Gtk.AssistantPageType.PROGRESS)

            # Create a horizontal box to hold the name and label
            hbox_name = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_name, False, False, 0)
            label_name = Gtk.Label(label="VM Name")
            entry_name = Gtk.Entry()
            entry_name.set_text("Name")
            hbox_name.pack_start(label_name, True, True, 1)
            hbox_name.pack_start(entry_name, True, True, 1)

            # Create a horizontal box vcpu spin
            hbox_spin_vcpu = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_spin_vcpu, False, False, 0)
            label_spinbutton = Gtk.Label(label="Vcpu")
            spinbutton_vcpu = Gtk.SpinButton()
            spinbutton_vcpu.set_range(1, 32)
            spinbutton_vcpu.set_increments(1, 1)
            spinbutton_vcpu.set_numeric(1)
            spinbutton_vcpu.set_value(2)
            hbox_spin_vcpu.pack_start(label_spinbutton, True, True, 1)
            hbox_spin_vcpu.pack_start(spinbutton_vcpu, True, True, 1)
        
            # Create a horizontal box memory spin
            hbox_spin_mem = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_spin_mem, False, False, 0)
            label_spinbutton_mem = Gtk.Label(label="Memory in GiB")
            spinbutton_mem = Gtk.SpinButton()
            spinbutton_mem.set_range(1, 32)
            spinbutton_mem.set_increments(1, 1)
            spinbutton_mem.set_numeric(1)
            spinbutton_mem.set_value(4)
            hbox_spin_mem.pack_start(label_spinbutton_mem, True, True, 0)
            hbox_spin_mem.pack_start(spinbutton_mem, True, True, 0)

            # Create a horizontal box for bootdev
            hbox_bootdev = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_bootdev, False, False, 0)
            label_bootdev = Gtk.Label(label="Bootdev")
            combobox_bootdev = Gtk.ComboBoxText()
            combobox_bootdev.set_entry_text_column(0)
            hbox_bootdev.pack_start(label_bootdev, True, True, 0)
            hbox_bootdev.pack_start(combobox_bootdev, True, True, 0)

            items_bootdev = qemulist.LIST_BOOTDEV
            for item in items_bootdev:
                combobox_bootdev.append_text(item)
            combobox_bootdev.set_active(0)

            # Handle bootdev selection
            combobox_bootdev.connect("changed", self.on_bootdev_changed)

            # Create a horizontal box for machine type
            hbox_machinet = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_machinet, False, False, 0)
            label_machinet = Gtk.Label(label="Machine")
            combobox_machinet = Gtk.ComboBoxText()
            combobox_machinet.set_entry_text_column(0)
            hbox_machinet.pack_start(label_machinet, True, True, 0)
            hbox_machinet.pack_start(combobox_machinet, True, True, 0)

            items_machinet = qemulist.LIST_MACHINETYPE
            for item in items_machinet:
                combobox_machinet.append_text(item)
            combobox_machinet.set_active(0)

            # Handle machine type selection
            combobox_machinet.connect("changed", self.on_machinet_changed)

            #Create a horizontal box for vmimage selection
            hbox_vmimage = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_vmimage, False, False, 0)
            label_vmimage = Gtk.Label(label="VM Image")
            filechooser_vmimage = Gtk.FileChooserButton(title="Select The VM Image")
            hbox_vmimage.pack_start(label_vmimage, True, True, 0)
            hbox_vmimage.pack_start(filechooser_vmimage, True, True, 0)

            #Create a horizontal box for CD/DVD
            hbox_cd = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_cd, False, False, 0)
            label_cd = Gtk.Label(label="CD/DVD")
            filechooser_cd = Gtk.FileChooserButton(title="Select The CD/DVD Image")
            hbox_cd.pack_start(label_cd, True, True, 0)
            hbox_cd.pack_start(filechooser_cd, True, True, 0)

            # Create a horizontal box for vnet
            hbox_vnet = Gtk.Box(spacing=6)
            vbox2.pack_start(hbox_vnet, False, False, 0)
            label_vnet = Gtk.Label(label="Virtual Network")
            combobox_vnet = Gtk.ComboBoxText()
            combobox_vnet.set_entry_text_column(0)
            hbox_vnet.pack_start(label_vnet, True, True, 0)
            hbox_vnet.pack_start(combobox_vnet, True, True, 0)

            # TOFIX
            hypervisor = hv.select_hypervisor()
            if not hypervisor.is_connected():
                print("No connection to LibVirt")
                return

            items_vnet = hypervisor.network_list()
            for item in items_vnet:
                combobox_vnet.append_text(item)
            combobox_vnet.set_active(0)

            # Handle vnet selection
            combobox_vnet.connect("changed", self.on_vnet_changed)

            self.set_page_complete(vbox2, True)

        def page_end(self):
            # PAGE : Then End
            box_end = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            label_summary = Gtk.Label(label="Summary")
            box_end.pack_start(label_summary, False, False, 0)
            self.append_page(box_end)
            self.set_page_title(box_end, "Summary")
            self.set_page_type(box_end, Gtk.AssistantPageType.SUMMARY)
            self.set_page_complete(box_end, True)

        # Connect signals
        self.connect("cancel", Gtk.main_quit)
        self.connect("close", Gtk.main_quit)
        self.connect("prepare", self.on_prepare)

        # create all the wizard pages
        page_intro(self)
        page_virtscenario(self)
        page_hypervisors(self)
        page_scenario(self)
        page_configuration(self)
        page_forcesev(self)
        page_end(self)

    def on_prepare(self, current_page, page):
        print("Preparing to show page:", self.get_current_page())
        print(self.expert)
        # remove virt scenario config and hypervisor if not expert mode
        if page == self.get_nth_page(1) and self.expert == "off":
            self.set_page_complete(current_page, True)
            self.next_page()
            self.set_page_complete(current_page, True)
            self.next_page()

        # skip forcesev if this is not a secure VM configuration
        if page == self.get_nth_page(5) and self.forcesev == "off":
            self.set_page_complete(current_page, True)
            self.next_page()

    def on_scenario_changed(self, combo_box):
        # add the page only if secure VM is selected
        # Get the selected item
        tree_iter = combo_box.get_active_iter()
        if tree_iter is not None:
            model = combo_box.get_model()
            selected_item = model[tree_iter][0]
            print("Selected item: {}".format(selected_item))

        if selected_item != "Secure VM":
            print("Not secure vm scenario")
            self.forcesev = "off"
        else:
            print("Secure vm selected")
            self.forcesev = "on"

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

    def on_destroy(self, widget, data=None):
        Gtk.main_quit()

def main():
    """
    Main
    """
    win = MyWizard()
    win.show_all()
    Gtk.main()

