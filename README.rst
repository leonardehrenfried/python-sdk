The relayr Python Library
=========================

Welcome to the relayr Python Library. The repository provides Python
developers with programmatic access points to the relayr platform.

These include access to the relayr cloud via the relayr API_ as well as 
direct connection to the relayr WunderBar sensors, via Bluetooth Low
Energy (using BlueZ_ on Linux, still very experimental).


Installation
--------------

You can install the library using one of the following methods, with the
help of Pip:

1. You can download the very latest version of the repository from GitHub::

    pip install git+https://github.com/relayr/python-sdk

2. You could also use the following to install the package from the `Python Package Index`_::

    pip install relayr

.. attention::

    Receiving data via MQTT will work only for Python 2.7 and above
    due to limited suport in ``paho-mqtt`` for TLS in Python 2.6.

Examples
--------

Receive a 10 second data stream, from one of your WunderBar sensors (device). In the
example below the device does not have to be a public one in order to be used. 
You can obtain your device IDs from the relayr Dashboard `My Devices section`_:

MQTT_ style (new)
.................

.. code-block:: python

    import time
    from relayr import Client
    from relayr.dataconnection import MqttStream
    c = Client(token='<my_access_token>')
    dev = c.get_device(id='<my_device_id>')
    def mqtt_callback(topic, payload):
        print('%s %s' % (topic, payload))
    stream = MqttStream(mqtt_callback, [dev])
    stream.start()
    time.sleep(10)
    stream.stop()


PubNub_ style (old)
...................

.. code-block:: python

    import time
    from relayr import Client
    c = Client(token='<my_access_token>')
    dev = c.get_device(id='<my_device_id>').get_info()
    user = c.get_user()
    app = c.get_app()
    def pubnub_callback(message, channel):
        print(repr(message), type(message))
    conn = user.connect_device(app, dev, pubnub_callback)
    conn.start()
    time.sleep(10)
    conn.stop()


Switch a device's LED on/off
............................

.. code-block:: python

    from relayr import Client
    c = Client(token='<my_access_token>')
    d = c.get_device(id='<my_device_id>')
    d.switch_led_on(True)


Documentation
-------------

For references to the full documenation for the Python library please visit
our Developer Dashboard `Python section`_!


.. comment:
    .. include:: CHANGELOG.txt


.. _repository: https://github.com/relayr/python-sdk
.. _API: https://developer.relayr.io/documents/relayrAPI/Introduction
.. _Python Package Index: https://pypi.python.org/pypi/relayr/
.. _BlueZ: http://www.bluez.org/
.. _Python section: https://developer.relayr.io/documents/Python/Introduction
.. _My Devices section: https://developer.relayr.io/dashboard/devices
.. _PubNub: http://www.pubnub.com/
.. _MQTT: http://mqtt.org/
.. _its Python client: https://github.com/pubnub/python/
