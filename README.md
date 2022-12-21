# GOALS

**EXPERIMENTATION** FOR [SUSE ALP OS](https://documentation.suse.com/alp/all/)

Prepare a libvirt XML guest configuration and the host to run a customized guest.
Idea is to use multiple **templates** and concatenate them to create the
expected Guest XML file.

# Devel planning / TODO

* mechanism to create the Guest XML file from template
* define all scenarios (list)
* post customization of XML config
* define conflict/compatibility between scenarios
* improve customization based on scenario
* host configuration
* create needed files on host (images, network definition)

# Possible Scenarios

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

# Files (WIP)

* **template.py**: libvirt template definition
* **scenario.py**: all the action to create the scenario are done
* **proto_host.py**: create the net xml file and the storage
* **proto_guest.py**: create dict to file the template
* **util.py**: needed functions
* **main.py**: launch the tool

# Usage

**main.py** will create **VMb.xml** based on template and validate it.

```
chmod 755 main.py
./main.py
```
