Python Relayr Client
====================

Official client for the `Relayr`_ RESTful API. Its goal is to provide common
ground for all Relayr-related code in Python. At the moment this comprises
access to the `Relayr`_ cloud via the `Relayr API`_, as well as some very
experimental direct access to local Wunderbar devices (sensors) via Bluetooth
LE (using `BlueZ`_ on Linux).


Installation
------------

The recommended installation tool of choice is `Pip`_.

You can install the very latest code of the ``relayr`` package from GitHub::

    pip install git+https://github.com/relayr/python-sdk

or as a released package from the `Python Package Index`_ (as soon as it
will be uploaded there)::

    pip install relayr

For more options please consult the documentation.


Examples
--------

Switch on/off an LED light on a device:

.. code-block:: python

	from relayr import Client
	c = Client(token='<my_access_token>')
	d = c.get_device(deviceID='<my_device_id>')
	d.switch_led_on(True)

Receive data from a device:

.. code-block:: python

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


Documentation
-------------

The existing documentation can be found in the ``docs`` subdirectory of the
source code distribution and can be rendered into various formats. 
`Full documentation`_ will also be provided on `Read The Docs`_, soon.


License
-------

MIT License. See ``LICENCE.txt`` file contained in this package.


.. _Relayr: http://relayr.io/
.. _Relayr API: https://developer.relayr.io/documents/relayr%20API/Introduction/
.. _Python Package Index: https://pypi.python.org/pypi/relayr/
.. _Full documentation: http://relayr.readthedocs.org/
.. _Read The Docs: http://readthedocs.org/
.. _Pip: https://pip.readthedocs.org/
.. _BlueZ: http://www.bluez.org/
