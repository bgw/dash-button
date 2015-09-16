#!/bin/sh
# Steps to setup:
# $ uci set dhcp.@dnsmasq[0].dhcpscript='/etc/config/dash-button'
# $ uci commit
# $ /etc/init.d/dnsmasq restart

mode="$1" # "add", "del", or "old"
mac="$2"
ip="$3"
host="$4"
wget -O - "http://pipeep-laptop.lan:8001/dash?mode=$mode&mac=$mac&ip=$ip&host=$host" >/dev/null 2>&1 &
