#!/usr/bin/python

import re
import json
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
	'disks': {}
}

# disks
proc_fdisk = subprocess.Popen(['fdisk', '-l'], stdout=subprocess.PIPE)
for fdisk_line in proc_fdisk.stdout:
	fdisk_line = fdisk_line.rstrip()
	fdisk_sek = re.search('^Disk /dev/(sd.*?): (.*?),', fdisk_line)
	if fdisk_sek:
		# basic information
		disk = {}
		disk['name'] = fdisk_sek.group(1)
		disk['capacity'] = fdisk_sek.group(2)

		# SMART
		proc_smart = subprocess.Popen(['smartctl', '-a', '/dev/' + disk['name']], stdout=subprocess.PIPE)
		disk['smart'] = {}

		for smart_line in proc_smart.stdout:
			# check for all parameters
			for param in smart_params:
				smart_sek = re.search(param['re'], smart_line)
				if smart_sek:
					disk['smart'][param['name']] = smart_sek.group(1)

		# save into data
		data['disks'][disk['name']] = disk

# print output
print json.dumps(data, sort_keys=True, indent=4)
