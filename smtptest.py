#!/usr/bin/env python3
"""smtptest.py: command-line smtp test connect and optional mail sender
Forked from:
https://github.com/turbodog/python-smtp-mail-sending-tester
Maintained:
https://github.com/marneu/python-smtp-mail-sending-tester/blob/master/smtptest.py

Usage: python smtptest.py [options] fromaddress toaddress serveraddress 
	This version is a bit more verbose on stderr and returns an error code

Examples:
	python smtptest.py bob@example.com mary@example.com mail.example.com
	python smtptest.py --debuglevel 1 --usetls -u bob -p xyzzy "Bob <bob@example.com>" mary@example.com mail.example.com

Using -q (quick) is only for internal servers, if address verification is enabled (shouldn't or exposed hosts)
At verbose == False and debuglevel == 0, smtptest will either succeed silently or print an error. Setting verbose or a debuglevel to 1 will generate intermediate output.

See also http://docs.python.org/library/smtplib.html

"""

__version__ = "1.1"
__author__ = "Lindsey Smith (lindsey.smith@gmail.com)"
__copyright__ = "(C) 2010 Lindsey Smith."
__license__ = "GPL2 or 3"
__credits__ = ["Lindsey Smith"]
__maintainer__ = "Markus Neubauer"
__email__ = "neubauer@.email-online.org"
__status__ = "Production"

import smtplib
from time import strftime
import sys
from optparse import OptionParser

fromaddr = ""
toaddr = ""
serveraddr = ""

usage = "Usage: %prog [options] fromaddress toaddress serveraddress"
parser = OptionParser(usage=usage)

parser.set_defaults(usetls=False)
parser.set_defaults(usessl=False)
parser.set_defaults(serverport=25)
parser.set_defaults(SMTP_USER="")
parser.set_defaults(SMTP_PASS="")
parser.set_defaults(debuglevel=0)
parser.set_defaults(verbose=False)
parser.set_defaults(quick=False)

parser.add_option("-t", "--usetls", action="store_true", dest="usetls", default=False, help="Connect using TLS, default is false")
parser.add_option("-s", "--usessl", action="store_true", dest="usessl", default=False, help="Connect using SSL, default is false")
parser.add_option("-n", "--port", action="store", type="int", dest="serverport", help="SMTP server port", metavar="nnn")
parser.add_option("-u", "--username", action="store", type="string", dest="SMTP_USER", help="SMTP server auth username", metavar="username")
parser.add_option("-p", "--password", action="store", type="string", dest="SMTP_PASS", help="SMTP server auth password", metavar="password")
parser.add_option("-q", "--quick", action="store_true", dest="quick", default=False, help="Use address verification method")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose message printing")
parser.add_option("-d", "--debuglevel", type="int", dest="debuglevel", help="Set to 1 to print smtplib.send messages", metavar="n")

(options, args) = parser.parse_args()
if len(args) != 3:
	parser.print_help()
	parser.error("incorrect number of arguments")
	sys.exit(-1)

fromaddr = args[0]
toaddr = args[1]
serveraddr = args[2]	
	
now = strftime("%Y-%m-%d %H:%M:%S")

msg = "From: %s\r\nTo: %s\r\nSubject: Test message from smtptest at %s\r\n\r\nTest message from the smtptest tool sent at %s" % (fromaddr, toaddr, now, now)

if options.verbose:
	print('usetls:', options.usetls)
	print('usessl:', options.usessl)
	print('from address:', fromaddr)
	print('to address:', toaddr)
	print('server address:', serveraddr)
	print('server port:', options.serverport)
	print('smtp username:', options.SMTP_USER)
	print('smtp password: *****')
	print('quick:', options.quick)
	print('smtplib debuglevel:', options.debuglevel)
	print("-- Message body ---------------------")
	print(msg)
	print("-------------------------------------")

server = None
if options.usessl:
	server = smtplib.SMTP_SSL()
else:
	server = smtplib.SMTP()

# can we connect?
server.set_debuglevel(options.debuglevel)
try:
	rc = server.connect(serveraddr, options.serverport)
	if rc[0] != 220:
		print('ERROR: can not connect to ', serveraddr, ':', options.serverport, file=sys.stderr)
		sys.exit(1)
except Exception as e:
	raise e
	sys.exit(1)

# ok proceed
server.ehlo()
# switch to TLS
if options.usetls:
	rc = server.starttls()
	if rc[0] != 220:
		server.quit()
		print('WARN: Server not secure ', serveraddr, ':', options.serverport, file=sys.stderr)
		sys.exit(2)

server.ehlo()
if options.SMTP_USER != "": 
	rc = server.login(options.SMTP_USER, options.SMTP_PASS)

if options.quick:
	rc = server.verify(toaddr)
	if rc[0] == 250:
		# short cut out connect works
		server.quit()
		sys.exit()
	if rc[1] == None:
		rc[1] = 'failed'
	print('WARN: VRFY', rc[1], serveraddr, ':', options.serverport, file=sys.stderr)
	msg = msg + "\r\n\r\nAddress verification failed"
	print('INFO: No quick, continue using mail...')

rc = server.sendmail(fromaddr, toaddr, msg)
if rc:
	print('ERROR: sending message ', serveraddr, ':', options.serverport, file=sys.stderr)
	sys.exit(3)
	
server.quit()
