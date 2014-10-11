# -*- coding: utf-8 -*-

"""
Functionality for working with Bluetooth, especially LE (Low Energy).

Since PyBluez doesn't support Bluetooth LE this module provides an abstraction
on the tools ``hcitool`` and ``gatttool``.

.. code-block:: python

    >>> from ble import scan_ble_devices
    >>> scan_ble_devices()
    [{'addr': 'F4:D7:AB:6D:EB:D5', 'name': 'WunderbarMIC'},
     {'addr': 'C3:18:9B:AF:F6:F1', 'name': 'WunderbarBRIDG'},
     ...
     {'addr': 'F2:EE:50:45:39:74', 'name': 'WunderbarGYRO'}]
"""

import re
import sys
import time

import commands
import pexpect


## TODO: convert to using commands instead of pexpect
def scan_ble_devices(hci_name='hci0', name_filter='.*', timeout=1):
    """
    Return list of discovered Bluetooth LE devices with address and name.
    
    Attention: This must be run with sudo permissions!

    :param hci_name: the HCI device name
    :type hci_name: string
    :param name_filter: a regular expression that service names need to match
    :type name_filter: string
    :param timeout: the timeout value for the scan duration in seconds
    :type timeout: string
    :rtype: a list of dicts, one per device, each with a name and addr entry

    Sample output::
    
        [{'addr': 'F4:D7:AB:6D:EB:D5', 'name': 'WunderbarMIC'},
         {'addr': 'C3:18:9B:AF:F6:F1', 'name': 'WunderbarBRIDG'},
         {'addr': 'D0:DA:36:13:EB:39', 'name': 'WunderbarIR'},
         {'addr': 'DE:7F:20:07:AD:04', 'name': 'WunderbarHTU'},
         {'addr': 'F2:84:DC:44:D7:5C', 'name': 'WunderbarLIGHT'},
         {'addr': 'E9:5D:10:B9:E2:1C', 'name': 'WunderbarMIC'},
         {'addr': 'F2:EE:50:45:39:74', 'name': 'WunderbarGYRO'}]
    """
    
    conn = pexpect.spawn('hciconfig %s reset' % hci_name) # needs sudo
    time.sleep(0.2)

    conn = pexpect.spawn('timeout %d hcitool lescan' % timeout) # needs sudo
    time.sleep(0.2)

    conn.expect('LE Scan \.+', timeout=timeout)
    # time.sleep(timeout)

    output = ''
    line_pat = '(?P<addr>([0-9A-F]{2}:){5}[0-9A-F]{2}) (?P<name>.*)'
    
    while True:
        try:
            res = conn.expect(line_pat)
            output += conn.after
        except pexpect.EOF:
            break
      
    lines = re.split('\r?\n', output.strip())
    lines = list(set(lines))
    lines = [line for line in lines if re.match(line_pat, line)]
    lines = [re.match(line_pat, line).groupdict() for line in lines]
    lines = [line for line in lines if re.match(name_filter, line['name'])]
    
    return lines


class GattDevice(object):
    """
    A class to communicate via GATT with a Bluetooth LE device.

    This class uses the Bluez ``getttool`` in a non-interactive manner.
    """
    
    def __init__(self, bluetooth_addr):
        """
        The ``bluetooth_addr`` parameeter is the MAC address of the device.
        """

        self.addr = bluetooth_addr
        self.data = {
            'services': [],
            'characteristics': [],
            'char-desc': [],
            'read_log': [], # log of read data: {'ts':..., ''handle':..., 'bytes':...}
            'write_log': []  # log of written data: same...
        }
        self.callbacks = {}

    def primary(self):
        """
        Discover primary services.
        """

        # example line format:
        # 'attr handle = 0x0001, end grp handle = 0x0007 uuid: 00001800-0000-1000-8000-00805f9b34fb'
        res = commands.getoutput('gatttool -t random -b %s --primary' % self.addr)        
        lines = re.split('\r?\n', res)
        lines = sorted(set(lines))
        self.data['services'] = lines
        return lines

    def characteristics(self):
        """
        Read list of characteristics.
        """

        # example line format:
        # 'handle = 0x0002, char properties = 0x02, char value handle = 0x0003, uuid = 00002a00-0000-1000-8000-00805f9b34fb'
        res = commands.getoutput('gatttool -t random -b %s --characteristics' % self.addr)
        lines = re.split('\r?\n', res)
        self.data['characteristics'] = lines
        return lines

    def char_desc(self):
        """
        Read list of characteristic descriptors.
        """

        # example line format:
        # 'handle = 0x000e, uuid = 00002010-0000-1000-8000-00805f9b34fb'
        res = commands.getoutput('gatttool -t random -b %s --char-desc' % self.addr)
        lines = re.split('\r?\n', res)
        # lines = re.findall('handle: .* uuid: [0-9a-f\-]{36}', res)
        self.data['char-desc'] = lines
        return lines

    def char_read_hnd(self, handle):
        """
        Read a single handle.
        """

        cmd = 'gatttool -t random -b %s --char-read -a 0x%x' % (self.addr, handle)
        res = commands.getoutput(cmd)
        res = re.match('Characteristic value/descriptor: (.*)', res).groups()[0]
        byte_values = res.split()
        return byte_values

    # higher-level interface

    def read_battery_level(self):
        "Return current battery level."

        pass


class WunderbarGattDevice(GattDevice):
    """
    A class to communicate via GATT with a Bluetooth LE Wunderbar device.

    This class uses the Bluez ``getttool`` in a non-interactive manner.
    """

    def switch_led_on(self):
        "Switch device LED on."

        pass

    def switch_led_off(self):
        "Switch device LED on."

        pass

    def read_value_named(self, name):
        "Return value with given name."

        pass

    def write_value_named(self, name, value):
        "Write value with given name."

        pass


class DeviceCallbacks(object):
    "A set of callbacks for handling device data." 

    pass
