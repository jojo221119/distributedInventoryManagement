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

    inventory = Inventory()
    multicast = ReliableMulticaster(multicastGroupIp='224.0.0.1', port=10000, sharedVar=sharedVar, inventory=inventory)
    multicastListener = threading.Thread(target=multicast.start, daemon=True)


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
    multicastListener.start()


    # Discover hosts in the network
    sharedVar.leader = net.discover_hosts()   





    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', 12347))


    t = datetime.now()
    logging.info("Start Main")
    logging.debug(f"State IP: {sharedVar.ip} leader: {sharedVar.leader} election: {sharedVar.election_in_progress} hosts: {sharedVar.hosts.keys()}")
    logging.debug(f"Inventory {inventory}")
    while True:
        
        if t < datetime.now()-timedelta(seconds=5):
            logging.debug(f"State IP: {sharedVar.ip} leader: {sharedVar.leader} election: {sharedVar.election_in_progress} hosts: {sharedVar.hosts.keys()}")
            logging.debug(f"Inventory {inventory}")
            t = datetime.now()
        

        if sharedVar.leader not in sharedVar.hosts.keys() and not sharedVar.election_in_progress:
            election.start_election()


        data, address = server_socket.recvfrom(1024)
        message = pickle.loads(data)
        if sharedVar.leader == sharedVar.ip:
            response = multicast.sendMessage(message)
            logging.debug(f"Response {response}")
            server_socket.sendto(pickle.dumps(response), address) 


    heartBeatListener.join()
    heartBeatSender.join()
    ddoh_listener_thread.join()
    election_listener_thread.join()





if __name__ == '__main__':
    main()
