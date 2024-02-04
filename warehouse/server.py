from datetime import datetime, timedelta
import logging
import os
import pickle
import queue
import random
import socket
import threading
from time import sleep

from flask import Flask
from flask_restful import Api


from serverLogic.inventory import Inventory
from serverLogic.item import Item
from networking.ddoh import Networking
from sharedVars.shared import Shared
from heartbeat.heartbeat import HeartBeat
from reliableMulticast.multicast import ReliableMulticaster
from leaderElection.election import BullyAlgorithm

# Configure the logging settings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("hello World")

    sharedVar = Shared()


    net = Networking(sharedVar)
    sharedVar.ip = net.ip
    sharedVar.broadcastIP = net.broadcastIp

    heartBeat = HeartBeat(sharedVar)
    heartBeatListener = threading.Thread(target=heartBeat.receive)
    heartBeatSender = threading.Thread(target=heartBeat.send_heartbeat)
    
    ddoh_listener_thread = threading.Thread(target=net.respond_to_discovery)

    election = BullyAlgorithm(sharedVar)
    election_listener_thread = threading.Thread(target=election.election_listener)

    heartBeatListener.start()
    heartBeatSender.start()
    ddoh_listener_thread.start()
    election_listener_thread.start()


    # Discover hosts in the network
    sharedVar.leader = net.discover_hosts()   


    delivery_queue = queue.Queue()

        
    leaderId = "????"
    groupSize = "????"
    multicast = ReliableMulticaster(multicastGroupIp='224.0.0.1', port=10000, id=id, leaderId=leaderId, groupSize=groupSize, deliveryQueue=delivery_queue)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 12347))

    server_socket.listen()

    inventory = Inventory()

    t = datetime.now()
    while True:
        
        if t < datetime.now()-timedelta(seconds=5):
            logging.debug(f"State IP: {sharedVar.ip} leader: {sharedVar.leader} election: {sharedVar.election_in_progress} hosts: {sharedVar.hosts.keys()}")
            t = datetime.now()
        

        if sharedVar.leader not in sharedVar.hosts.keys() and not sharedVar.election_in_progress:
            election.start_election()

#        client_socket, client_address = server_socket.accept()
#        data = client_socket.recv(1024)
#        message = pickle.loads(data)
#        if message["type"] == "newItem":
#            inventory.addItem(message["name"],message["description"])     
#        elif message["type"] == "getItems":
#            inventory.getItems()
#        elif message["type"] == "putItem":
#            inventory.putItem(message["itemId"],message["ammount"])
#        elif message["type"] == "takeItem":
#            inventory.takeItem(message["itemId"],message["ammount"])
#        else:
#            logging.info(f"No message type matched")
    
    heartBeatListener.join()
    heartBeatSender.join()
    ddoh_listener_thread.join()
    election_listener_thread.join()





if __name__ == '__main__':
    main()
