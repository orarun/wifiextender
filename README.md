# The WiFi Extender
#### Video Demo:  https://youtu.be/_Wsqj8ZGlEI
#### Description: The WiFi Extender is a web application written in Python, HTML, Flask and Supervisor and working on the NanoPi Neo ARM.

## Overview

We, together with my family like travel abroad. And sometimes in the hotels where we rest, a WiFi signal is not so good. And I wanted to create a device which will has two WiFi adapters one of which, let's call it "External", will connect to the hotel WiFi and another adapter, let's call it "Local", provide a local WiFi network for my gadgets.

I know, there are routers and repeaters which I can use for this purposes, but they take more space and I've had the NanoPi, two WiFi adapters and I got an idea for CS50 final project )

## Structure

The structure of the project as follow

wifiextender<br>
├── app.py<br>
├── README.md<br>
├── static<br>
│   ├── bootstrap.min.css<br>
│   └── styles.css<br>
├── templates<br>
│   ├── layout.html<br>
│   ├── main.html<br>
│   └── networks.html

**app.py** - a main file of the application. For my application I import next libraries: *os*, *subprocess*, *requests*, *urllib.parse*, *ipaddress*, *re*;
*Flask*, *redirect*, *render_template*, *request*, *session*, *flash*; *Session*<br>

In main file I have the functions below:
- getMyAP() - reads local SSID from file /etc/hostapd/hostapd.conf
- stdoutParse(stdout) - parses of the output of the OS'es commands
- wifiClients() - reads OS's file which contain leased IPs /var/lib/dhcp/dhcpd.leases
- getCurrentConn() - gets a wifi network the my device is currently connected to

**README.md** - this readme file<br>

