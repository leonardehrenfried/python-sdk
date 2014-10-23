#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for accessing Relayr Wunderbar devices via Bluetooth LE.
"""

import sys
import commands

import pytest
try:
    import bluetooth
    HAVE_BLUETOOTH = True
except NotImplementedError:
    HAVE_BLUETOOTH = False


HAVE_BLUEZ = commands.getoutput('which hcitool') != ''
ON_LINUX = sys.platform.startswith("linux")


class BluetoothTestCase(object):
    "Tests using PyBluez."

    @pytest.mark.skipif(not HAVE_BLUETOOTH, reason="requires working bluetooth package")
    @pytest.mark.skipif(not ON_LINUX, reason="requires Linux")
    def test_service_discovery(self):
        "Test service (not LE!) discovery."
        try:
            # if found contains a (addr, name) tuple per device
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
        except bluetooth.btcommon.BluetoothError:
            nearby_devices = []
        assert len(devs) > 0


@pytest.mark.skipif(not ON_LINUX, reason="requires Linux")
class BleTestCase(object):
    "Tests for accessing BLE devices via Bluez tools (needs root permissions)."

    def test_ble_scan(self):
        "Test BLE service discovery (needs switched on BLE devices!)."
        from relayr.ble import scan_ble_devices
        devs = scan_ble_devices(timeout=3)
        assert len(devs) > 0

    def test_access_device(self):
        "Test accessing BLE device."
        from relayr.ble import WunderbarGattDevice
        from config import testset4 as context
        addr = context['bluetoothAddr']
        d = WunderbarGattDevice(addr)
        assert len(d.primary()) > 0
        assert len(d.characteristics()) > 0
        assert len(d.char_desc()) > 0
        assert len(d.char_read_hnd(0x0016)) > 0


if __name__ == "__main__":
    unittest.main()
