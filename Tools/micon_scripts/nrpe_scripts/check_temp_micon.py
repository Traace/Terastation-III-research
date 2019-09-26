#!/usr/bin/python3

# Nagios NRPE Temp Check for micon controllers
# Used in various Buffalo NAS products etc.

# Based on micon_fan_daemon.py by 1000001101000
# https://github.com/1000001101000
# Modified for nrpe usage by Traace
# https://github.com/Traace

import libmicon
import subprocess
import time
import sys
import configparser
import os

# Define quits for nagios Status Messages
OK=int(0)
WARNING=int(1)
CRITICAL=int(2)
UNKNOWN=int(3)

config_file="/etc/micon_fan.conf"

config = configparser.ConfigParser()
if os.path.exists(config_file):
	config.read(config_file)
else:
	config['Rackmount'] = {'MediumTempC': '40', 'HighTempC': '50', 'ShutdownTempC': '65'}
	config['Desktop'] = {'MediumTempC': '25', 'HighTempC': '35', 'ShutdownTempC': '65'}
	with open(config_file, 'w') as configfile:
		config.write(configfile)

if len(sys.argv) > 1:
	debug=str(sys.argv[1])
else:
	debug=""

##try reading micon version from each port to determine the right one
for port in ["/dev/ttyS1","/dev/ttyS3"]:
	test = libmicon.micon_api(port)
	version = test.send_read_cmd(0x83)
	test.port.close()
	if version:
		break

version=version.decode('utf-8')

if ((version.find("TS-RXL") != -1) or (version.find("TS-MR") != -1) or (version.find("1400R") != -1)):
	med_temp=int(config['Rackmount']['MediumTempC'])
	high_temp=int(config['Rackmount']['HighTempC'])
	shutdown_temp=int(config['Rackmount']['ShutdownTempC'])
else:
	med_temp=int(config['Desktop']['MediumTempC'])
	high_temp=int(config['Desktop']['HighTempC'])
	shutdown_temp=int(config['Desktop']['ShutdownTempC'])

if debug == "debug":
	print("Terastation Version: ",version," Medium Temp: ",med_temp,"C"," High Temp: ",high_temp,"C")

# Check Fan Speed and Temp, give outputs based on results.
# Highes rule must be first, code runs from top to bottom , even within "level 5" languages :)
test = libmicon.micon_api(port)
micon_temp=int.from_bytes(test.send_read_cmd(0x37),byteorder='big')
current_speed=int.from_bytes(test.send_read_cmd(0x33),byteorder='big')
if debug == "debug":
	print("Status: Debug  Fan Speed:",current_speed," Temperature:",micon_temp,"C")
if micon_temp >= high_temp:
	print("Status: Critical  Fan Speed:",current_speed," Temperature:",micon_temp,"C")
	if debug == "debug":
		print(CRITICAL)
	test.port.close()
	quit(CRITICAL)
if micon_temp >= med_temp:
	print("Status: Warning  Fan Speed:",current_speed," Temperature:",micon_temp,"C")
	if debug == "debug":
		print(WARNING)
	test.port.close()
	quit(WARNING)
if micon_temp < med_temp:
	print("Status: OK  Fan Speed:",current_speed," Temperature:",micon_temp,"C")
	if debug == "debug":
		print(OK)
	test.port.close()
	quit(OK)
else :
	if debug == "debug":
		print(UNKNOWN)
		print("ELSE MESSAGE")
	quit(UNKNOWN)
