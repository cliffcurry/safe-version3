from netaddr import EUI, mac_bare
import sys
sys.path.insert(0, '../ui/django_macaddress/macaddress')
import django_macaddress
# from macaddress import format_mac
# from macaddress.fields import MACAddressField
x=django_macaddress.macaddress.fields.MACAddressField(null=True, blank=True,primary_key=True)
# mac = EUI('00:12:3c:37:64:8f')
# format_mac(mac, mac_bare)

# format_mac(mac, 'netaddr.mac_cisco')
