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
python GTK3 helper
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk


class GtkHelper():
    """
    GtkHelper
    """

    def __init__(self):
        """
        init
        """
        print("here")

    # https://developer-old.gnome.org/hig/stable/visual-layout.html.en
    def margin_left(self):
        """
        return a gtk with correct alignement L
        """
        self.set_margin_left(18)

    def margin_right(self):
        """
        return a gtk with correct alignement R
        """
        self.set_margin_right(18)

    def margin_left_right(self):
        """
        return a gtk with correct alignement L R
        """
        self.set_margin_left(18)
        self.set_margin_right(18)

    def margin_top_left(self):
        """
        return a gtk with correct alignement T L
        """
        self.set_margin_top(12)
        self.set_margin_left(18)

    def margin_top_right(self):
        """
        return a gtk with correct alignement T R
        """
        self.set_margin_top(12)
        self.set_margin_right(18)

    def margin_top_left_right(self):
        """
        return a gtk with correct alignement T L R
        """
        self.set_margin_top(12)
        self.set_margin_left(18)
        self.set_margin_right(18)

    def margin_bottom_left(self):
        """
        return a gtk with correct alignement B L
        """
        self.set_margin_bottom(12)
        self.set_margin_left(18)

    def margin_bottom_right(self):
        """
        return a gtk with correct alignement B R
        """
        self.set_margin_bottom(12)
        self.set_margin_right(18)

    def margin_bottom_left_right(self):
        """
        return a gtk with correct alignement B L R 
        """
        self.set_margin_bottom(12)
        self.set_margin_left(18)
        self.set_margin_right(18)

    def margin_top_bottom_left(self):
        """
        return a gtk with correct alignement T B L 
        """
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_left(18)

    def margin_all(self):
        """
        return a gtk with correct alignement T B L R 
        """
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_left(18)
        self.set_margin_right(18)

    def create_label(data, halign):
        """
        create label
        """
        label = Gtk.Label(label=str(data))
        label.set_halign(halign)
        label.set_margin_left(18)
        return label

    def create_entry(data, halign):
        """
        create entry
        """
        entry = Gtk.Entry()
        entry.set_editable(False)
        entry.set_text(str(data))
        entry.set_halign(halign)
        return entry

    def create_scrolled():
        """
        create scroll gtk
        """
        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.set_hexpand(True)
        scrolled_win.set_vexpand(True)
        return scrolled_win

    def create_frame(title):
        """
        create a frame 
        """
        frame = Gtk.Frame()
        frame.set_border_width(10)
        frame.set_label_align(0, 0.8)
        frame.set_label(title)
        return frame

    def find_value_in_combobox(self):
        """
        return selected value in combobox
        """
        tree_iter = self.get_active_iter()
        if tree_iter is not None:
            model_value = self.get_model()
            selected_value = model_value[tree_iter][0]
            return selected_value
