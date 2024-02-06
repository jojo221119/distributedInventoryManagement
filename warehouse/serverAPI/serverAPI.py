import logging
import pickle
import socket
import netifaces



class ServerAPI:
    def __init__(self):
        self.broadcastIp = self.__getBroadcastIP()

    def __getBroadcastIP(self):
        ips = []
        for iface in netifaces.interfaces():
            if iface == 'lo' or iface.startswith('vbox'):
                continue
            iface_details = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in iface_details:
                ips.append(iface_details[netifaces.AF_INET])
        return ips[0][0]["broadcast"]

    def __getServerIPs(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            # Broadcast a discovery message
            DISCOVERY_MESSAGE = {'type': "client"}
            broadcast_socket.sendto(pickle.dumps(DISCOVERY_MESSAGE), (self.broadcastIp, 64000))

            # Listen for responses
            broadcast_socket.settimeout(2)  # Timeout for listening (in seconds)
            while True:
                data, addr = broadcast_socket.recvfrom(1024)
                message = pickle.loads(data)
                logging.debug(f"Received: {message}")
                if "type" in message.keys() and message["type"] == "servers":
                    print(f"Discovered leader at {addr[0]}:{addr[1]}")
                    broadcast_socket.settimeout(None)
                    broadcast_socket.close()
                    hosts = list(message["hosts"].keys())
                    return hosts

        except socket.timeout:
            logging.debug("Discovery complete or timeout reached.")

        finally:
            broadcast_socket.close()
        return []

    def sendMessageToServer(self, message):
        hosts = self.__getServerIPs()
        logging.debug(f"{hosts}")
        if len(hosts) < 1:
            return {"type": "Error"}
        server_host = hosts[0]
        server_port = 12347

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        client_socket.sendto(pickle.dumps(message), (server_host, server_port))

        r, server_address = client_socket.recvfrom(1024)
        response = pickle.loads(r)
        logging.debug(f"Received response from {server_address}: {response}")

        client_socket.close()
        return response