import ipaddress
from flask import request

# Cloudflare IP ranges
CF_IPV4_RANGES = [
    '173.245.48.0/20',
    '103.21.244.0/22',
    '103.22.200.0/22',
    '103.31.4.0/22',
    '141.101.64.0/18',
    '108.162.192.0/18',
    '190.93.240.0/20',
    '188.114.96.0/20',
    '197.234.240.0/22',
    '198.41.128.0/17',
    '162.158.0.0/15',
    '104.16.0.0/13',
    '104.24.0.0/14',
    '172.64.0.0/13',
    '131.0.72.0/22',
]

CF_IPV6_RANGES = [
    '2400:cb00::/32',
    '2606:4700::/32',
    '2803:f800::/32',
    '2405:b500::/32',
    '2405:8100::/32',
    '2a06:98c0::/29',
    '2c0f:f248::/32',
]

class IP:
    def ipv4_in_range(ip, ip_range):
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(ip_range)
        except ValueError:
            return False
    
    def ipv6_in_range(ip, ip_range):
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(ip_range)
        except ValueError:
            return False
    
    def is_cloudflare_ip(ip):
        for cf_net in CF_IPV4_RANGES:
            if ipv4_in_range(ip, cf_net):
                return True
        for cf_net in CF_IPV6_RANGES:
            if ipv6_in_range(ip, cf_net):
                return True
        return False

    def get_ip():
        remote_addr = request.remote_addr
        cf_connecting_ip = request.headers.get('CF-Connecting-IP')
        if cf_connecting_ip and is_cloudflare_ip(remote_addr):
            return cf_connecting_ip

        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for and ipv4_in_range(remote_addr, '127.0.0.0/8'):
            # Use the first IP in the header list
            return x_forwarded_for.split(',')[0].strip()

        if x_forwarded_for and remote_addr == '10.0.1.10':
            return x_forwarded_for.split(',')[0].strip()

        return remote_addr
