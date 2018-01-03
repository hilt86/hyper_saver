#!/usr/bin/env python
""" This script starts a hyper.sh container on Yubikey
    insertion and stops it on removal - tested on OSX """

import os
import sys
import time
import subprocess
import osquery

FNULL = open(os.devnull, 'w')
CONTAINER_NAME = sys.argv[1]
FIP_NAME = sys.argv[2]

# Spawn an osquery process using an ephemeral extension socket.
instance = osquery.SpawnInstance()
instance.open()  # This may raise an exception


def search():
    # Issues queries and call osquery Thrift APIs.
    usb_devices = instance.client.query("select * from usb_devices;")

    # search for a Yubikey
    for device in usb_devices.response:
        for usb_attributes in device:
            if usb_devices.response[usb_devices.response.index(device)]['vendor'] == "Yubico" and usb_devices.response[usb_devices.response.index(device)]['model'] == "Yubikey NEO OTP+U2F+CCID":
                return True
    return False

class Printer():
    """ Print things to stdout on one line dynamically """
    def __init__(self, data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

def check_container_running():
    """ This function checks is a hyper container is running """
    state = subprocess.check_output(['/usr/local/bin/hyper', 'ps', '-f', 'status=running', '-f', 'name=boring-hopper', '--format', '{{ .Names }}']).strip()
    return bool(state == "boring-hopper")

if __name__ == "__main__":
    while True:
        container_running = check_container_running()
        yubikey_present = search()

        """ set and print status """
        if container_running == True: cont_disp_status = "running"
        else: cont_disp_status = "stopped"
        if yubikey_present == True: usb_disp_status = "inserted"
        else: usb_disp_status = "absent"
        screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
        Printer(screen_output)
        time.sleep(5)

        if not container_running and yubikey_present:
            time.sleep(3)
            cont_disp_status = "starting"
            screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
            Printer(screen_output)
            subprocess.call(['/usr/local/bin/hyper', 'start', CONTAINER_NAME], stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'exec', '-d', CONTAINER_NAME, '/usr/sbin/sshd'], stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'fip', 'attach', FIP_NAME, CONTAINER_NAME], stdout=FNULL, stderr=subprocess.STDOUT)
        elif not yubikey_present and container_running: 
            cont_disp_status = "stopping"
            screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
            Printer(screen_output)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'fip', 'detach', CONTAINER_NAME], stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(3)
            subprocess.call(['/usr/local/bin/hyper', 'stop', CONTAINER_NAME], stdout=FNULL, stderr=subprocess.STDOUT)
