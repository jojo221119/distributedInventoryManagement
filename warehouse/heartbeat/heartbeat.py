from datetime import datetime, timedelta
import pickle
import time, socket

TIMEOUTSEC = 3

class HeartBeat:
    def __init__(self, sharedVars) -> None:
        self.sharedVars = sharedVars
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


    def send_heartbeat(self):
        while True:
            message = {"ip": self.sharedVars.ip}
            self.socket.sendto(pickle.dumps(message), (self.sharedVars.broadcastIP, 12345))
            time.sleep(1)

    def receive(self):
        self.socket.bind(('0.0.0.0', 12345))
        while True:
            data, addr = self.socket.recvfrom(1024)
            print("Received heartbeat from {}: {}".format(addr[0], pickle.loads(data)))
            if addr[0] in self.sharedVars.hosts and not self.sharedVars.hosts[addr[0]] < datetime.now()-timedelta(seconds=TIMEOUTSEC) :
               self.sharedVars.hosts[addr[0]] = datetime.now()
            
            for host,timestamp in self.sharedVars.hosts.items():
                if timestamp < datetime.now()-timedelta(seconds=TIMEOUTSEC):
                    del self.sharedVars.hosts[host]