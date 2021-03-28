#import wifi
# WLAN0 and WLAN1 are hardcoded to WAN and LAN accordingly
import os, subprocess, requests, urllib.parse, ipaddress, re
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def getMyAP():
	# reading local SSID from a config file /etc/hostapd/hostapd.conf
	with open('/etc/hostapd/hostapd.conf', 'r') as file:
		for line in file:
			if line[:5] == "ssid=":
				return line[5:-1]

# Variable which contain of a name of the device's Access Point (Local WiFi network)
myap = getMyAP()


@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "GET":

		# Set wan_connection_successfull cookie to False
		session["wan_connection_successfull"] = False

		# Client connected to the device
		clients = wifiClients()

		# Get a wifi network the device is currently connected to
		currentConn = getCurrentConn()

		return render_template("main.html", clients=clients, myap=myap, currentconn=currentConn)
		
	else:
		# If "Disconnect" button has been pressed then the device disconnects from current wifi and purge all saved wifi networks
		button = request.form['button']

		# If "Scan" button has been pressed then we redirect to the /networks route
		if button == "Scan":
			return redirect("/networks")

		# Get an output of the "nmcli" command
		try:
			disconnect = subprocess.check_output("nmcli --fields NAME -t connection show | grep -v Wired | xargs -I «{}» nmcli connection delete «{}»", shell=True)
		except subprocess.CalledProcessError as disconnectexc:
			return redirect("/")
		else:

			# Set wan_disconnection_successfull cookie to True to show a flash message on the page
			flash('Successfully disconnected!')
			session["wan_disconnection_successfull"] = True

		return redirect("/")


@app.route("/networks", methods=["GET", "POST"])
def networks():
	if request.method == "GET":

		# List of available wifi networks
		outputList = None
		error = False

		# Get an output of the "nmcli" command
		try:
			output = subprocess.check_output("nmcli -t -f SSID,CHAN,RATE,SIGNAL,IN-USE dev wifi", shell=True)
		except:
			error = True
		else:
			# Delete last empty string of the output as it is just a new line
			output = output[:-1]

			# Parse output to get a list of wifi networks
			outputList = stdoutParse(output)

		### Sample of output list of WiFi networks
		### [['YourAPSSID', '1', '65 Mbit/s', '100', ' '], ['Space3', '3', '130 Mbit/s', '100', ' '], ['Space2', '6', '130 Mbit/s', '75', '*'],['Tolik', '8', '270 Mbit/s', '42', ' ']]

			# Store output_list to cookie to send it to the "network" page
			session["output_list"] = outputList


		# wan, lan, statusList = getNetworkInterfaces()
		clients = wifiClients()
		currentConn = getCurrentConn()

		return render_template("networks.html", myap=myap, currentConn=currentConn, error=error, outputList=outputList, clients = wifiClients())

	else:
		# If "Rescan" button has been pressed then rescan wifi networks
		button = request.form['button']
		if button == "Rescan":
			return redirect("/networks")
		else:
			# Else we assume that we get a password. So, try to connect to the wifi network with the given passowrd
			passwd = request.form.get("passwd")
			if passwd != '':
				connect = None
				error = False

				# Get an output of the "nmcli" command
				try:
					connect = subprocess.check_output('nmcli dev wifi connect ' + session["output_list"][int(button)-1][0] + ' password ' + passwd, text=True, shell=True)
				except:
					error = True
				else:
					connect = connect[:-1]
				if connect.find('successfully') != -1:

					# Set wan_connection_successfull cookie to True to show a flash message on the page
					flash('Successfully connected!')
					session["wan_connection_successfull"] = True
					return redirect("/")
				else:
					flash('Connection error!')
					return redirect("/networks")
			else:
				flash('You must provide a password!')
			
			return redirect("/networks")


def stdoutParse(stdout):
# Parse of the scan output 
	outputList = []
	string = ''
	for n in stdout:
		if n != 10:	# End of line
			string += chr(n)
		else:
			# Delimeter of the items is ":"
			s = string.split(":")
			outputList.append(s)
			string = ''
	return outputList


# def getNetworkInterfaces():
# 	# Get network interfaces of the device
# 	interfaces = subprocess.check_output("ls /sys/class/net/", text=True, shell=True)
# 	interfaces = interfaces[:-1]

# 	status = subprocess.check_output('nmcli -t dev status', shell=True)

# 	# Delete last empty string of the output
# 	status = status[:-1]

# 	statusList = stdoutParse(status)

# 	if (interfaces.find('wlan0') != -1):
# 		wan = "Internet: wlan0"
# 	else:
# 		wan = "Internet: Interface not found"
# 	if (interfaces.find('wlan1') != -1):
# 		lan = "Local: wlan1"
# 	else:
# 		lan = "Local: Interface not found"

# 	return (wan, lan, statusList)

def wifiClients():
	dhcpLeases = []
	# reading file with leased IPs /var/lib/dhcp/dhcpd.leases
	with open('/var/lib/dhcp/dhcpd.leases', 'r') as file:
		# decalring the regex pattern for IP addresses 
		pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
		idx = -1

		# Sometimes, there is no hostname parameter among leased IPs in the dhcpd.leases file
		# Initial parameter of availability of client's hostname in the output
		clientHostname = False

		for line in file:
			# finding IP by pattern
			ip = pattern.search(line)

			# Get IP
			if ip is not None:
				ip = ip.group()

			# If we found something matches given pattern and it's a real IP address save IP to the list
			if (ip is not None) and ipaddress.ip_address(ip):

				# If we didn't find client's hostname save "none" to the list
				if (idx != -1) and (not clientHostname):
					dhcpLeases[idx].append("none")
				
				# Iterate index
				idx += 1

				# Set clientHostname to initial state
				clientHostname = False

				# Add founded IP to the list
				dhcpLeases.append([ip])

			# If we found "hardware ethernet" save it to the list
			if line.find('hardware ethernet') != -1:
				dhcpLeases[idx].append(line[20:37])
			
			# If we found "client-hostname" save it to the list and set clientHostname to "True"
			if line.find('client-hostname') != -1:
				dhcpLeases[idx].append(line[19:(len(line)-3)])
				clientHostname = True

		# If we didn't find a hostname for the last IP in the file, we put "none" to the list
		if not clientHostname:
			dhcpLeases[idx].append("none")
	return dhcpLeases


def getCurrentConn():
		# Get a wifi network the device is currently connected to
		currentConn = None
		error = False

		# Get an output of the "nmcli" command
		try:
			output = subprocess.check_output("nmcli -t connection show --active | grep wlan0", shell=True)
		except:
			error = True
		else:
			currentConn = stdoutParse(output)

		# If the device is connected to any wifi network then we return a name of that network
		if currentConn is not None:
			return currentConn[0][0]
		else:
			return currentConn
