import socket
import pickle
import time
import random

class BullyAlgorithm:
    def __init__(self, sharedVar):
        self.sharedVar = sharedVar
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 12346))
        
    def election_listener(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.handle_message(data, addr)

    def start_election(self):
        self.sharedVar.leader = None
        time.sleep(random.randrange(4,32,4))
        self.sharedVar.election_in_progress = True
        if self.sharedVar.leader is None:
            for host in self.sharedVar.hosts.keys():
                self.send_message(host, {'type': 'election', 'addresse': self.sharedVar.ip, 'pid': self.sharedVar.pid})
            time.sleep(3)
            if self.sharedVar.leader is None:
                for host in self.sharedVar.hosts.keys():
                    self.send_message(host, {'type': 'coordinator', 'addresse': self.sharedVar.ip, 'pid': self.sharedVar.pid})
                self.sharedVar.leader = self.sharedVar.ip
                self.sharedVar.election_in_progress = False

    def handle_message(self, message, addr):
        sender_pid = message['pid']
        message_type = message['type']
        
        if message_type == 'election':
            self.handle_election_message(sender_pid, addr)
        elif message_type == 'coordinator':
            self.handle_coordinator_message(sender_pid, addr)

    def handle_election_message(self, sender_pid):
        if sender_pid < self.process_id:
            for host in self.hosts:
                self.send_message(host, {'type': 'election', 'addresse': self.ip, 'pid': self.process_id})
            time.sleep(3)
            if self.sharedVar.leader is None:
                for host in self.sharedVar.hosts.keys():
                    self.send_message(host, {'type': 'coordinator', 'addresse': self.sharedVar.ip, 'pid': self.sharedVar.pid})
                self.sharedVar.leader = self.sharedVar.ip
                self.sharedVar.election_in_progress = False


    def handle_coordinator_message(self, sender_addresse):
        self.sharedVar.leader = sender_addresse
        self.sharedVar.election_in_progress = False



    def send_message(self, receiver, message):
        receiver_address = (receiver, 12345)
        self.sock.sendto(pickle.dumps(message), (receiver_address, 12345))


