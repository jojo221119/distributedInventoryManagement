from datetime import datetime
import logging
import pickle
import random
import socket
import sys
from time import sleep
import time
import netifaces
import socket
import threading


DISCOVERY_PORT = 64000



class Networking:
    def __init__(self, sharedVar):
        self.interface = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        self.ips = self.getAllIps()
        self.broadcastIp = self.ips[0][0]["broadcast"]
        self.ip = socket.gethostbyname(socket.gethostname())
        self.sharedVar = sharedVar

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
        logging.debug(f'sending on {self.ip}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_TCP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((self.broadcastIp,0))
        sock.sendto(pickle.dumps(message), ("255.255.255.255", 8089))
        sock.close()

        sleep(2)

    def discover_hosts(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sleep(random.randrange(3,32,4))

        try:
            DISCOVERY_MESSAGE = {'type': "discovery", 'addresse':self.ip}
            broadcast_socket.sendto(pickle.dumps(DISCOVERY_MESSAGE), (self.broadcastIp, DISCOVERY_PORT))

            broadcast_socket.settimeout(2)  # Timeout for listening (in seconds)
            while True:
                data, addr = broadcast_socket.recvfrom(1024)
                message = pickle.loads(data)
                logging.debug(f"Received: {message}")
                if "type" in message.keys() and message["type"] == "discovered":
                    logging.debug(f"Discovered leader at {addr[0]}:{addr[1]}")
                    broadcast_socket.settimeout(None)
                    broadcast_socket.close()
                    self.sharedVar.hosts = message["hosts"] 
                    return addr[0]

        except socket.timeout:
            logging.debug("Discovery complete or timeout reached.")

        finally:
            broadcast_socket.close()
        
        self.sharedVar.hosts[self.ip] = datetime.now()
        return self.ip

    def respond_to_discovery(self):
        response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        response_socket.bind(('0.0.0.0', DISCOVERY_PORT))

        try:
            while True:
                data, addr = response_socket.recvfrom(1024)
                message = pickle.loads(data)
                logging.debug(f"Received {message}")
                if self.sharedVar.leader == self.ip and  "type" in message.keys() and message["type"] == "discovery":
                    self.sharedVar.hosts[addr[0]] = datetime.now()
                    RESPONSE_MESSAGE = {'type': "discovered", 'addresse':self.ip, "foreignAdress":message["addresse"], "hosts": self.sharedVar.hosts}
                    response_socket.sendto(pickle.dumps(RESPONSE_MESSAGE), addr)
                elif self.sharedVar.leader == self.ip and  "type" in message.keys() and message["type"] == "client":
                    RESPONSE_MESSAGE = {'type': "servers", 'addresse':self.ip, "foreignAdress":addr[0], "hosts": self.sharedVar.hosts}
                    logging.debug(f"Send {RESPONSE_MESSAGE}")
                    response_socket.sendto(pickle.dumps(RESPONSE_MESSAGE), addr)
                    


        finally:
            response_socket.close()
