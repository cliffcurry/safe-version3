#!/bin/sh
# showIPandMAC.sh
 
IP=$(ip addr show wlan0 | awk '/inet / {print $2}' | cut -d/ -f 1)
MAC=$(ip link show wlan0 | awk '/ether/ {print $2}')
 
echo "IP Address: $IP"
echo "MAC Address: $MAC"
 
# EndOfFile