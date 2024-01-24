import json

import logging
import queue
import socket
import struct
import sys
import threading
import uuid
from time import sleep

# Configure the logging settings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


id = str(uuid.uuid4())
quorum = 1

def get_ip_address():
        # Get the local hostname
        hostname = socket.gethostname()

        # Get the IP address associated with the hostname
        ip_address = socket.gethostbyname(hostname)

        return ip_address

class Message(dict):
    def __init__(self, seq, sender, message, type):
        dict.__init__(self, seq = seq, sender = sender, message = message, type = type)

class Log:
    def __init__(self):
        self.log = {}
    
    def addMessage(self, message):
        entry = {
            "message": message["message"],
            "seq": message["seq"],
            "commit": False,
            "ack_count": 0 
        }
        self.log[message["seq"]] = entry
    
    def commitMessage(self, message):
        self.log[message["seq"]]["commit"] = True
    
    def increment_ack(self, message):
        self.log[message["seq"]]["ack_count"] += 1
        return self.log[message["seq"]]["ack_count"]
    
    def getAckCount(self, message):
        return self.log[message["seq"]]["ack_count"]

    def messageInLog(self, message):
        return message["seq"] in self.log.keys()
    
    def getMessage(self, seq):
        if seq in self.log.keys():
            return self.log[seq]
        else:
            return {}

class OrderedReliableMulticast:

    def __init__(self, multicast_group_ip, port, leader, delivery_queue):
        self.port = port
        self.group_ip = multicast_group_ip
        self.delivery_queue = delivery_queue
        self.leader = leader
        self.holdback_queue = {}
        self.seq = 0

    def setup(self):
        multicast_group = (self.group_ip, self.port)

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to a specific interface and port
        sock.bind(('0.0.0.0', 10000))

        # Join the multicast group
        group = socket.inet_aton(multicast_group[0])
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock = sock
        logging.debug(f"Waiting for multicast messages from {multicast_group}...")

    def send_multicast_message(self, message):
        multicast_group = (self.group_ip, self.port)
        
        logging.debug(f"Send {message} to Multicast group {self.group_ip}:{self.port}")
        self.sock.sendto(json.dumps(message).encode(), multicast_group)

    def receive_multicast_messages(self):

        while True:
            data, _ = self.sock.recvfrom(1024)
            message = json.loads(data.decode())
            if message['sender'] != id:
                logging.debug(f"Received message from {message['sender']}: {message}")
                if leader:
                    if message["type"] == "ack":
                        if log.messageInLog(message):
                            log.increment_ack(message)
                            logging.debug(f"ack Count: {log.getAckCount(message)}")
                            if log.getAckCount(message) >= quorum:
                                self.send_multicast_message(Message(seq=message["seq"], sender=id, message="", type="commit"))
                                log.commitMessage(message)
                                delivery_queue.put(log.getMessage(message["seq"]))
                elif message["type"] == "commit":
                    if log.messageInLog(message):
                        log.commitMessage(message)
                        delivery_queue.put(log.getMessage(message["seq"]))
                elif message["type"] == "message":
                    log.addMessage(message)
                    self.send_multicast_message(Message(seq=message["seq"], sender=id, message="", type="ack"))
            



    def start(self):
        self.setup()
        self.receive_multicast_messages()

def myTimer(seconds, delivery_queue):
    while True:
        sleep(seconds)
        logging.debug(f"Delivered {delivery_queue.get()}")



if __name__ == "__main__":

    print(id)

    leader = False
    if len(sys.argv) > 1 and sys.argv[1] == "leader":
        leader = True

    logging.debug(f"I am Leader {leader}")

    delivery_queue = queue.Queue()
    client = OrderedReliableMulticast('224.0.0.1', 10000, leader, delivery_queue)

    clientThread = threading.Thread(target=client.start, daemon=True)

    for thread in [clientThread]:
        thread.start()

    


    log = Log()

    # Thread that will sleep in background and call your function
    # when the timer expires.
    myThread = threading.Thread(target=myTimer, args=(5,delivery_queue,))
    myThread.start()
    
    while True:
        if leader:
            seq = input("Enter sequence number to multicast: ")
            message = input("Enter message to multicast: ")
            message = Message(seq=seq, sender=id, message=message, type="message")
            log.addMessage(message)
            client.send_multicast_message(message)

    for thread in [clientThread]:
        thread.join()
