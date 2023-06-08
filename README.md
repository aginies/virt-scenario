# Name

virt-scenario - Create XML config and prepare host for a specific scenario

# Goals

This is an **EXPERIMENTATION** project for [SUSE ALP OS](https://documentation.suse.com/alp/all/)

It prepares a libvirt XML guest configuration and the host to run a customized guest.
Idea is to use multiple **templates** and concatenate them to create the
expected Guest XML file.

IE: setting up a secure VM is not so easy from scratch, this tool will prepare the host,
the XML guest config with secure parameter, and will deal with all the certificate, attestation
and launch measurement. In only 2 commands you can start a secure VM on an AMD SEV system!
It also simplify the usage of disk Image encryption.

Customization to match a specific scenario is not graved in stone. The idea is to
prepare a configuration which should improved the usage compared to a basic setting.
This will **NOT guarantee** that this is perfect as this higly depends on your current system.

[![virt-scenario](https://img.youtube.com/vi/RKoRu2UVEtU/0.jpg)](https://www.youtube.com/watch?v=RKoRu2UVEtU)


# User Settings

User can set some parameter in the **/etc/virt-scenario/virtscenario.yaml**.
This will override the scenario settings. A table will be displayed showing the recommended settings VS the current one.

Example:
```yaml
# WARNING: INCORRET PARAMATERS WILL LEAD TO BAD VM CONFIGURATION
# Dont change the section name
# This will overwrite scenario settings....
config:
  - path: /etc/virt-scenario
  - vm-config-store: /etc/virts-scenario/vmconfig
emulator:
  - emulator: /usr/bin/qemu-system-x86_64
input:
  - keyboard: virtio
  - mouse: virtio
architecture:
  - arch: x86_64
STORAGE_DATA:
# some options are only available with qcow2 format and
# will be ignored in case of any other image format
  - disk_type: file
#  - disk_cache: none
  - disk_target: vda
  - disk_bus: virtio
  - path: /var/livirt/images
  - format: qcow2
# host side: qemu-img creation options (-o), qemu-img --help
  - unit: G
  - capacity: 20
  - cluster_size: 1024
  - lazy_refcounts: on
# preallocation: off, metadata (qcow2), falloc, full
  - preallocation: off
  - compression_type: zlib
  - encryption: off
host_filesystem:
  - fmode: 644
  - dmode: 755
  - source_dir: /tmp
  - target_dir: /tmp/host
```

**/etc/virt-scenario/virthosts.yaml** is used to define an Hypervisors list mostly for secure VM configuration.
```yaml
localhost:
  url: qemu:///system
# Generate with 'sevctl export --full filename.pdh' on the given host
  sev-cert: /path/to/host-cert-chain.pdh
```

# Usage

## Get it and use it

### From source code

**main.py** will create an **xml** based file on template and validate it.
It will also prepare the host system and create the VM image file.
Currently **desktop**, **computation** and **securevm** are available.

```
git clone https://github.com/aginies/virt-scenario.git
cd virt-scenario/src
python3 -m virtscenario
> conf virtscenario.yaml
> desktop
```

Tool to select a firmware based on feature:
```
python3 -m virt_select_firmware
```

Tool to launch the VM from the config file generated by virt-scenario:
```
python3 -m virtscenario-launch
```

GTK virt-scenario:
```
python3 -m vsmygtk
```

### From Package

Get the package for your Distribution and install it. For openSUSE, SLES:

* [devel stable project](https://build.opensuse.org/package/show/Virtualization/virt-scenario)
* [devel unstable](https://build.opensuse.org/package/show/home:aginies/virt-scenario)

You should run this tool as **root** to configure host part, for the Gtk you can use **gnomesu**
to launch it as root.

* **virt-scenario**: CMD Interactive mode (console)
* **virt-scenario-gtk**: The GTK interface

### virt-scenario as an API

**virt-scenario** is usable from **Cmd Interactive** or using a **GTK interface**.
It also provides an **API**. A commented [Demo example](src/demo_api_usage.py) file is available.

## Default configuration

The default configuration for VM definition are:
* **disk path image**: /var/libvirt/qemu
* **arch**: x86_64
* **machine**: pc-q35-6.2
* **boot_dev**: hd
* **emulator**: /usr/bin/qemu-system-x86_64
* **input**: keyboard and mouse as virtio

They could be overwriten by the choosen scenario.

Depending on scenario the default will change to some other value.

## Interactive commands

### virt-scenario configuration

* **overwrite**: Force overwrite previous setting
* **mode**: Guest/Host/Both mode
* **conf**: Setting the virt-scenario configuration file

### Hypervisor configuration

* **hvconf**: Load Hypervisor configuration
* **hvselect**: Set hypervisor for which VMs are configured
* **hvlist**: List available hypervisors
* **force_sev**: Force the extract of a localhost PDH file. This is **NOT secure** as this file should be stored in a secure place! Only for demo purpose

### Guest configuration 

* **name**: Define a name for the VM
* **vcpu**: Choose how many VCPU
* **memory**: Choose the Memory size (in GiB)
* **vnet**: Virtual Network for the VM
* **machine**: Select the Machine type (from a list)
* **bootdev**: Select the boot dev (from a list)
* **cdrom**: File Path to CD/DVD installation media
* **vmimage**: File path to an already existing VM image

### Storage Guest configuration

* **capacity**: Disk Size image (GiB)
* **format**: Select the Disk Image format (qcow2/raw)
* **cache**: Specify the Disk Cache mode
* **encryption**: Encrypt the VM Disk image
* **diskpath**: Directory where to store disk image

### Generate the XML configuration and prepare the host

* **computation**: Create an XML configuration and host config to do computation VM
* **desktop**: Create an XML configuration and host config for Desktop VM
* **securevm**: Create an XML configuration and host config for Secure VM 

### Others

* **shell**: Execution of a system command
* **info**: Get current host information about CPU and Memory

# Possible Scenarios

## Default Settings Comparison 

This settings should be better than default one. Of course this is not perfect,
and there is maybe some mistakes. Feel free to comment on this parameters or request
addition of new one.

[default_settings](DEFAULT_SETTINGS.md)

## Not yet ready

* Testing an OS
* Easy migration of VM
* Soft RT VM (latency improvments)

# Devel Information

This is still **WIP**, but the code is relatively stable.

## Devel planning / TODO

* ~~mechanism to create the Guest XML file from template~~
* ~~define all scenarios (list)~~
* ~~post customization of XML config~~
* ~~show host configuration~~
* ~~implement interactive shell~~
* ~~check if running inside a container (for host configuration)...~~
* ~~do more configuration on the Host side~~
* ~~create needed files on host: images, network definition, etc...~~
* ~~define conflict/compatibility between scenarios (is this still needed?)~~
* improve customization based on scenario (need to get some QA on this...)

## Code

[Source](https://github.com/aginies/virt-scenario)

[Issues](https://github.com/aginies/virt-scenario/issues)

## Class / Functions

All scenarios are define in the **Scenarios** class. It can do direct
configuration calling **BasicConfiguration.XXX** or **ComplexConfiguration.XXX**,
or request a specific features calling **Features.XXX**. User setting always
overwrite any values set automatically by scenario.

[Scenarios()](src/virtscenario/scenarios.py#L24)
```
class Scenarios()
	-> BasicConfiguration.XXX
	-> ComplexConfiguration.XXX
	-> Features.XXX
```

[Features()](src/virtscenario/features.py#L50)
```
class Features()
	-> XXX_perf() -> BasicConfiguration.XXX
                  -> ComplexConfiguration.XXX
```

[BasicConfiguration()](src/virtscenario/dict.py#L20)
```
class BasicConfiguration()
	name(self, name)
	vcpu(self, vcpu)
	cpumode_pass(self, migratable, extra)
	power(self, suspend_to_mem, suspend_to_disk)
	audio(self, model)
	input(self, inputtype, bus)
	usb(self, model)
	watchdog(self, model, action)
	emulator(self, emulator)
	memory(self, unit, max_memory, memory)
	osdef(self, arch, machine, boot_dev)
	ondef(self, on_poweroff, on_reboot, on_crash)
	features(self, features)
	clock(self, clock_offset, clock)
	iothreads(self, iothreads)
	security_f(self, sectype, secdata)
	video(self, model_type)
```

[ComplexConfiguration()](src/virtscenario/dict.py#L214)
```
ComplexConfiguration()
	disk(self, disk)
	network(self, mac, network, intertype, iommu)
	access_host_fs(self)
	tpm(self, tpm_model, tpm_type, device_path)
	tpm_emulated(self, tpm_model, tpm_type, version)
    access_host_fs(self, fmode, dmode, source_dir, target_dir)
```

## Templates definition

All templates are in the python lib **virt-scenario/template.py** file.

## Files (virtscenario)

* [virtscenario.yaml](src/virtscenario.yaml): user setting (overwrite scenario settings)
* [virthosts.yaml](src/virthosts.yaml) Hypervisors list and settings
* [libvirt.py](src/virtscenario/libvirt.py) Wrapper for getting libVirt domain capabilities
* [firmware.py](src/virtscenario/firmware.py) Select the firmware with the required feature-set
* [sev.py](src/virtscenario/sev.py) Get parameters for configuring an SEV or SEV-ES VM and do detaction
* [template.py](src/virtscenario/template.py) libvirt XML template definition
* [scenario.py](src/virtscenario/scenario.py) different call to create the XML based on the selected scenario
* [dict.py](src/virtscenario/dict.py) create the dict with data to file the template
* [configuration.py](src/virtscenario/configuration.py) all stuff related to configuration
* [features.py](src/virtscenario/features.py) prepare some features for the VM
* [host.py](src/virtscenario/host.py) create the storage and prepare the host
* [guest.py](src/virtscenario/guest.py) create dict to file all the templates
* [immutable.py](src/virtscenario/immutable.py) Immutable data (to be removed when implementation will be done...)
* [qemulist.py](src/virtscenario/qemulist.py) provide list of available options in qemu and some default path
* [util.py](src/virtscenario/util.py) internal needed functions
* [cmd.py](src/virtscenario/cmd.py) Python CMD interactive part
* [main.py](src/virtscenario/main.py) launch the tool and create the final XML file and host configuration
* [hypervisors.py](src/virtscenario/hypervisors.py) list, select, connect to an hypervisor (or any other HV action)
* [configstore.py](src/virtscenario/configstore.py) Guest configuration store (used mostly for Confidential computing)

## Host configuration

* check CPU flag: sev, sev-es, pdpe1gb, pse
* check SEV on the system and libvirt enablement
* enable an AMD SEV system
* generate SEV attestation and update VM XML
* configure HugePages and THP
* enable/disable KSM
* adjust swappiness
* manage IO scheduler

## Possible Guest VM Features

* CPU performance
* System features
* Security
* Memory performance
* Storage performance
* Video (virtio or others)
* Network performance
* Clock performance
* Using host hardware
* Access host OS filesystem
* AMD SEV
* select right firmware for VM guest
* Disk Encryption

## Stuff currently immutable

This is currently not changeable using the template, this needs to be adjusted in the futur (or not...):
* console_data
* channel_data
* memballoon_data
* rng_data
* Memory Backing
* metadata_data
* only support 1 disk per VM

# Example with securevm (Confidential Computing)

virt-scenario currently only support setting secure Virtual Machine on AMD SEV or SEV-ES system.
For more information about SUSE and SEV please refer to [SLES AMD SEV](href="https://documentation.suse.com/sles/15-SP4/single-html/SLES-amd-sev/).

## Prepare  Your VM

virt-scenario provides different options to configure the Virtual Machine.
In our example we will set different parameters to suit our needs, most of them
provides completion using the [TAB] key:

```
name ALPOS
vcpu 4
memory 8
vnet default
bootdev hd
vmimage /var/lib/libvirt/images/ALP-VM.x86_64-0.0.1-kvm_encrypted-Snapshot20230309.qcow2
force_sev on
```

This end up with a prompt like:
```
---------- User Settings ----------
Disk Path: /var/lib/libvirt/images
Main Configuration: /etc/virt-scenario/virtscenario.yaml
Hypervisor Configuration: /etc/virt-scenario/virthosts.yaml
Force SEV PDH extraction: on
Name: ALPOS
Vcpu: 4
Memory: 8
Boot Device: hd
Virtual Network: default
VM Image file: /var/lib/libvirt/images/ALP-VM.x86_64-0.0.1-kvm_encrypted-Snapshot20230309.qcow2
```

## Generate XML and prepare the host

You are ready to run **securevm** to prepare the host system and generate the XML libvirt config:
```
securevm
```

The generated XML file is available in **~/etc/virt-scenario/vmconfig/ALPOS/domain.xml**. You can also find
 a **config.yaml** which contains host data about this VM. In our case **attestation** will be set to
true, the host will be **localhost**. The **/etc/virt-scenario/virthosts.yaml** will be updated to
configure the correct path to the extracted PDH file (sev-cert).

## Launch the VM

Launch the VM with the **virt-scenario-launch** tool:
```shell
# virt-scenario-launch --start ALPOS
Connected to libvirtd socket; Version: 7001000
SEV(-ES) attestation passed!
Validation successfull for domain ALPOS
```

# Authors

Written by Antoine Ginies

Contributors: Joerg Roedel

