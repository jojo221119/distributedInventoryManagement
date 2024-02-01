from operator import le
import queue
import random
import sys
import threading
from time import sleep
import uuid
from networking.ddoh import Networking
from sharedVars.shared import Shared



def main():
    print("hello World")

    sharedVar = Shared()

#    if len(sys.argv) > 1 and sys.argv[1] == "leader":
#        sharedVar.leader = True
#    else:
#        leader = False



    net = Networking(sharedVar)
    response_thread = threading.Thread(target=net.respond_to_discovery)
    response_thread.start()

    sleep(random.randint(0, 10))

    # Discover hosts in the network
    sharedVar.leader = net.discover_hosts()

    print(f"Net {net.sharedVar.leader}")
    


    while True:
        print(f"Shared {sharedVar.leader}")
        sleep(10)

    
    response_thread.join()


#        delivery_queue = queue.Queue()

#        id = str(uuid.uuid4())
#        leaderId = "????"
#        groupSize = "????"
#        multicast = ReliableMulticaster(multicastGroupIp='224.0.0.1', port=10000, id=id, leaderId=leaderId, groupSize=groupSize, deliveryQueue=delivery_queue)

        



if __name__ == '__main__':
    main()
