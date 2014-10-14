#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scan Wunderbar devices and show what we find about them.

Todo:

- add command-line args to make this more flexible

Example:

$ python scan_wunderbars.py
Discovered device: F1:42:E6:63:20:A2 WunderbarMIC 
  characteristic uuid: 00002a00-0000-1000-8000-00805f9b34fb
    name handle: 0x0002, data: 02 03 00 00 2a , str: '\x02\x03\x00\x00*'
    name handle: 0x0003, data: 57 75 6e 64 65 72 62 61 72 4d 49 43 , str: 'WunderbarMIC'
  characteristic uuid: 00002a01-0000-1000-8000-00805f9b34fb
    name handle: 0x0004, data: 02 05 00 01 2a , str: '\x02\x05\x00\x01*'
    name handle: 0x0005, data: 00 02 , str: '\x00\x02'
  characteristic uuid: 00002a04-0000-1000-8000-00805f9b34fb
    name handle: 0x0006, data: 02 07 00 04 2a , str: '\x02\x07\x00\x04*'
    name handle: 0x0007, data: b0 00 b0 00 05 00 2c 01 , str: '\xb0\x00\xb0\x00\x05\x00,\x01'
  characteristic uuid: 00002a05-0000-1000-8000-00805f9b34fb
    name handle: 0x0009, data: 20 0a 00 05 2a , str: ' \n\x00\x05*'
    name handle: 0x000a, data: None, str: None
  characteristic uuid: 00002010-0000-1000-8000-00805f9b34fb
    name handle: 0x000d, data: 02 0e 00 10 20 , str: '\x02\x0e\x00\x10 '
    name handle: 0x000e, data: None, str: None
  characteristic uuid: 00002011-0000-1000-8000-00805f9b34fb
    name handle: 0x0010, data: 0a 11 00 11 20 , str: '\n\x11\x00\x11 '
    name handle: 0x0011, data: None, str: None
  characteristic uuid: 00002012-0000-1000-8000-00805f9b34fb
    name handle: 0x0013, data: 0a 14 00 12 20 , str: '\n\x14\x00\x12 '
    name handle: 0x0014, data: None, str: None
  characteristic uuid: 00002013-0000-1000-8000-00805f9b34fb
    name handle: 0x0016, data: 08 17 00 13 20 , str: '\x08\x17\x00\x13 '
    name handle: 0x0017, data: None, str: None
  characteristic uuid: 00002014-0000-1000-8000-00805f9b34fb
    name handle: 0x0019, data: 0a 1a 00 14 20 , str: '\n\x1a\x00\x14 '
    name handle: 0x001a, data: None, str: None
  characteristic uuid: 00002016-0000-1000-8000-00805f9b34fb
    name handle: 0x001c, data: 32 1d 00 16 20 , str: '2\x1d\x00\x16 '
    name handle: 0x001d, data: None, str: None
  characteristic uuid: 00002a29-0000-1000-8000-00805f9b34fb
    name handle: 0x0021, data: 02 22 00 29 2a , str: '\x02"\x00)*'
    name handle: 0x0022, data: 52 65 6c 61 79 72 , str: 'Relayr'
  characteristic uuid: 00002a27-0000-1000-8000-00805f9b34fb
    name handle: 0x0023, data: 02 24 00 27 2a , str: "\x02$\x00'*"
    name handle: 0x0024, data: 31 2e 30 2e 32 , str: '1.0.2'
  characteristic uuid: 00002a26-0000-1000-8000-00805f9b34fb
    name handle: 0x0025, data: 02 26 00 26 2a , str: '\x02&\x00&*'
    name handle: 0x0026, data: 31 2e 30 2e 30 , str: '1.0.0'
  characteristic uuid: 00002a19-0000-1000-8000-00805f9b34fb
    name handle: 0x0028, data: 12 29 00 19 2a , str: '\x12)\x00\x19*'
    name handle: 0x0029, data: 64 , str: 'd'
  device name: WunderbarMIC
  battery level: 100
...
"""


from relayr.ble import scan_ble_devices, GattDevice, data2str


def scan_wunderbars():
    """
    Scan Wunderbar devices and show what we find about them.
    """
    
    devices = scan_ble_devices(name_filter='Wunderbar.*')
    for dev in devices:
        print("Discovered device: %(addr)s %(name)s " % dev)
        d = GattDevice(dev['addr'])
        chars = d.characteristics()
        for char in chars:
            if len(char['_uuid']) == 4:
                print('  characteristic uuid: %s' % char['uuid'])
                h = char['name_handle']
                dat = d.char_read_hnd(h)
                print('    name handle: %s, data: %s, str: %s' % (h, dat, repr(data2str(dat))))
                h = char['value_handle']
                dat = d.char_read_hnd(h)
                print('    name handle: %s, data: %s, str: %s' % (h, dat, repr(data2str(dat))))
        print('  device name: %s' % d.read_device_name())
        print('  battery level: %s' % d.read_battery_level())
        print('')


if __name__ == "__main__":
    scan_wunderbars()
