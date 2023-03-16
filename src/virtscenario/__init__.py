# -*- coding: utf-8 -*-
# Authors: Antoine Ginies <aginies@suse.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
virt scenario
"""

import gettext
import virtscenario.main

gettext.bindtextdomain("virtscenario", "/usr/share/locale")
gettext.textdomain("virtscenario")
try:
    gettext.install("virtscanario", localedir="/usr/share/locale")
except IOError:
    import builtins

    builtins.__dict__["_"] = str

__version__ = "0.7.4"
