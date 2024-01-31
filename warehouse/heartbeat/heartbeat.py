import time, socket, threading

class HeartBeat:
    def __init__(self, ips) -> None:
        self.ip_array = ips
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def send_heartbeat(self):
        while True:
            for ip in self.ip_array:
                message = "Heartbeat from {}".format(socket.gethostname())
                self.socket.sendto(message.encode(), (ip, 12345))
            time.sleep(5)

    def _receive(self):
        self.socket.bind(('0.0.0.0', 12345))
        while True:
            data, addr = self.socket.recvfrom(1024)
            print("Received heartbeat from {}: {}".format(addr[0], data.decode()))