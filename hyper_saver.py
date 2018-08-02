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
# This may raise an exception
instance.open()


def search_for_yubico_usb():
    """
    Searches USB devices list for devices made by Yubico &
    Returns true if a device made by Yubico is present
    """
    # Issues queries and call osquery Thrift APIs.
    usb_devices = instance.client.query("select * from usb_devices;")

    # search for a Yubikey
    for device in usb_devices.response:
        for usb_attributes in device:
            if usb_devices.response[usb_devices.response.index(device)]['vendor'] == "Yubico":
                return True
    return False

class Printer():
    """ Print things to stdout on one line dynamically """
    def __init__(self, data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

def check_container_running(container):
    """ This function checks if a hyper container is running """
    state = subprocess.check_output(['/usr/local/bin/hyper', 'ps', '-f', 'status=running', '-f', 'name=' + container, '--format', '{{ .Names }}']).strip()
    return bool(state == container)

def get_container_id_from_name(container):
    """ returns containerId if running """
    containerId = subprocess.check_output(['/usr/local/bin/hyper', 'ps', '-f', 'name=' + container, '--format', '{{ .ID }}']).strip()
    return containerId

def check_fip_attached(fip, container):
    """ checks that given fip is attached to given container """

def start_container(container):
    """ starts container """
    try:
        subprocess.call(['/usr/local/bin/hyper', 'start', container], stdout=FNULL, stderr=subprocess.STDOUT)
    except IOError:
        print(" I/O error ")

def stop_container(container):
    """ stops container """
    try:
        subprocess.call(['/usr/local/bin/hyper', 'stop', container], stdout=FNULL, stderr=subprocess.STDOUT)
    except IOError:
        print(" I/O error ")

def start_sshd(container):
    """ starts sshd in container """
    try:
        subprocess.call(['/usr/local/bin/hyper', 'exec', '-d', container, '/usr/sbin/sshd'], stdout=FNULL, stderr=subprocess.STDOUT)
    except IOError:
        print(" I/O error ")

def attach_fip(fip, container):
    """ attaches fip to container """
    try:
        subprocess.call(['/usr/local/bin/hyper', 'fip', 'attach', fip, container], stdout=FNULL, stderr=subprocess.STDOUT)
    except IOError:
        print(" I/O error ")

def detach_fip(container):
    """ detaches fip from container """
    try:
        subprocess.call(['/usr/local/bin/hyper', 'fip', 'detach', container], stdout=FNULL, stderr=subprocess.STDOUT)
    except IOError:
        print(" I/O error ")


if __name__ == "__main__":
    while True:
        try:
            container_running = check_container_running(CONTAINER_NAME)
        except subprocess.CalledProcessError:
            print(" I/O error ")
        yubikey_present = search_for_yubico_usb()

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
            start_container(CONTAINER_NAME)
            time.sleep(3)
            start_sshd(CONTAINER_NAME)
        elif not yubikey_present and container_running: 
            cont_disp_status = "stopping"
            screen_output =  "Container : %s ||| Yubikey : %s" % (cont_disp_status, usb_disp_status)
            Printer(screen_output)
            time.sleep(3)
            stop_container(CONTAINER_NAME)
