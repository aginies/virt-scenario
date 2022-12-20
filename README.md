# GOALS

**EXPERIMENTATION** FOR [SUSE ALP OS](https://documentation.suse.com/alp/all/)


Prepare XML libvirt configuration file and prepare the host.
Using **template** for all part of the XML file.

**WIP**
* First Phase: mechanism to create the XML file (mostly done)
* Second Phase: define all configs for all scenarios

# Possible Scenarios (NOT YET IMPLEMENTED)

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

This will create **VMb.xml** based on template and validate it.

```
chmod 755 main.py
./main.py
```
