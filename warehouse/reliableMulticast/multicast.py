from datetime import datetime, timedelta
import json

import logging
import socket
import struct
from time import sleep

from serverLogic.inventory import Inventory
from .log import Log
from .message import Message

# Configure the logging settings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ReliableMulticaster:

    def __init__(self, multicastGroupIp, port, sharedVar, inventory):
        self.sharedVar = sharedVar
        self.port = port
        self.groupIp = multicastGroupIp
        self.inventory = inventory
        self.holdback_queue = {}
        self.seq = 0
        self.log = Log()

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
#        if message['sender'] != self.sharedVar.ip:
        logging.debug(f"Received message from {message['sender']}: {message}")
        
        if message["type"] == "message":
            self.__receiveMessage(message)
        elif self.sharedVar.leader == self.sharedVar.ip:
            if message["type"] == "ack":
                self.__receiveAcknowledge(message)
            elif message["type"] == "missing":
                self.__receiveMissing(message)


        elif message["type"] == "commit":
            logging.debug(f"Received commit message")
            self.__receiveCommit(message)

            
        elif message["type"] == "abort":
            self.__receiveAbort(message)


    def sendMessage(self, content):
        self.seq += 1
        m = Message(seq=self.seq, sender=self.sharedVar.ip, content=content, type="message")
        self.log.addMessage(m)
        self.__send_multicast_message(m)

        for i in range(3):
            t = datetime.now()
            while t > datetime.now()-timedelta(seconds=5):
                if self.log.isMessageCommited(m):
                    return self.log.getResponse(m)
            logging.debug(i)
            if i < 2:
                self.__send_multicast_message(m)
            else:
                m = Message(seq=self.seq, sender=self.sharedVar.ip, content="", type="abort")
                self.__send_multicast_message(m)
                response = self.log.getResponse(m)
                self.log.removeMessage(m)
                self.seq -= 1
                logging.debug(f"Abort message {m}")
                return response


            
    
    def __sendCommit(self, seq):
        m = Message(seq=seq, sender=self.sharedVar.ip, content="", type="commit")
        self.__send_multicast_message(m)

    def __sendAcknowledge(self, seq):
        m = Message(seq=seq, sender=self.sharedVar.ip, content="", type="ack")
        self.__send_multicast_message(m)

    def __sendMissing(self,lastReceivedSeq):
        m = Message(seq=None, sender=self.sharedVar.ip, content=f"{self.seq + 1},{lastReceivedSeq}", type="missing")
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
            logging.debug(f"AckCount {ackCount}, Quorum {len(self.sharedVar.hosts.keys())} reached {ackCount >= len(self.sharedVar.hosts.keys())}")
            if ackCount >= len(self.sharedVar.hosts.keys()):
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
        m = self.log.getMessage(seq)
        logging.debug(f"Deliver message {m}")
        response = self.inventory.processMessage(m["content"])
        self.log.commitMessage(message,response)
