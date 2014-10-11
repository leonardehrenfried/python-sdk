#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for accessing Relayr Wunderbar devices via Bluetooth LE.
"""

import sys
import commands
import unittest

try:
    import bluetooth
    HAVE_BLUETOOTH = True
except NotImplementedError:
    HAVE_BLUETOOTH = False

from relayr import ble


HAVE_BLUEZ = commands.getoutput('which hcitool') != ''


class BluetoothTestCase(unittest.TestCase):
    "Tests using PyBluez."

    @unittest.skipUnless(HAVE_BLUETOOTH, "requires working bluetooth package")
    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_service_discovery(self):
        """
        Test service discovery.
        """

        # perform a simple device discovery (not LE!) followed by a remote 
        # name request of each discovered device

        try:
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
        except bluetooth.btcommon.BluetoothError:
            nearby_devices = []
        
        if nearby_devices:
            print("Found %d Bluetooth devices." % len(nearby_devices))
            for addr, name in nearby_devices:
                print("  %s - %s" % (addr, name))


class BleTestCase(unittest.TestCase):
    "Tests for accessing BLE devices via Bluez tools (needs root permissions)."

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_ble_scan(self):
        """
        Test BLE service discovery (needs switched on BLE devices!).
        """
        devs = scan_ble_devices(timeout=3)
        self.assertTrue(len(devs) > 0


    def test_access_device(self):
        """
        Test accessing BLE device.
        """
        from config import testset4 as context
        addr = context['bluetoothAddr']
        d = ble.SimpleBleDeviceWunderbar(addr)

        prim = d.primary()
        self.assertTrue(len(prim) > 0)

        chars = d.characteristics()
        self.assertTrue(len(chars) > 0)

        char_desc = d.char_desc()
        self.assertTrue(len(char_desc) > 0)

        data = d.char_read_hnd(0x0016)
        self.assertTrue(len(data) > 0)


if __name__ == "__main__":
    unittest.main()
