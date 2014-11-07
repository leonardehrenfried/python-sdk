#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for accessing Relayr Wunderbar devices via Bluetooth LE.

Some of these test need root permissions, see docstrings below.
"""

import sys
import subprocess

import pytest
try:
    import bluetooth
    HAVE_BLUETOOTH = True
except NotImplementedError:
    HAVE_BLUETOOTH = False


ON_LINUX = sys.platform.startswith("linux")
HAVE_BLUEZ = subprocess.Popen(['which', 'hcitool']).stdout != ''

@pytest.mark.skipif(not HAVE_BLUETOOTH, reason="requires working bluetooth package")
@pytest.mark.skipif(not ON_LINUX, reason="requires Linux")
class TestBluetooth(object):
    "Tests using PyBluez."

    def test_service_discovery(self):
        "Test service (not LE!) discovery."
        try:
            # if found contains a (addr, name) tuple per device
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
        except bluetooth.btcommon.BluetoothError:
            nearby_devices = []
        assert len(devs) > 0


@pytest.mark.skipif(not ON_LINUX, reason="requires Linux")
class TestBle(object):
    "Tests for accessing BLE devices via Bluez tools (needs root permissions)."

    def test_ble_scan(self):
        "Test BLE service discovery (needs switched on BLE devices!)."
        from relayr.ble import scan_ble_devices
        devs = scan_ble_devices(timeout=3)
        assert len(devs) > 0

    def test_access_device(self, fix_registered):
        "Test accessing BLE device."
        from relayr.ble import WunderbarGattDevice
        addr = fix_registered.testset4['bluetoothAddr']
        d = WunderbarGattDevice(addr)
        assert len(d.primary()) > 0
        assert len(d.characteristics()) > 0
        assert len(d.char_desc()) > 0
        assert len(d.char_read_hnd(0x0016)) > 0
