#!/usr/bin/env python
""" This script starts a hyper.sh container on Yubikey
   insertion and stops it on removal """

import sys
import time
import subprocess
import osquery

def search():
    """This function searches for a Yubico device"""
    # Spawn an osquery process using an ephemeral extension socket.
    instance = osquery.SpawnInstance()
    instance.open()  # This may raise an exception

    # Issues queries and call osquery Thrift APIs.
    usb_devices = instance.client.query("select * from usb_devices;")

    # search for a Yubikey
    for device in usb_devices.response:
        for usb_attributes in device:
            if usb_devices.response[usb_devices.response.index(device)]['vendor'] == "Yubico" and usb_devices.response[usb_devices.response.index(device)]['model'] == "Yubikey NEO OTP+U2F+CCID":
                return True
    return False

class Printer():
    """
    Print things to stdout on one line dynamically
    """
    def __init__(self, data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

def container_running():
    """This function checks is a hyper container is running"""
    state = subprocess.check_output(['/usr/local/bin/hyper', 'ps', '-f', 'status=running', '-f', 'name=boring-hopper', '-q']).strip()
    return bool(state == "f2f225c16c75")

if __name__ == "__main__":
    while True:
        cont_status = container_running()
        usb_status = search()
        screen_output =  "Container running : %s Yubikey inserted : %s" % (cont_status, usb_status)
        Printer(screen_output)
        time.sleep(5)
        if cont_status == False and usb_status == True:
            time.sleep(3)
            print "Starting Boring Hopper"
            subprocess.call(['/usr/local/bin/hyper', 'start', 'boring-hopper'])
            time.sleep(3)
            print "Starting sshd"
            subprocess.call(['/usr/local/bin/hyper', 'exec', '-d', 'boring-hopper', '/usr/sbin/sshd'])
            time.sleep(3)
            print "Attaching FIP"
            subprocess.call(['/usr/local/bin/hyper', 'fip', 'attach', 'access', 'boring-hopper'])
        elif usb_status == False and cont_status == True:
            print "detaching FIP"
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'fip', 'detach', 'boring-hopper'])
            time.sleep(3)
            print "Stopping Boring Hopper"
            subprocess.call(['/usr/local/bin/hyper', 'stop', 'boring-hopper'])
