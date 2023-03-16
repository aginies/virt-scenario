#!/usr/bin/python3
# -*- coding: utf-8; -*-
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
Setup script used for building, testing, and installing modules
based on setuptools.
"""

import codecs
import os
import re
import sys
import subprocess
import time
from glob import glob
import setuptools
from setuptools.command.install import install
from setuptools.command.sdist import sdist

sys.path.insert(0, "src")


def read(fname):
    """
    Utility function to read the text file.
    """
    path = os.path.join(os.path.dirname(__file__), fname)
    with codecs.open(path, encoding="utf-8") as fobj:
        return fobj.read()


class PostInstallCommand(install):
    """
    Post-installation commands.
    """
    #install.run(self)

class GenerateMan():
    """
    Generate the man page
    """
    #cmd = ["pandoc", "README.md", "-f", "markdown", "-s", "-t", "man", "-o", "man/virt-scenario.1",]
    cmd = ["echo", "BYPASSING"]
    if subprocess.call(cmd) != 0:
        raise RuntimeError("Building man pages has failed")
    else:
        print("Man pages generated successfully")

class CleanCommand(setuptools.Command):
    """
    Our custom command to clean out junk files.
    """
    description = "Cleans out junk files we don't want in the repo"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        cmd_list = dict(
            rm_build_stuff="rm -vrf build dist",
            rm_man="rm -vf man/*.1",
            rm_src_egg="rm -vrf src/*.egg-info/",
            rm_pycache="rm -vrf src/*/__pycache__/",
        )
        [os.system(cmd) for cmd in cmd_list.values()]

class CheckLint(setuptools.Command):
    """
    Check python source files with pylint and black.
    """

    def __init__(self):
        """
        init some stuff
        """
        errors_only = ""

    user_options = [("errors-only", "e", "only report errors")]
    description = "Check code using pylint"

    def initialize_options(self):
        """
        Initialize the options to default values.
        """
        self.errors_only = False

    def finalize_options(self):
        """
        Check final option values.
        """
        pass

    def run(self):
        """
        Call black and pylint here.
        """
        pylint_opts = None
        if self.errors_only:
            pylint_opts.append("-E")

        processes = []
        output_format = "colorized" if sys.stdout.isatty() else "text"
        pylint_opts = ["--output-format=%s" % output_format]

        print(">>> Running pylint ...")
        processes.append(subprocess.run(["pylint", "src"] + pylint_opts))

        sys.exit(sum([p.returncode for p in processes]))


# SdistCommand is reused from the libvirt python binding (GPLv2+)
class SdistCommand(sdist):
    """
    Custom sdist command, generating a few files.
    """

    user_options = sdist.user_options

    description = "ChangeLog; build sdist-tarball."
    GenerateMan()

    def gen_changelog(self):
        """
        Generate ChangeLog file out of git log
        """
        cmd = "git log '--pretty=format:%H:%ct %an  <%ae>%n%n%s%n%b%n'"
        fd1 = os.popen(cmd)
        fd2 = open("ChangeLog", "w")

        for line in fd1:
            match = re.match(r"([a-f0-9]+):(\d+)\s(.*)", line)
            if match:
                timestamp = time.gmtime(int(match.group(2)))
                fd2.write(
                    "%04d-%02d-%02d %s\n"
                    % (
                        timestamp.tm_year,
                        timestamp.tm_mon,
                        timestamp.tm_mday,
                        match.group(3),
                    )
                )
            else:
                if re.match(r"Signed-off-by", line):
                    continue
                fd2.write("    " + line.strip() + "\n")

        fd1.close()
        fd2.close()

    def run(self):
        if not os.path.exists("build"):
            os.mkdir("build")

        if os.path.exists(".git"):
            self.gen_changelog()

        sdist.run(self)

        if os.path.exists(".git"):
            files = ["ChangeLog"]
            [os.unlink(item) for item in files if os.path.exists(item)]


setuptools.setup(
    name="virt-scenario",
    version="0.7.4",
    author="Antoine Ginies",
    author_email="aginies@suse.com",
    description="Virt-scenario",
    license="GPLv3",
    long_description=read("README.md"),
    url="https://github.com/aginies/virt-scenario",
    keywords="virtualization",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "virt-scenario = virtscenario.main:main",
            "virt-scenario-launch = virtscenario_launch.main:main",
            "virt-select-firmware = virt_select_firmware.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2)",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={
        "install": PostInstallCommand,
        "lint": CheckLint,
        "sdist": SdistCommand,
        "clean": CleanCommand,
    },
    data_files=[("share/man/man1", ["man/virt-scenario.1"]),
                ("share/virt-scenario/", glob("src/virt-scenario/*.py")),
                (("share/virt-scenario", ["src/virtscenario.yaml"])),
                (("share/virt-scenario", ["src/virthosts.yaml"])),
               ],
    extras_require={"dev": ["pylint"]},
    install_requires=['PyYAML', 'pyudev', 'libvirt-python'],
)
