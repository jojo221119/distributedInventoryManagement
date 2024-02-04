import logging
import queue
import uuid
from networking.ddoh import Networking
from warehouse.reliableMulticast.multicast import ReliableMulticaster


def main():
    logging.debug("hello World")
    net = Networking()
    delivery_queue = queue.Queue()

    id = str(uuid.uuid4())
    leaderId = "????"
    groupSize = "????"
    multicast = ReliableMulticaster(multicastGroupIp='224.0.0.1', port=10000, id=id, leaderId=leaderId, groupSize=groupSize, deliveryQueue=delivery_queue)



if __name__ == '__main__':
    main()
