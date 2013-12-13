import csv
import os
import sys
import time
import web
from web import form

sys.path.append(os.getcwd())
from dhcplease import build_lease_dict

render = web.template.render('templates/')

urls = (
  '/', 'register'
)

app = web.application(urls, globals())

macform = form.Form( 
    form.Textbox('sticker',
        form.notnull,
        form.regexp('A001[\d]{3}', 'Like A001001'),
        value='A001',
        post='The A001... number from the yellow sticker'
    ), 
    form.Textbox('label', 
        form.notnull,
        form.regexp('([NS]C[123]|RM[\d]+)-[\d+]', 'Like NC2-20'),
        post='The cart or room name and CB number, like NC2-20'
    ),
    form.Textbox('username',
        form.notnull,
        post='Your username, like 17sandyp'
    )
)

def log_mac_address(sticker, label, username, mac_address, ip_address, created_at):
    with open('mac_address.csv', 'a+b') as csvfile:
        w = csv.writer(csvfile)
        w.writerow([ sticker, label, username, mac_address, ip_address, 
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(created_at)) ])

def dhcp_lookup(ip_address, sticker, label, username):
    t_now = time.time()
    d_ip = build_lease_dict()
    
    if ip_address not in d_ip:
        return "Your IP address, %s, was not found." % ip_address
    else:
        mac_address = d_ip[ip_address]['macAddress']
        log_mac_address(sticker, label, username, mac_address, ip_address, t_now)
        return "Your IP address, %s, was leased to MAC address %s!" % (ip_address, mac_address)


class register:
    def GET(self): 
        ua = web.ctx.env['HTTP_USER_AGENT']
        if 'CrOS' in ua:
            form = macform()
            return render.regform(form)
        else:
            return render.invalidua(ua)

    def POST(self): 
        ua = web.ctx.env['HTTP_USER_AGENT']
        if 'CrOS' in ua:
            form = macform() 
            if not form.validates(): 
                return render.regform(form)
            else:
                msg = dhcp_lookup(web.ctx['ip'], form.sticker.value, form.label.value, form.username.value)
                return render.thankyou(msg, form.username.value)
        else:
            return render.invalidua(ua)
            

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

# serveradmin fullstatus dhcp