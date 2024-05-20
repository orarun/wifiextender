#!/bin/bash
sleep 3
/usr/bin/systemctl stop wpa_supplicant
/usr/bin/systemctl stop isc-dhcp-server
ifdown wlan0
ifup wlan0
sleep 2
/usr/bin/systemctl start wpa_supplicant
sleep 2
/usr/bin/systemctl start isc-dhcp-server
/usr/bin/systemctl restart hostapd

#env >>/tmp/test.log
#file "/sys${DEVPATH}" >>/tmp/test.log

#if [ "${ACTION}" = add -a -d "/sys${DEVPATH}" ]; then
#echo "add ${DEVPATH}" >>/tmp/test.log
#fi
