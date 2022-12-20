# GOALS

**EXPERIMENTATION** FOR [SUSE ALP OS](https://documentation.suse.com/alp/all/)

**WIP**

Prepare XML libvirt configuration file and prepare the host.
Two methodes under testing: using **virt-install** and some parameters, or using
**template** for all part of the XML file.

# Scenarios

* CPU performance
* Storage performance
* Video performance
* Network performance
* Using host hardware
* Easy migration of VM
* Computation
* Access host OS filesystem
* Testing an OS
* Secure VM
* Soft RT VM

# Files

* **template.py**: define all part of the XML configuration
* **main.py**: do all stuff. Also contains XML parameter, this will be move to scenarios

# Usage

Will create **VMa.xml** with **virt-install**.
This will also create **VMb.xml** based on template and validate it.

```chmod 755 main.py
./main.py
```
