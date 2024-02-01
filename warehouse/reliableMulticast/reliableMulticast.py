import json

import logging
import queue
import socket
import struct
import sys
import threading
from time import sleep
import platform
from log import Log
from message import Message

# Configure the logging settings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ReliableMulticaster:

    def __init__(self, multicastGroupIp, port, id, leaderId, groupSize, deliveryQueue):
        self.port = port
        self.groupIp = multicastGroupIp
        self.delivery_queue = deliveryQueue
        self.leader = leaderId
        self.holdback_queue = {}
        self.seq = 0
        self.id = id
        self.log = Log()
        self.groupSize = groupSize

    def setup(self):
        multicast_group = (self.groupIp, self.port)

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to a specific interface and port
        sock.bind(('0.0.0.0', 10000))

        # Join the multicast group
        group = socket.inet_aton(multicast_group[0])
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock = sock

        logging.debug(f"Sequence Number: {self.seq}")
        logging.debug(f"Waiting for multicast messages from {multicast_group}...")

    def start(self):
        self.setup()
        while True:
            self.receive_multicast_messages()

    def __send_multicast_message(self, message):
        multicast_group = (self.groupIp, self.port)
        logging.debug(f"Send {message} to Multicast group {self.groupIp}:{self.port}")
        self.sock.sendto(json.dumps(message).encode(), multicast_group)

    def receive_multicast_messages(self):

        data, _ = self.sock.recvfrom(1024)
        message = json.loads(data.decode())
        if message['sender'] != myid:
            logging.debug(f"Received message from {message['sender']}: {message}")
            
            if self.leader == self.id:
                if message["type"] == "ack":
                    self.__receiveAcknowledge(message)
                elif message["type"] == "missing":
                    self.__receiveMissing(message)


            elif message["type"] == "commit":
                logging.debug(f"Received commit message")
                self.__receiveCommit(message)

            elif message["type"] == "message":
                self.__receiveMessage(message)
            
            elif message["type"] == "abort":
                self.__receiveAbort(message)


    def sendMessage(self, content):
        self.seq += 1
        m = Message(seq=self.seq, sender=myid, content=content, type="message")
        self.log.addMessage(m)
        self.log.acknowledgeMessage(m)
        self.__send_multicast_message(m)

        for i in range(3):
            sleep(5)
            if not self.log.isMessageCommited(m):
                if i < 2:
                    self.__send_multicast_message(m)
                else:
                    m = Message(seq=self.seq, sender=myid, content="", type="abort")
                    self.__send_multicast_message(m)
                    self.log.removeMessage(m)
                    self.seq -= 1
                    logging.debug(f"Abort message {m}")
                return False
            else:
                return True
            
    
    def __sendCommit(self, seq):
        m = Message(seq=seq, sender=myid, content="", type="commit")
        self.__send_multicast_message(m)

    def __sendAcknowledge(self, seq):
        m = Message(seq=seq, sender=myid, content="", type="ack")
        self.__send_multicast_message(m)

    def __sendMissing(self,lastReceivedSeq):
        m = Message(seq=None, sender=myid, content=f"{self.seq + 1},{lastReceivedSeq}", type="missing")
        self.__send_multicast_message(m)


    def __receiveMissing(self, message):
        numbers = message["content"].split(",")
        
        for i in range(int(numbers[0]), int(numbers[1])):
            m = self.log.getMessage(i)
            self.__send_multicast_message(m)

    def __receiveCommit(self, message):
        if message["seq"] > (self.seq + 1) or not self.log.messageInLog(message):
            logging.debug(f"Received commit for unknown message")
            self.__sendMissing(message["seq"])       
        else:
            if not self.log.isMessageCommited(message):
                self.seq += 1
                self.__commitMessageAndForwardContent(message)


    def __receiveAcknowledge(self, message):
        if self.log.messageInLog(message):
            ackCount = self.log.acknowledgeMessage(message)
            logging.debug(f"AckCount {ackCount}, Quorum {int(self.groupSize)} reached {ackCount >= (int(self.groupSize))}")
            if ackCount >= int(self.groupSize):
                self.__sendCommit(message["seq"])
                if not self.log.isMessageCommited(message):
                    self.__commitMessageAndForwardContent(message)

    def __receiveMessage(self, message):
        if not self.log.messageInLog(message):
            self.log.addMessage(message)

        self.__sendAcknowledge(message["seq"])

    def __receiveAbort(self, message):
        self.log.removeMessage(message)

    def __commitMessageAndForwardContent(self,message):
        seq = message["seq"]
        self.log.commitMessage(message)
        m = self.log.getMessage(seq)
        logging.debug(f"Deliver message {m}")
        delivery_queue.put(m["content"])


def myTimer(seconds, deliveryQueue):
    while True:
        sleep(seconds)
#        if deliveryQueue.empty():
#            logging.debug("Waiting for delivery")
#        else:    
        logging.info(f"Processed {deliveryQueue.get()}")



if __name__ == "__main__":

    myid = platform.node()
    #str(uuid.uuid4())
    quorum = 1

    
    
    if len(sys.argv) > 1 and sys.argv[1] == "leader":
        leaderId = myid
    else:
        leaderId = "leader"

    logging.debug(f"My ID: {myid}")
    logging.debug(f"Leader ID: {leaderId}")

    groupSize = 3

    delivery_queue = queue.Queue()
    client = ReliableMulticaster('224.0.0.1', 10000, myid, leaderId, groupSize, delivery_queue)

    clientThread = threading.Thread(target=client.start, daemon=True)

    for thread in [clientThread]:
        thread.start()



    # Thread that will sleep in background and call your function
    # when the timer expires.
    myThread = threading.Thread(target=myTimer, args=(5,delivery_queue,))
    myThread.start()
    
    while True:
        if leaderId == myid:
            for i in range(1,1000):
                input("Enter message to multicast: \n") 
                client.sendMessage(f"test{i}")
            
            #message =            
            #client.sendMessage(message)

    for thread in [clientThread]:
        thread.join()
