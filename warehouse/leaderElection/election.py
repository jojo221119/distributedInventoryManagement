import socket
import pickle

class BullyAlgorithm:
    def __init__(self, process_id, hosts):
        self.process_id = process_id
        self.hosts = hosts
        self.coordinator = None
        self.election_in_progress = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = self.get_own_ip()
        self.sock.bind(('0.0.0.0', 12345))
        

    def start_election(self):
        self.election_in_progress = True
        for host in self.hosts:
            self.send_message(host, {'type': 'election', 'addresse': self.ip, 'pid': self.process_id})
        print(f"Process {self.process_id} initiates an election.")

    def handle_message(self, message):
        sender_pid = message['pid']
        message_type = message['type']
        sender_addresse = message['addresse']
        
        if message_type == 'election':
            self.handle_election_message(sender_pid, sender_addresse)
        elif message_type == 'coordinator':
            self.handle_coordinator_message(sender_pid, sender_addresse)

    def handle_election_message(self, sender_pid, sender_addresse):
        if sender_pid < self.process_id:
            for host in self.hosts:
                self.send_message(host, {'type': 'election', 'addresse': self.ip, 'pid': self.process_id})
        else:
            self.send_message(sender_addresse, {'type': 'coordinator', 'addresse': self.ip, 'pid': self.process_id})
            self.election_in_progress = False


    def handle_coordinator_message(self, sender_pid, sender_addresse):
        print(f"Process {sender_pid} acknowledges Process {self.process_id} as coordinator.")


    def send_message(self, receiver, message):
        receiver_address = (receiver, 12345)
        self.sock.sendto(pickle.dumps(message), (receiver_address, 12345))

    def update_hosts(self, hosts):
        self.hosts = hosts
    
    def get_own_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_address = sock.getsockname()[0]
        sock.close()
        return ip_address

