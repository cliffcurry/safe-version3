
import netifaces
def get_mac_addr():
    interfaces=netifaces.interfaces()
# ['lo', 'eth0', 'tun2']

    listofstuff=netifaces.ifaddresses(interfaces[1])[netifaces.AF_LINK]
# [{'addr': '08:00:27:50:f2:51', 'broadcast': 'ff:ff:ff:ff:ff:ff'}]
    macadd=listofstuff[0]['addr']
    return macadd
    
print(get_mac_addr())

import json
import requests

r=requests.get('http://129.255.255.187')
print(r)
print(r.text)
