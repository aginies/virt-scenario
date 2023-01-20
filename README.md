# GOALS

**EXPERIMENTATION** FOR [SUSE ALP OS](https://documentation.suse.com/alp/all/)

Prepare a libvirt XML guest configuration and the host to run a customized guest.
Idea is to use multiple **templates** and concatenate them to create the
expected Guest XML file. If Host need a custom setting it will be done in second phase.

Customization to match a specific scenario is not graved in stone. The idea is to
prepare a configuration which should improved the usage compared to a basic setting.
This will **NOT guarantee** that this is perfect.

![image](images/virt-scenario.jpg)
![image](images/user_setting.jpg)
![image](images/secure_vm.jpg)
![image](images/end_process.jpg)

# Devel Information

This **WIP**, a lot of changes can occur in current code.

# Devel planning / TODO

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

# User settings

see [manpage virt-scenario](man/virt-scenario.pod)

# Default configuration

The default configuration for VM definition is:
* **disk path image**: /var/libvirt/qemu
* **arch**: x86_64
* **machine**: pc-q35-6.2
* **boot_dev**: hd
* **input**: keyboard and mouse as virtio

Depending on scenario the default will change to some other value.

# Host configuration

* check CPU flag: sev, pdpe1gb, pse
* check SEV libvirt enablement
* enable an AMD SEV system
* check if running in a container and display host config to apply
* configure Huge Pages
* enable/disable KSM
* adjust swappiness
* manage IO scheduler

# Possible Features

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

# Possible Scenarios

WIP:
* Computation
* Desktop
* Secure VM

Not yet ready:
* Testing an OS
* Easy migration of VM
* Soft RT VM

# Stuff currently immutable

This is currently not changeable using the template, this needs to be
adjusted in the futur:
* console_data
* channel_data
* graphics_data
* memballoon_data
* rng_data
* metadata_data
* controller_data
* only support 1 disk per VM

# Class / Functions

All scenarios are define in the **Scenarios** class. It can do direct
configuration calling **BasicConfiguration.XXX** or **ComplexConfiguration.XXX**,
or request a specific features calling **Features.XXX**. User setting always
overwrite any values set automatically by scenario.

```
class Scenarios()
	-> BasicConfiguration.XXX
	-> ComplexConfiguration.XXX
	-> Features.XXX
```

```
class Features()
	-> XXX_perf() -> BasicConfiguration.XXX
		      -> ComplexConfiguration.XXX
```

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
	security(self, sectype, secdata)
	video(self, model_type)
```

```
ComplexConfiguration()
	disk(self, disk)
	network(self, mac, network, intertype, iommu)
	access_host_fs(self)
	tpm(self, tpm_model, tpm_type, device_path)
	tpm_emulated(self, tpm_model, tpm_type, version)
```

# Files (WIP)

* **virtscenario.yaml**: user setting (overwrite scenario settings)
* **template.py**: libvirt XML template definition
* **scenario.py**: different call to create the XML based on the selected scenario
* **configuration.py**: create the dict with data to file the template
* **features.py**: prepare some features for the VM
* **host.py**: create the net xml file and the storage, prepare the host
* **guest.py**: create dict to file all the templates
* **immutable.py**: Immutable data (to be removed when implementation will be done...)
* **qemulist.py**: provide list of available options in qemu and some default path
* **util.py**: needed functions
* **main.py**: launch the tool and create the final XML file and host configuration

# Usage

**main.py** will create an **xml** based file on template and validate it.
Second phase will prepare the host system and create the VM image file.
Currently **desktop**, **computation** and **securevm** are available.

```
git clone https://github.com/aginies/virt-scenario.git
cd virt-scenario/src
python3 -m virtscenario
```
