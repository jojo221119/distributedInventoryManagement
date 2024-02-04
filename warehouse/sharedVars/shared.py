import os

class Shared:
    def __init__(self):
        self.leader = ""
        self.hosts = {}
        self.ip = ""
        self.broadcastIP = ""
        self.pid = os.getpid()
        self.election_in_progress = False