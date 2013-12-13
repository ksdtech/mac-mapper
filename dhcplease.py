import os
import re

def build_lease_dict():
    prog = re.compile(r'dhcp:dhcpLeasesArray:_array_index:(\d+):(ipAddress|macAddress|computerName)\s*=\s*\"(.+)\"')

    d_index = { }
    d_ip = { }
    for line in os.popen('serveradmin fullstatus dhcp', 'r').readlines():
        m = prog.match(line.strip())
        if m:
            i = m.group(1)
            if i not in d_index:
                d_index[i] = { 'index': i }
            k = m.group(2)
            v = m.group(3)
            d_index[i][k] = v
            if k == 'ipAddress':
                d_ip[v] = d_index[i]
    
    return d_ip

if __name__=="__main__":
    d_ip = build_lease_dict()
    for k, v in d_ip.iteritems():
        print("ip %s -> mac %s" % (k, v['macAddress']))