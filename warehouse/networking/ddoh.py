import socket
from time import sleep
import netifaces

class Networking:
    def __init__(self):
        self.interface = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        self.ips = self.getAllIps()
        self.broadcastIp = self.ips[0][0]["broadcast"]

    def getAllIps(self):
        ips = []
        for iface in netifaces.interfaces():
            if iface == 'lo' or iface.startswith('vbox'):
                continue
            iface_details = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in iface_details:
                ips.append(iface_details[netifaces.AF_INET])
        return ips
    
    def broadcast(self, message):
        print(f'sending on {ip}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_TCP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((self.broadcastIp,0))
        sock.sendto(message, ("255.255.255.255", 8089))
        sock.close()

        sleep(2)