from datetime import datetime, timedelta
import logging
import pickle
import selectors
import socket
import threading


from serverLogic.inventory import Inventory
from networking.ddoh import Networking
from sharedVars.shared import Shared
from heartbeat.heartbeat import HeartBeat
from reliableMulticast.multicast import ReliableMulticaster
from leaderElection.election import BullyAlgorithm


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

    logging.debug(f"{sharedVar.broadcastIP}")

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
    server_socket.setblocking(False)

    sel = selectors.DefaultSelector()
    sel.register(server_socket, selectors.EVENT_READ, data=None)

    t = datetime.now()
    logging.info("Start Main")
    logging.debug(f"State IP: {sharedVar.ip} leader: {sharedVar.leader} election: {sharedVar.election_in_progress} seq: {multicast.seq} hosts: {list(sharedVar.hosts.keys())}")
    while True:
        
        if t < datetime.now()-timedelta(seconds=5):
            logging.debug(f"State IP: {sharedVar.ip} leader: {sharedVar.leader} election: {sharedVar.election_in_progress} seq: {multicast.seq} hosts: {list(sharedVar.hosts.keys())}")
            t = datetime.now()
        

        if sharedVar.leader not in sharedVar.hosts.keys() and not sharedVar.election_in_progress:
            election.start_election()
        
        while sharedVar.election_in_progress:
            i = 1
        

        events = sel.select(timeout=0)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                data, address = server_socket.recvfrom(1024)
                message = pickle.loads(data)
                if sharedVar.leader == sharedVar.ip:
                    response = multicast.sendMessage(message)
                else:
                    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    udp_socket.bind(('', 0))
                    leader_address = (sharedVar.leader, 12347)
                    logging.debug(f"Forward message to leader")
                    udp_socket.sendto(pickle.dumps(message), leader_address)

                    r, _ = udp_socket.recvfrom(1024)
                    response = pickle.loads(r)

                logging.debug(f"Response {response}")
                server_socket.sendto(pickle.dumps(response), address)


    heartBeatListener.join()
    heartBeatSender.join()
    ddoh_listener_thread.join()
    election_listener_thread.join()





if __name__ == '__main__':
    main()
