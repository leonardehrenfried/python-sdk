# The relayr Python Library

Welcome to the relayr Python Library. [The repository](https://github.com/relayr/python-sdk) provides Python developers with  programmatic access points to the relayr platform.

These include access to the relayr cloud via the [relayr API](https://developer.relayr.io/documents/relayrAPI/Introduction) as well as direct connection to the relayr WunderBar sensors, via Bluetooth Low Energy (using [BlueZ](http://www.bluez.org/) on Linux). 


## Installation

You can install the library using one of the following methods, using Pip: 

1. You can download the very latest version of the repository from GitHub:

    	pip install git+https://github.com/relayr/python-sdk

2. You may us the following to install the package from the [Python Package Index](https://pypi.python.org/pypi):

    
		pip install relayr


## Usage Examples


### Switching on/off an LED light on a device:

	from relayr import Client
	c = Client(token='<my_access_token>')
	d = c.get_device(deviceID='<my_device_id>')
	d.switch_led_on(True)

### Receiving data from a device:

	import time
	from relayr import Client
	c = Client(token='<my_access_token>')
	d = c.get_device(deviceID='<my_device_id>').get_info()
	def callback(message, channel):
	    print(repr(message), type(message))
	user = c.get_user()
	conn = user.connect_device(d, callback)
	conn.start()
	time.sleep(10)
	conn.stop()

## Full Documentation Reference

The full reference of the package could be obtained in one of the following methods: 

1. The documentation may be found in the ***Docs*** sub directory in the Github repository and it can be rendered in various formats. Please see instructions on how to achieve this [here](http://) 


2. You may access the full reference on the [Read the Docs](http://https://readthedocs.org/) website.
