import logging
import socket
import pickle
import time


class BullyAlgorithm:
    def __init__(self, sharedVar):
        self.sharedVar = sharedVar
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 12346))
        self.abortOwnElection = False
        
    def election_listener(self):
        logging.debug(f"Start Listening")
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.handle_message(pickle.loads(data), addr)

    def start_election(self):
        if not self.sharedVar.election_in_progress:
            if self.abortOwnElection:
                self.abortOwnElection = False
                self.sharedVar.election_in_progress = False
                logging.debug("Abort Election")
                while self.sharedVar.leader == "":
                    time.sleep(1)
                return

            logging.debug(f"Start election")
            self.sharedVar.leader = ""
            #time.sleep(random.randrange(4,32,4))
            self.sharedVar.election_in_progress = True
            if self.sharedVar.leader == "":
                for host in list(self.sharedVar.hosts.keys()):
                    self.send_message(host, {'type': 'election', 'addresse': self.sharedVar.ip, 'pid': self.sharedVar.pid})
                time.sleep(3)
                if self.abortOwnElection:
                    logging.debug("Abort Election")
                    while self.sharedVar.leader == "":
                        time.sleep(1)
                    self.abortOwnElection = False
                    self.sharedVar.election_in_progress = False
                    return

                if self.sharedVar.leader == "":
                    for host in list(self.sharedVar.hosts.keys()):
                        self.send_message(host, {'type': 'coordinator', 'addresse': self.sharedVar.ip, 'pid': self.sharedVar.pid})
                    self.sharedVar.leader = self.sharedVar.ip
                    self.abortOwnElection = False
                    self.sharedVar.election_in_progress = False

    def handle_message(self, message, addr):
        message_type = message['type']
        
        if message_type == 'election':
            self.handle_election_message(addr[0])
        elif message_type == 'coordinator':
            self.handle_coordinator_message(addr[0])

    def handle_election_message(self, sender_addresse):
        logging.debug(f"Received election message Own IP: {self.sharedVar.ip} sender: {sender_addresse} result: {sender_addresse < self.sharedVar.ip}")
        if sender_addresse < self.sharedVar.ip:
            self.start_election()
        else:
            self.abortOwnElection = True


    def handle_coordinator_message(self, sender_addresse):
        logging.debug(f"Received coordinator message Own IP: {self.sharedVar.ip} sender: {sender_addresse} result: {sender_addresse < self.sharedVar.ip}")
        if sender_addresse < self.sharedVar.ip:
            self.start_election()
        else:
            self.abortOwnElection = True
            self.sharedVar.leader = sender_addresse
            self.sharedVar.election_in_progress = False



    def send_message(self, receiver, message):
        if receiver != self.sharedVar.ip:

            receiver_address = (receiver, 12346)
            logging.debug(f"Send Message {message} to {receiver_address}")
            self.sock.sendto(pickle.dumps(message), receiver_address)
