import struct
import sys
from datetime import datetime
from pypureomapi import *

# Load OMAPI_KEYNAME and OMAPI_ENCODED_KEY into global namespace
execfile("./omapi_secrets.py", globals())

DHCP_SERVER_IP = "10.4.51.70"
OMAPI_PORT = 7911
OMAPI_OP_UPDATE = 3

def unpack_uint8(b):
    return struct.unpack("!B", b[:1])[0]

def unpack_uint32(b):
    return struct.unpack("!I", b[:4])[0]
    
def unpack_ts(b):
    ts = unpack_uint32(b)
    if ts == 0:
        return None
    return datetime.fromtimestamp(ts)

def get_lease_object(omapi, ip):
    """
    @type omapi: Omapi
    @type ip: str
    @rtype: OmapiMessage
    @raises OmapiErrorNotFound:
    @raises socket.error:
    """
    msg = OmapiMessage.open(b"lease")
    msg.obj.append((b"ip-address", pack_ip(ip)))
    response = omapi.query_server(msg)
    if response.opcode != OMAPI_OP_UPDATE:
        raise OmapiErrorNotFound()
        
    lease = dict(response.obj)
    lease['flags']            = unpack_uint8(lease['flags'])
    lease['state']            = unpack_uint32(lease['state'])
    lease['hardware-type']    = unpack_uint32(lease['hardware-type'])
    lease['hardware-address'] = unpack_mac(lease['hardware-address'])
    # lease['client-hostname']
    # lease['dhcp-client-identifier']
    lease['ip-address']       = unpack_ip(lease['ip-address'])
    lease['subnet']           = unpack_uint32(lease['subnet'])
    lease['pool']             = unpack_uint32(lease['pool'])
    lease['starts']           = unpack_ts(lease['starts'])
    lease['ends']             = unpack_ts(lease['ends'])
    lease['cltt']             = unpack_ts(lease['cltt'])
    lease['tsfp']             = unpack_ts(lease['tsfp'])
    lease['atsfp']            = unpack_ts(lease['atsfp'])
    lease['tstp']             = unpack_ts(lease['tstp'])
    return lease

if __name__=='__main__':
    lease_ip = sys.argv[1]
    try:
        omapi = Omapi(DHCP_SERVER_IP, OMAPI_PORT, OMAPI_KEYNAME, OMAPI_ENCODED_KEY)
        mac = omapi.lookup_mac(lease_ip)
        print "%s is currently assigned to mac %s" % (lease_ip, mac)
        d = get_lease_object(omapi, lease_ip)
        print "lease object: %s" % d
    except OmapiErrorNotFound:
        print "%s is currently not assigned" % (lease_ip,)
    except OmapiError, err:
        print "an error occured: %r" % (err,)

    
