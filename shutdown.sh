#!/bin/bash

PIN="203"

echo $PIN > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio$PIN/direction

while true
  do
    value=`cat /sys/class/gpio/gpio$PIN/value`
    if [[ $value == "0" ]]
    then
      shutdown -h 0
    fi
    sleep 0.5
  done