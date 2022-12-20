# GOALS

**EXPERIMENTATION** FOR [SUSE ALP OS](https://documentation.suse.com/alp/all/)

**WIP**

Prepare XML libvirt configuration file and prepare the host.

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

Will create **VM.xml** and validate it. Currently 

```chmod 755 main.py
./main.py
```
