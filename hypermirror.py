#!/usr/bin/env python

import time
import osquery
import subprocess

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
        time.sleep(3)
        print "Starting Boring Hopper"
        subprocess.call(['/usr/local/bin/hyper', 'start', 'boring-hopper'])
        time.sleep(3)
        print "Starting sshd"
        subprocess.call(['/usr/local/bin/hyper', 'exec', '-d', 'boring-hopper', '/usr/sbin/sshd'])
        time.sleep(3)
        print "Attaching FIP"
        subprocess.call(['/usr/local/bin/hyper', 'fip', 'attach', 'access', 'boring-hopper'])
    else:
        print "no Yubikey device is plugged in"
        print "detaching FIP"
        time.sleep(3)
        subprocess.call(['/usr/local/bin/hyper', 'fip', 'detach', 'boring-hopper'])
        time.sleep(3)
        print "Stopping Boring Hopper"
        subprocess.call(['/usr/local/bin/hyper', 'stop', 'boring-hopper'])
