from netaddr import IPNetwork, IPAddress, IPSet, IPRange

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
            return server_ip
    return None

print find_server('10.3.66.101')
print find_server('10.2.61.101')
print find_server('10.5.64.102')
