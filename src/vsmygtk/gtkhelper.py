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
from gi.repository import Gtk


def find_value_in_combobox(widget):
    """
    return selected value in combobox
    """
    tree_iter = widget.get_active_iter()
    if tree_iter is not None:
        model_value = widget.get_model()
        selected_value = model_value[tree_iter][0]
        return selected_value
    return False

# https://developer-old.gnome.org/hig/stable/visual-layout.html.en
def margin_left(widget):
    """
    return a gtk with correct alignement L
    """
    widget.set_margin_left(18)

def margin_right(widget):
    """
    return a gtk with correct alignement R
    """
    widget.set_margin_right(18)

def margin_left_right(widget):
    """
    return a gtk with correct alignement L R
    """
    widget.set_margin_left(18)
    widget.set_margin_right(18)

def margin_top_left(widget):
    """
    return a gtk with correct alignement T L
    """
    widget.set_margin_top(12)
    widget.set_margin_left(18)

def margin_top_right(widget):
    """
    return a gtk with correct alignement T R
    """
    widget.set_margin_top(12)
    widget.set_margin_right(18)

def margin_top_left_right(widget):
    """
    return a gtk with correct alignement T L R
    """
    widget.set_margin_top(12)
    widget.set_margin_left(18)
    widget.set_margin_right(18)

def margin_bottom(widget):
    """
    return a gtk with correct alignement B L
    """
    widget.set_margin_bottom(12)

def margin_bottom_left(widget):
    """
    return a gtk with correct alignement B L
    """
    widget.set_margin_bottom(12)
    widget.set_margin_left(18)

def margin_bottom_right(widget):
    """
    return a gtk with correct alignement B R
    """
    widget.set_margin_bottom(12)
    widget.set_margin_right(18)

def margin_bottom_left_right(widget):
    """
    return a gtk with correct alignement B L R
    """
    widget.set_margin_bottom(12)
    widget.set_margin_left(18)
    widget.set_margin_right(18)

def margin_top_bottom_left(widget):
    """
    return a gtk with correct alignement T B L
    """
    widget.set_margin_top(12)
    widget.set_margin_bottom(12)
    widget.set_margin_left(18)

def margin_all(widget):
    """
    return a gtk with correct alignement T B L R
    """
    widget.set_margin_top(12)
    widget.set_margin_bottom(12)
    widget.set_margin_left(18)
    widget.set_margin_right(18)

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

def create_entry_password():
    """
    create a entry password
    """
    entry = Gtk.Entry()
    entry.set_visibility(False)
    entry.set_invisible_char("*")
    return entry
