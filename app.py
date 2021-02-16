#import wifi
# WLAN0 and WLAN1 are hardcoded to WAN and LAN accordingly
import os, subprocess, requests, urllib.parse, ipaddress, re
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class WifiNetwork:
	def __init__(self, ssid, ch, rate, signal):
		self.ssid = ssid
		self.ch = ch
		self.rate = rate
		self.signal = signal

	def connect(self, passwd):
		connect = subprocess.check_output('nmcli dev wifi connect ' + self.ssid + ' password ' + passwd, text=True, shell=True)
		
	def __str__(self):
		return f"SSID: {self.ssid}"

def getMyAP():
	# reading local SSID from config file /etc/hostapd/hostapd.conf
	with open('/etc/hostapd/hostapd.conf', 'r') as file:
		for line in file:
			if line[:5] == "ssid=":
				return line[5:-1]
myAP = getMyAP()


@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "GET":
		session["wan_connection_successfull"] = False
		# session["rescan"] = False

		# wan, lan, statusList = getNetworkInterfaces()
		clients = wifiClients()
		currentConn = getCurrentConn()

		return render_template("main.html", clients=clients, myap=myAP, currentconn=currentConn)
		
	else:
		# If "Disconnect" button has been pressed then disconnect from current wifi connection and purge all saved wifi networks
		button = request.form['button']
		if button == "Scan":
			return redirect("/networks")
		
		#disconnect = None
		error = False

		try:
			disconnect = subprocess.check_output("nmcli --fields NAME -t connection show | grep -v Wired | xargs -I «{}» nmcli connection delete «{}»", shell=True)
		except subprocess.CalledProcessError as disconnectexc:
			print("error code " + disconnectexc.output)
			return redirect("/")
		else:
			flash('Successfully disconnected!')
			session["wan_disconnection_successfull"] = True
		return redirect("/")


@app.route("/networks", methods=["GET", "POST"])
def networks():
	if request.method == "GET":

		outputList = None
		error = False
		try:
			output = subprocess.check_output("nmcli -t -f SSID,CHAN,RATE,SIGNAL,IN-USE dev wifi", shell=True)
		except:
			error = True
		else:
			# Delete last empty string of the output
			output = output[:-1]

			outputList = stdoutParse(output)

			#wifiList = stdoutParse1(output)
			#print(wifiList)

		#outputList = [['YourAPSSID', '1', '65 Mbit/s', '100', ' '], ['Space3', '3', '130 Mbit/s', '100', ' '], ['Space2', '6', '130 Mbit/s', '75', '*'],['Tolik', '8', '270 Mbit/s', '42', ' ']]
			session["output_list"] = outputList

		wan, lan, statusList = getNetworkInterfaces()
		clients = wifiClients()
		currentConn = getCurrentConn()

		# /sys/class/net/
		return render_template("networks.html", myAP=myAP, currentConn=currentConn, error=error, outputList=outputList, wan=wan, lan=lan, clients = wifiClients())

	else:
		# If "Rescan" button has been pressed then rescan wifi networks
		button = request.form['button']
		if button == "Rescan":
			return redirect("/networks")
		else:
			passwd = request.form.get("passwd")
			if passwd != '':
				connect = None
				error = False

				for n in wifiList:
					if session["output_list"][int(button)-1][0] == n.ssid:
						try:
							connect = n.connect(passwd)
						except:
							error = True
						else:
							connect = connect[:-1]
						if connect.find('successfully') != -1:
							flash('Successfully connected!')
							session["wan_connection_successfull"] = True
							return redirect("/")
				# try:
				# 	WifiNetwork.connect(passwd)
				# 	#connect = subprocess.check_output('nmcli dev wifi connect ' + session["output_list"][int(button)-1][0] + ' password ' + passwd, text=True, shell=True)
				# except:
				# 	error = True
				# else:
				# 	connect = connect[:-1]
				# if connect.find('successfully') != -1:
				# 	flash('Successfully connected!')
				# 	session["wan_connection_successfull"] = True
				# 	return redirect("/")

				else:
					flash('Connection error!')
					return redirect("/networks")
			else:
				flash('You must provide a password!')
				# return redirect("/")
			
			return redirect("/networks")


def stdoutParse(stdout):
	outputList = []
	string = ''
	for n in stdout:
		if n != 10:	# End of line
			string += chr(n)
		else:
			s = string.split(":")
			outputList.append(s)
			string = ''
	return outputList

def stdoutParse1(stdout):
	arr = []
	string = ''
	for n in stdout:
		if n != 10:	# End of line
			string += chr(n)
		else:
			s = string.split(":")
			#print(s)
			#wifi = WifiNetwork(s[0], s[1], s[2], s[3])
			arr.append(wifi)
			print(wifi)
			string = ''
	return arr


def getNetworkInterfaces():
	interfaces = subprocess.check_output("ls /sys/class/net/", text=True, shell=True)
	interfaces = interfaces[:-1]

	status = subprocess.check_output('nmcli -t dev status', shell=True)

	# Delete last empty string of the output
	status = status[:-1]

	statusList = stdoutParse(status)

	if (interfaces.find('wlan0') != -1):
		wan = "Internet: wlan0"
	else:
		wan = "Internet: Interface not found"
	if (interfaces.find('wlan1') != -1):
		lan = "Local: wlan1"
	else:
		lan = "Local: Interface not found"

	return (wan, lan, statusList)

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

		# If we didn't find hostname for last IP in the file we put "none" to the list
		if not clientHostname:
			dhcpLeases[idx].append("none")
	return dhcpLeases


def getCurrentConn():
		currentConn = None
		error = False
		try:
			output = subprocess.check_output("nmcli -t connection show --active | grep wlan0", shell=True)
		except:
			error = True
		else:
			currentConn = stdoutParse(output)

		if currentConn is not None:
			return currentConn[0][0]
		else:
			return currentConn


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
