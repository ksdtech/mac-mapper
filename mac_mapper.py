#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7
import csv
import os
import sys
import time
import web
from web import form
from netaddr import IPNetwork, IPAddress, IPSet, IPRange
from pypureomapi import *

# Load OMAPI_KEYNAME and OMAPI_ENCODED_KEY into global namespace
execfile("./omapi_secrets.py", globals())

# Check User-Agent to see if request is running CrOs
ENFORCE_CROS = True
OMAPI_PORT = 7911

BACICH_DHCP_SERVER = "10.3.51.73"
KENT_DHCP_SERVER   = "10.4.51.70"

# Bacich - 10.3.51.73
# range 10.3.64.1 10.3.67.254;
# range 10.7.64.1 10.7.67.254;
# range 10.11.64.1 10.11.67.254;
bacich_10_3  = IPRange('10.3.64.1',  '10.3.67.254').cidrs()
bacich_10_7  = IPRange('10.7.64.1',  '10.7.67.254').cidrs()
bacich_10_11 = IPRange('10.11.64.1', '10.11.67.254').cidrs()
bacich_all   = IPSet(bacich_10_3 + bacich_10_7 + bacich_10_11)

# Kent - 10.4.51.70
# range 10.2.60.1 10.2.63.254;
# range 10.4.64.1 10.3.67.254;
# range 10.6.60.1 10.6.63.254;
# range 10.8.64.1 10.8.67.254;
# range 10.10.64.1 10.10.67.254;
# range 10.12.64.1 10.12.67.254;
kent_10_2  = IPRange('10.2.60.1',  '10.2.63.254').cidrs()
kent_10_4  = IPRange('10.4.64.1',  '10.4.67.254').cidrs()
kent_10_6  = IPRange('10.6.60.1',  '10.6.63.254').cidrs()
kent_10_8  = IPRange('10.8.64.1',  '10.8.67.254').cidrs()
kent_10_10 = IPRange('10.10.64.1', '10.10.67.254').cidrs()
kent_10_12 = IPRange('10.12.64.1', '10.12.67.254').cidrs()
kent_all   = IPSet(kent_10_2 + kent_10_4 + kent_10_6 + 
    kent_10_8 + kent_10_10 + kent_10_12)

LOOKUPS = [
    (bacich_all, BACICH_DHCP_SERVER),
    (kent_all,   KENT_DHCP_SERVER),
]

def find_server(ip_address):
    test = IPAddress(ip_address)
    for ip_set, server_ip in LOOKUPS:
        if test in ip_set:
            try:
                omapi = Omapi(server_ip, OMAPI_PORT, OMAPI_KEYNAME, OMAPI_ENCODED_KEY)
            except:
                omapi = None
            return (server_ip, omapi)
    return (None, None)

def log_mac_address(sticker, label, username, mac_address, ip_address, created_at):
    with open('mac_address.csv', 'a+b') as csvfile:
        w = csv.writer(csvfile)
        w.writerow([ sticker, label, username, mac_address, ip_address, 
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(created_at)) ])

def dhcp_lookup(ip_address, sticker, label, username):
    t_now = time.time()
    (server_ip, omapi) = find_server(ip_address)
    if not server_ip:
        return "Could not map a DHCP server for %s" % ip_address
    if not omapi:
        return "Problem connecting to %s DHCP server API" % server_ip
    try:
        mac_address = omapi.lookup_mac(ip_address)
        log_mac_address(sticker, label, username, mac_address, ip_address, t_now)
        return "Your IP address, %s, was assigned to the hardware address %s." % (ip_address, mac_address)
    except:
        return "Your IP address, %s, was not found." % ip_address

render = web.template.render('templates/')

macform = form.Form( 
    form.Textbox('sticker',
        form.notnull,
        form.regexp('A001[\d]{3}', '&nbsp;Like A001001'),
        value='A001',
        post='&nbsp;The A001... number from the yellow sticker'
    ), 
    form.Textbox('label', 
        form.notnull,
        form.regexp('([NS]C[123]|RM[\d]+|CB|TO)-[\d+]', '&nbsp;Like NC2-20'),
        post='&nbsp;The cart or room name and CB number, like NC2-20, RM23-20, or CB-20'
    ),
    form.Textbox('username',
        form.notnull,
        post='&nbsp;Your username, like 17sandyp'
    )
)

class MacMapper:
    def GET(self): 
        ua = web.ctx.env['HTTP_USER_AGENT']
        if 'CrOS' in ua or not ENFORCE_CROS:
            form = macform()
            return render.registration_form(form, ua)
        else:
            return render.invalid_ua(ua)

    def POST(self): 
        ua = web.ctx.env['HTTP_USER_AGENT']
        if 'CrOS' in ua or not ENFORCE_CROS:
            form = macform() 
            if not form.validates():
                return render.registration_form(form, ua)
            else:
                msg = dhcp_lookup(web.ctx['ip'], form.sticker.value, form.label.value, form.username.value)
                return render.thank_you(msg, form.username.value)
        else:
            return render.invalid_ua(ua)
            
urls = ('/.*', 'MacMapper')
app = web.application(urls, globals())
web.internalerror = web.debugerror

if __name__=="__main__":
    app.run()
