# -*- coding: utf-8 -*-

"""
Functionality for working with Bluetooth, especially LE (Low Energy).

Since PyBluez doesn't support Bluetooth LE yet this module provides an
abstraction on the tools ``hcitool`` and ``gatttool``.

This module needs to be run with root permisions.

Example:

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
import shlex
import subprocess

import pexpect


# Device information service
Device_Name_UUID = '2a00'
Manufacturer_Name_UUID = '2a29'
Firmware_Revision_UUID = '2a26'
Hardware_Revision_UUID = '2a27'
# Battery service
Battery_Level_UUID = '2a19'


def data2str(data):
    """
    Convert some data to a string.

    An empty or None value is returned unchanged (helpful for testing), e.g.:

    '57 75 6e 64 65 72 62 61 72 49 52' -> 'WunderbarIR'
    '' -> ''
    """
    if not data: return data
    text = ''.join([chr(int(v, 16)) for v in data.split()])
    return text


def str2data(str):
    """
    Convert a string to some data bytes.

    An empty or None value is returned unchanged (helpful for testing), e.g.:

    'WunderbarIR' -> '57 75 6e 64 65 72 62 61 72 49 52'
    '' -> ''
    """
    if not str: return str
    data = ' '.join([hex(ord(c))[2:] for c in str])
    return data


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
    
    def __init__(self, addr):
        """
        Instantiate an object representing a device accessible via GATT.

        :param addr: the MAC address of the device
        :type addr: string
        """

        self.addr = addr
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
        cmd = 'gatttool -t random -b %s --primary' % self.addr
        res = subprocess.check_output(shlex.split(cmd))
        lines = re.split('\r?\n', res)
        lines = sorted(set(lines))
        self.data['services'] = lines
        return lines

    def characteristics(self, uuid=None):
        """
        Read list of characteristics.

        If the ``uuid`` parameter is given, only this characteristic will be read.

        :param uuid: uuid to be read
        :type uuid: string
        """

        # example line format:
        # 'handle = 0x0002, char properties = 0x02, char value handle = 0x0003, uuid = 00002a00-0000-1000-8000-00805f9b34fb'
        cmd = 'gatttool -t random -b %s --characteristics' % self.addr
        if uuid:
            cmd += ' --uuid=%s' % uuid
        res = subprocess.check_output(shlex.split(cmd))
        lines = re.split('\r?\n', res)
        pat = '^handle\s*=\s*(?P<name_handle>0x[0-9a-fA-F]{4}),\s*char\s*properties\s*=\s*(?P<properties>0x[0-9a-fA-F]+),\s*char\s*value\s*handle\s*=\s*(?P<value_handle>0x[0-9a-fA-F]{4}),\s*uuid\s*=\s*(?P<uuid>[0-9a-fA-F\-]+)'
        lines = [re.match(pat, line).groupdict() for line in lines]
        for line in lines:
            short = line['uuid'].split('-')[0]
            while short[0] == '0': short = short[1:]
            line['_uuid'] = short
        self.data['characteristics'] = lines
        return lines

    def char_desc(self):
        """
        Read list of characteristic descriptors.
        """

        # example line format:
        # 'handle = 0x000e, uuid = 00002010-0000-1000-8000-00805f9b34fb'
        cmd = 'gatttool -t random -b %s --char-desc' % self.addr
        res = subprocess.check_output(shlex.split(cmd))
        lines = re.split('\r?\n', res)
        # lines = re.findall('handle: .* uuid: [0-9a-f\-]{36}', res)
        self.data['char-desc'] = lines
        return lines

    def char_read_hnd(self, handle):
        """
        Read a data string representing the value of a handle.

        Return None if the handle cannot be read, e.g. because it is invalid.

        :param handle: uuid to be read, e.g. '0x0017'
        :type handle: string
        """

        cmd = 'gatttool -t random -b %s --char-read --handle %s' % (self.addr, handle)
        res = subprocess.check_output(shlex.split(cmd))
        if not res.startswith('Characteristic value/descriptor:'):
            return None
        res = re.match('Characteristic value/descriptor: (.*)', res).groups()[0]
        byte_values = res # .split()
        return byte_values

    # higher-level interface

    def read_device_name(self):
        "Return device name."

        for char in self.data['characteristics']:
            if char['_uuid'] == Device_Name_UUID:
                value_handle = char['value_handle']
        data = self.char_read_hnd(value_handle) # eg. '57 75 6e 64 65 72 62 61 72 49 52'
        name = ''.join([chr(int(v, 16)) for v in data.split()]) # e.g. 'WunderbarIR'
        return name

    def read_battery_level(self):
        "Return current battery level."

        value_handle = None
        for char in self.data['characteristics']:
            if char['_uuid'] == Battery_Level_UUID:
                value_handle = char['value_handle']
        if not value_handle:
            return None
        data = self.char_read_hnd(value_handle) # eg. '64'
        level = int(data, 16) # e.g. 100
        return level


class WunderbarGattDevice(GattDevice):
    """
    A class to communicate via GATT with a Bluetooth LE Wunderbar device.

    This class uses the Bluez ``getttool`` in a non-interactive manner.
    """

    def switch_led_on(self):
        "Switch device LED on."

        pass

    def switch_led_off(self):
        "Switch device LED off."

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
