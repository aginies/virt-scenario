# GOALS

**EXPERIMENTATION** FOR [SUSE ALP OS](https://documentation.suse.com/alp/all/)

Prepare a libvirt XML guest configuration and the host to run a customized guest.
Idea is to use multiple **templates** and concatenate them to create the
expected Guest XML file.

![image](https://github.com/aginies/virt-scenario/blob/6a540c45370de784edcef4ba7e692777cffa28fd/virt-scenario.jpg)

# Devel Information

A lot of variable are currently set in the code and will be changeable in the futur
(FEATURES_DATA, CLOCK_DATA, ON_DATA, TPM_DATA, etc...)
Still lot of work TODO...

# Devel planning / TODO

* mechanism to create the Guest XML file from template
* define all scenarios (list)
* post customization of XML config
* define conflict/compatibility between scenarios
* improve customization based on scenario
* show host configuration
* create needed files on host (images, network definition, etc...)
* ~~implement interactive shell~~

# Possible Features

* CPU performance
* Video performance
* Network performance
* Storage performance
* Using host hardware
* Access host OS filesystem

# Possible Scenarios

* Easy migration of VM
* Computation
* Testing an OS
* Secure VM
* Soft RT VM

# Class available

All scenarios are define in the **Scenarios** class. It can do direct
configuration calling **BasicConfiguration.XXX** or **ComplexConfiguration.XXX**,
or request a specific features calling **Features.XXX**

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

# Files (WIP)

* **template.py**: libvirt XML template definition
* **scenario.py**: all the action to create the scenario are done there
* **proto_host.py**: create the net xml file and the storage
* **proto_guest.py**: create dict to file all the template
* **immutable.py**: Immutable data (to be removed ...)
* **util.py**: needed functions
* **main.py**: launch the tool and create the final XML file

# Usage

**main.py** will create an *xml** based file on template and validate it.
Currently **desktop** and **computation** are available.

```
chmod 755 main.py
./main.py
```
