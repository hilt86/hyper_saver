#!/usr/bin/env python
""" This script starts a hyper.sh container on Yubikey
   insertion and stops it on removal """

import os
import sys
import time
import subprocess
import osquery

FNULL = open(os.devnull, 'w')

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
        if cont_status == True: cont_disp_status = "running"
        else: cont_disp_status = "stopped"
        if usb_status == True: usb_disp_status = "inserted"
        else: usb_disp_status = "absent"
        screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
        Printer(screen_output)
        time.sleep(5)
        if cont_status == False and usb_status == True:
            time.sleep(3)
            cont_disp_status = "starting"
            screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
            Printer(screen_output)
            subprocess.call(['/usr/local/bin/hyper', 'start', 'boring-hopper'], stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'exec', '-d', 'boring-hopper', '/usr/sbin/sshd'], stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'fip', 'attach', 'access', 'boring-hopper'], stdout=FNULL, stderr=subprocess.STDOUT)
        elif usb_status == False and cont_status == True:
            cont_disp_status = "stopping"
            screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
            Printer(screen_output)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'fip', 'detach', 'boring-hopper'], stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'stop', 'boring-hopper'], stdout=FNULL, stderr=subprocess.STDOUT)
