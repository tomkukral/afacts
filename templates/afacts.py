#!/usr/bin/env python2

import re
import json
import datetime
import subprocess

# define smart parameters to read
smart_params = [
    {'name': 'serial', 're': '^Serial Number:[\s]*(.*)'},
    {'name': 'model', 're': '^Device Model:[\s]*(.*)'},
    {'name': 'firmware', 're': '^Firmware Version:[\s]*(.*)'},
    {'name': 'rpm', 're': '^Rotation Rate:[\s]*(.*)'}
]

# init output data
data = {
    'disks': {},
    'ipmi': {},
    'timestamp': datetime.datetime.utcnow().isoformat(),
    'errors': {}
}

# disks
try:
    fdisk_proc = subprocess.Popen(['fdisk', '-l'], stdout=subprocess.PIPE)
except OSError as e:
    fdisk_proc = False
    data['errors']['disks'] = str(e)

if fdisk_proc:
    for fdisk_line in fdisk_proc.stdout:
        fdisk_line = fdisk_line.rstrip()
        fdisk_sek = re.search('^Disk /dev/(sd.*?): (.*?),', fdisk_line)
        if fdisk_sek:
            # basic information
            disk = {}
            disk['name'] = fdisk_sek.group(1)
            disk['capacity'] = fdisk_sek.group(2)

            # SMART
            smart_proc = subprocess.Popen(['smartctl', '-a', '/dev/' + disk['name']], stdout=subprocess.PIPE)
            disk['smart'] = {}

            for smart_line in smart_proc.stdout:
                # check for all parameters
                for param in smart_params:
                    smart_sek = re.search(param['re'], smart_line)
                    if smart_sek:
                        disk['smart'][param['name']] = smart_sek.group(1)

            # save into data
            data['disks'][disk['name']] = disk

# ipmitool
try:
    ipmi_proc = subprocess.Popen(['ipmitool', 'fru'], stdout=subprocess.PIPE)
except OSError as e:
    ipmi_proc = False
    data['errors']['ipmi'] = str(e)

if ipmi_proc:
    for ipmi_line in ipmi_proc.stdout:
        ipmi_line = ipmi_line.rstrip()
        ipmi_sek = re.search('[\s]*(.*?)[\s]*:[\s]*(.*)[\s]*', ipmi_line)
        if ipmi_sek:
            data['ipmi'][ipmi_sek.group(1)] = ipmi_sek.group(2)

# print output
print(json.dumps(data))
