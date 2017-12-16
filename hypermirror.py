#!/usr/bin/env python

import osquery

def search():

    # Spawn an osquery process using an ephemeral extension socket.
    instance = osquery.SpawnInstance()
    instance.open()  # This may raise an exception

    # Issues queries and call osquery Thrift APIs.
    usbDevices = instance.client.query("select * from usb_devices;")

    # search for a Yubikey
    for device in usbDevices.response:
        for usbAttr in device:
            if usbDevices.response[usbDevices.response.index(device)]['vendor'] == "Yubico":
                return True 

if __name__ == "__main__":
    if search():
        print "a Yubikey is plugged in"
    else:
        print "no Yubikey device is plugged in"
