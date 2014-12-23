The relayr Python Library
=========================

Welcome to the relayr Python Library. The repository provides you Python
developers with programmatic access points to the relayr platform.

These include access to the relayr cloud via the relayr API_ as well as 
direct connection to the relayr WunderBar sensors, via Bluetooth Low
Energy (using BlueZ_ on Linux).


Installation
--------------

You can install the library using one of the following methods, with the
help of Pip:

1. You can download the very latest version of the repository from GitHub::

    pip install git+https://github.com/relayr/python-sdk

2. You may use the following to install the package from the `Python Package Index`_::

    pip install relayr


Examples
--------

Receive data for 10 seconds from a private device of your WunderBar
(you can obtain your device IDs e.g. from your `relayr Dashboard`_):

.. code-block:: python

    import time
    from relayr import Client
    c = Client(token='<my_access_token>')
    dev = c.get_device(id='<my_device_id>').get_info()
    user = c.get_user()
    app = c.get_app()
    def callback(message, channel):
        print(repr(message), type(message))
    conn = user.connect_device(app, dev, callback)
    conn.start()
    time.sleep(10)
    conn.stop()

Switch on/off an LED light on a device:

.. code-block:: python

    from relayr import Client
    c = Client(token='<my_access_token>')
    d = c.get_device(id='<my_device_id>')
    d.switch_led_on(True)


Documentation
-------------

For references to the full documenation for the Python library please visit
our Developer Dashboard `Python section`_!

.. _repository: https://github.com/relayr/python-sdk
.. _API: https://developer.relayr.io/documents/relayrAPI/Introduction
.. _Python Package Index: https://pypi.python.org/pypi/relayr/
.. _BlueZ: http://www.bluez.org/
.. _Python section: https://developer.relayr.io/documents/Python/Introduction
.. _relayr Dashboard: https://developer.relayr.io/dashboard/devices