**bootstrap.min.css** - a bootstrap style file, has been taken on the [Bootswatch website] (https://bootswatch.com)<br>
**styles.css** - my file of styles, which is used for my project<br>

**layout.html** - the base html file which contains a base structure of the html pages. Here described blocks which are using in *main.html* and *networks.html* pages<br>
**main.html** - the main page of the application. There are two sections on the page, "Internet" and "Local network". In the "Internet" section there is an information about WiFi network my device is currently connected to. And two buttons "Disconnect" and "Scan". In the "Local network" section there is an information about leased IPs that OS is provided for the device's local WiFi clients.<br>
**networks.html** - the page with available networks. There are the same two sections on the page, "Internet" and "Local network". But in this time, in the "Internet" section there is a list of available WiFi networks. In the "Local network" section there is the same information about leased IPs for local clients.<br><br>

## Installation of the OS

To install an OS on the NanoPi Neo ARM board I used [this image](https://mirrors.dotsrc.org/armbian-dl/nanopineo/archive/Armbian_23.5.2_Nanopineo_jammy_current_6.1.30.img.xz)
http://wiki.friendlyarm.com/wiki/index.php/NanoPi_NEO#Get_Started.

## Configuring the OS

After OS is installed we need configure a number of packages. The WiFi Extender is a web application written in Python, HTML, Flask and Sipervisor and working on the NanoPi Neo ARM. For my project I used OS Armbian 20.11.6 Buster (old one and new is 22.04.2 LTS (Jammy Jellyfish)), Python 3.7.3, Flask 1.1.2. and Supervisor 3.3.5-1.

To configure the OS for my project I used the packages below:

- **hostapd** - is a user space software access point capable of turning normal network interface cards into access points and authentication servers.
Capabilities:
*Create an AP*;
*Create multiple APs on the same card* (if the card supports it, usually up to 8);
*Create one AP on one card and another AP on a second card,* all within a single instance of Hostapd;
*Use 2.4GHz and 5GHz at the same time on the same card.* This requires a card with two radios though, which is pretty rare (but hostapd supports it) - if the card creates two wlanX interfaces, you might be lucky;
- **wpa_supplicant** - is a cross-platform supplicant with support for WEP, WPA and WPA2 (IEEE 802.11i). It is suitable for desktops, laptops and embedded systems. It is the IEEE 802.1X/WPA component that is used in the client stations. It implements key negotiation with a WPA authenticator and it controls the roaming and IEEE 802.11 authentication/association of the wireless driver. Included with the supplicant are a GUI and a command-line utility for interacting with the running supplicant. From either of these interfaces it is possible to review a list of currently visible networks, select one of them, provide any additional security information needed to authenticate with the network (for example, a passphrase, or username and password) and add it to the preference list to enable automatic reconnection in the future. wpa_supplicant can authenticate with any of the following EAP (Extensible Authentication Protocol) methods: EAP-TLS, EAP-PEAP (both PEAPv0 and PEAPv1), EAP-TTLS, EAP-SIM, EAP-AKA, EAP-AKA', EAP-pwd, EAP-EKE, EAP-PSK (experimental), EAP-FAST, EAP-PAX, EAP-SAKE, EAP-GPSK, EAP-IKEv2, EAP-MD5, EAP-MSCHAPv2, and LEAP (requires special functions in the driver).
- **isc-dhcp-server** - is a complete open source solution for implementing DHCP servers, relay agents, and clients. ISC DHCP supports both IPv4 and IPv6, and is suitable for use in high-volume and high-reliability applications. DHCP is available for free download under the terms of the MPL 2.0 license.
- **nmcli** - is a command-line tool for controlling NetworkManager and reporting network status. It can be utilized as a replacement for nm-applet or other graphical clients. nmcli is used to create, display, edit, delete, activate, and deactivate network connections, as well as control and display network device status.
Typical uses include:
*Scripts:* Utilize NetworkManager via nmcli instead of managing network connections manually. nmcli supports a terse output format which is better suited for script processing. NetworkManager can also execute scripts, called "dispatcher scripts", in response to network events. 
*Servers*, headless machines, and terminals: nmcli can be used to control NetworkManager without a GUI, including creating, editing, starting and stopping network connections and viewing network status.
- **supervisor** - is a client/server system that allows its users to control a number of processes on UNIX-like operating systems. It was inspired by the following:<br><br>
*Convenience*. It is often inconvenient to need to write rc.d scripts for every single process instance. rc.d scripts are a great lowest-common-denominator form of process initialization/autostart/management, but they can be painful to write and maintain. Additionally, rc.d scripts cannot automatically restart a crashed process and many programs do not restart themselves properly on a crash. Supervisord starts processes as its subprocesses, and can be configured to automatically restart them on a crash. It can also automatically be configured to start processes on its own invocation.<br><br>
*Accuracy*. It’s often difficult to get accurate up/down status on processes on UNIX. Pidfiles often lie. Supervisord starts processes as subprocesses, so it always knows the true up/down status of its children and can be queried conveniently for this data.<br><br>
*Delegation*. Users who need to control process state often need only to do that. They don’t want or need full-blown shell access to the machine on which the processes are running. Processes which listen on “low” TCP ports often need to be started and restarted as the root user (a UNIX misfeature). It’s usually the case that it’s perfectly fine to allow “normal” people to stop or restart such a process, but providing them with shell access is often impractical, and providing them with root access or sudo access is often impossible. It’s also (rightly) difficult to explain to them why this problem exists. If supervisord is started as root, it is possible to allow “normal” users to control such processes without needing to explain the intricacies of the problem to them. Supervisorctl allows a very limited form of access to the machine, essentially allowing users to see process status and control supervisord-controlled subprocesses by emitting “stop”, “start”, and “restart” commands from a simple shell or web UI.<br><br>
*Process Groups*. Processes often need to be started and stopped in groups, sometimes even in a “priority order”. It’s often difficult to explain to people how to do this. Supervisor allows you to assign priorities to processes, and allows user to emit commands via the supervisorctl client like “start all”, and “restart all”, which starts them in the preassigned priority order. Additionally, processes can be grouped into “process groups” and a set of logically related processes can be stopped and started as a unit.<br><br>

## Description

In this project I use two wireless adapters, **wlan0** and **wlan1**. **wlan0** is used as WAN interface for connection the device to the Internet via available WiFi network and **wlan1** is used as WLAN interface for local clients.

To connect to the Internet via device it is also required to configure routing and firewall. To configure the device for getting Internet I used the [website](http://raspberry-at-home.com/hotspot-wifi-access-point).

To appoint wireless adapters static names based on their MAC addresses create a file /etc/udev/rules.d/70-persistent-net.rules and put here the following:
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="<put your wifi dongle wlan0 MAC address here>", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="wlan*", NAME="wlan0"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="<put your wifi dongle wlan1 MAC address here>", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="wlan*", NAME="wlan1"
(https://forum.armbian.com/topic/5167-orange-pi-zero-wifi-adapter-wlx20xxxxxxxxxx/)

For the application to start correctly, a certain daemons startup order required as, for instance, "isc-dhcp-server" daemon requires that a network interface should be already configured and started before the daemon. To the "/etc/rc.local" I added the code below:

```
systemctl stop wpa_supplicant
systemctl stop isc-dhcp-server
ifdown wlan1
ifup wlan1
systemctl start wpa_supplicant
systemctl start isc-dhcp-server
systemctl restart hostapd
```
<br>

## How the device works

First of all, to use a device it should be booted into the OS and starts my Python application. To achive this I use **supervisor** system. A simple configuration file should be as follow:

```
$ cat /etc/supervisor/conf.d/flask_app.conf

[program:flask_app]                                                                  
command = flask run -h 192.168.0.35                                      
directory = /var/www/wifiextender                            
autostart = true                                                                
autorestart = true
```

So, first I have to connect to the local WiFi network of my device and open main page of the app. There are two sections here, "Internet" and "Local network". In the "Internet" section there is an information about WiFi network my device is currently connected to, by an External WiFi adapter. And two buttons "Disconnect" and "Scan". I can disconnect from the current WiFi network and scan for available networks. In the "Local network" section there is an information about clients connected to my device and leased IPs that OS is provided for my WiFi clients. By clicking on the "Disonnect" button we disconnect the device from the current WiFi network. "Scan" button is using for scan for available WiFi networks.

To see which WiFi networks are available now I press the *Scan* button and wait for 5-10 seconds when our External adapter scans for WiFi networks. After that I will be redirected to the **networks.html** page with the available networks and be able to choose any  WiFi network and connect it. On this page I also have two sections, "Internet" and "Local network". But in this time, in the "Internet" section there is a list of available WiFi networks. In the "Local network" section there is the same information about leased IPs for local clients.<br><br>

To connect to one of the WiFi network I must input a password to "Password" field. Usually, for security, when we input a passwords they we see asterisks instead of the actual characters in our password but in my case, I consciously left a password visible as I plan to get a password from hotels staff and I do not need to hide it from someone. And also I do not need to make my application more complex, like add sections with "Show password" marks.
<br>

## Design

This app is also has a responsive design and good looks on a mobile phone as I added into **layout.html** the code below:
```
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### **Thanks**
Thank you CS50 team and personal David and Brian! You are really good teachers who can explain difficult things with simple words.
