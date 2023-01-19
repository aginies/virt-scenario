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
Prepare the Host system
"""

import uuid
import os
from string import Template
import virtscenario.template as template
import virtscenario.util as util

def create_net_xml(file, net_data):
    """
    Create a libvirt XML for the network bridge
    """
    xml_template = template.NETWORK_TEMPLATE
    xml_net = {
        'network_uuid': str(uuid.uuid4()),
        'network_name': net_data['network_name'],
        'bridge': net_data['bridge'],
        'stp': net_data['stp'],
        'ip': net_data['ip'],
        'netmask': net_data['netmask'],
        'dhcp_start': '.'.join(net_data['ip'].split('.')[0:3]+[net_data['dhcp_start']]),
        'dhcp_end': '.'.join(net_data['ip'].split('.')[0:3]+[net_data['dhcp_end']]),
    }

    xml = Template(xml_template).substitute(xml_net)
    print("Create network bridge " +file)
    with open(file, 'w') as file_h:
        file_h.write(xml)

def create_storage_vol_xml(file, storage_data):
    """
    Create storage vol xml
    """
    xml_template = template.STORAGE_TEMPLATE
    xml_storage = {
        'storage_uuid': str(uuid.uuid4()),
        'storage_name': storage_data['storage_name'],
        'allocation': storage_data['allocation'],
        'unit': storage_data['unit'],
        'capacity': storage_data['capacity'],
        'path': storage_data['path']+'.'+storage_data['type'],
        'owner': storage_data['owner'],
        'group': storage_data['group'],
        'mode': storage_data['mode'],
        'label': storage_data['label'],
        }

    xml = Template(xml_template).substitute(xml_storage)
    print("Create storage volume " +file)
    with open(file, 'w') as file_h:
        file_h.write(xml)

def create_storage_image(storage_data):
    """
    Create the storage image
    """
    # TOFIX: prealloc metadata only for qcow2 image
    util.print_summary("\nCreating the Virtual Machine image")
    encryption = ""
    #ie: qemu-img create -f qcow2 Win2k.img 20G
    if os.path.isdir(storage_data['path']):
        print(storage_data['path'])
    else:
        util.print_warning(storage_data['path']+" Doesnt exist, creating it")
        try:
            os.makedirs(storage_data['path'], exist_ok=True)
        except Exception:
            util.print_error("Can't create "+storage_data['path']+" directory")
    filename = storage_data['path']+"/"+storage_data['storage_name']+"."+storage_data['format']
    cmd = "qemu-img create"

    # preallocation: off / metadata / falloc, full
    if storage_data['preallocation'] is False:
        preallocation = "preallocation=off"
    else:
        preallocation = "preallocation="+str(storage_data['preallocation'])

    # qcow2 related stuff
    if storage_data['format'] == "qcow2":
        # on / off VS True / False
        lazyref = ""
        if storage_data['lazy_refcounts'] is True:
            lazyref = "lazy_refcounts=on"
        else:
            lazyref = "lazy_refcounts=off"
        # cluster size: 512k / 2M
        clustersize = "cluster_size="+storage_data['cluster_size']
        # zlib zstd
        compression_type = "compression_type="+storage_data['compression_type']

        # encryption on
        if storage_data['encryption'] is True:
        # qemu-img create --object secret,id=sec0,data=123456 -f qcow2
        # -o encrypt.format=luks,encrypt.key-secret=sec0 base.qcow2 1G
            encryption = " --object secret,id=sec0,data="+storage_data['password']
            encryption += " -o "+"encrypt.format=luks,encrypt.key-secret=sec0"

        cmdall = cmd+" -o "+lazyref+","+clustersize+","+preallocation+","+compression_type
        cmdall += " -f "+storage_data['format']
        cmdall += encryption+" "+filename+" "+str(storage_data['capacity'])+storage_data['unit']
    else:
        # this is not a qcow2 format
        cmdoptions = " -o "+preallocation
        cmdoptions += " -f "+storage_data['format']+" "+filename
        cmdoptions += " "+str(storage_data['capacity'])+storage_data['unit']
        cmdall = cmd+" "+cmdoptions

    print(cmdall)
    out, errs = util.system_command(cmdall)
    if errs:
        print(errs)
    if not out:
        print(' No output... seems weird...')
    else:
        print(out)

def check_cpu_flag(flag):
    """
    check if a CPU flag is present
    """
    cpuinfo = open("/proc/cpuinfo")
    data = cpuinfo.read()
    test = data.find(flag)
    cpuinfo.close()
    return test

def check_libvirt_sev():
    """
    check that libvirt support sev
    """
    cmd = "virsh domcapabilities | grep sev"
    out, errs = util.system_command(cmd)
    util.print_summary("\nCheck libvirt support SEV")
    if errs:
        print(errs)
    if out.find("no") != -1:
        util.print_error("Libvirt doesnt Support SEV!")
    else:
        util.print_ok("Libvirt support SEV")
    print(out)

def check_sev_enable():
    """
    check that sev is enable on this system
    """
    sevinfo = open("/sys/module/kvm_amd/parameters/sev")
    #sevinfo = open("/sys/module/kvm/supported")
    data = sevinfo.read()
    test = data.find("Y")
    sevinfo.close()
    return test

def check_in_container():
    """
    check if inside a container
    """
#    if os.environ['container'] != "":
#        return True
    out, errs = util.system_command("systemd-detect-virt -c")
    if errs:
        print(errs)
    if out.find("none") == -1:
        print("You are inside a container, you should do some stuff on the host system....")
        return True

def enable_sev():
    """
    enable sev on the system
    """
    if check_in_container() is True:
        print("Create: /etc/modprobe.d/sev.conf")
        print("options mem_encrypt=on kvm_amd sev=1 sev_es=1")
    else:
        sevconf = open("/etc/modprobe.d/sev.conf", "w")
        sevconf.write("options mem_encrypt=on kvm_amd sev=1 sev_es=1")
        sevconf.close()

def hugepages_enable():
    """
    check that vm.nr_hugepages is not 0
    reserve 1 GB (1,048,576 KB) for your VM Guest (2M hugepages)
    """
    hpconf = "/etc/sysctl.d/hugepages.conf"
    if check_in_container() is True:
        print("Create: /etc/sysctl.d/hugepages.conf")
        print("sysctl vm.nr_hugepages=512")
    else:
        if os.path.isfile(hpconf):
            return True
        else:
            print("Creating "+hpconf)
            fdhp = open(hpconf, "w")
            fdhp.write("vm.nr_hugepages=512")
            fdhp.close()
            out, errs = util.system_command("sysctl vm.nr_hugepages=512")
            util.print_summary("\nSetting vm.nr_hugepages=512")
            if errs:
                print(errs)
            print(out)

def reprobe_kvm_amd_module():
    """
    reload the module
    """
    cmd = "modprobe -vr kvm_amd ; modprobe -v kvm_amd"
    if os.environ['container'] != "":
        print("You are inside a container, you should do this on the host system:")
        print(cmd)
    else:
        out, errs = util.system_command(cmd)
        util.print_summary("\nReprobe the KVM module")
        if errs:
            print(errs)
        print(out)

def kvm_amd_sev():
    """
    be sure kvm_amd sev is enable if not enable it
    https://documentation.suse.com/sles/15-SP1/html/SLES-amd-sev/index.html
    """
    util.print_summary("Host section")
    util.print_summary("Enabling sev if needed")
    check_libvirt_sev()
    flag = "sev"
    test_flag = check_cpu_flag(flag)
    if test_flag <= -1:
        util.print_error(" "+flag+" CPU flag not found...")
        util.print_error("WARNING: You can not do secure VM on this system (SEV)")
    else:
        util.print_ok("Found "+flag+" CPU flag")
        test_sev = check_sev_enable()
        if test_sev <= -1:
            util.print_error(" SEV not enabled on this system")
            enable_sev()
            reprobe_kvm_amd_module()
        else:
            util.print_ok(" SEV enabled on this system")

def hugepages():
    """
    prepare system to use hugepages
    https://documentation.suse.com/sles/15-SP4/single-html/SLES-virtualization-best-practices/#sec-vt-best-mem-huge-pages
    """
    #pdpe1gb pse
    flaglist = ["pdpe1gb", "pse"]
    foundok = False
    for flag in flaglist:
        test_flag = check_cpu_flag(flag)
        if test_flag <= -1:
            util.print_error(" "+flag+" CPU flag not found...")
        else:
            util.print_ok("Found "+flag+" CPU flag")
            foundok = True
    if foundok is True:
        hugepages_enable()
    else:
        util.print_error("There is no hugepages support on this system")

def host_end(filename, overwrite, toreport):
    """
    end of host configuration
    """
    if overwrite is True:
        util.print_warning("You are over writing scenario setting!")
        util.print_recommended(toreport)
    util.print_summary_ok("\nHost Configuration is done")
    util.print_ok("To use it:\nvirsh define "+filename)

# Net data
NET_DATA = {
    'network_name': "test_net",
    'bridge': "br0",
    'stp': "on",
    'ip': "192.168.12.1",
    'netmask': "255.255.255.0",
    'dhcp_start': "30",
    'dhcp_end': "254",
}
#create_net_xml("net.xml", NET_DATA)
