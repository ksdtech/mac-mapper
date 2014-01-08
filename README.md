mac-mapper
==========
web.py application to register Chromebook MAC addresses.

Looks up DHCP leases from an ISC DHCP server using the OMAPI
protocol and the remote IP address of the request.

Appends results to a .csv file.

Requirements
------------
* Python 2.6 or above
* web.py package
* netaddr package
* pypureomapi package
