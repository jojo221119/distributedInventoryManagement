class Shared:
    def __init__(self):
        self.leader = None
        self.hosts = []

    def getLeader(self):
        return self.leader
    
    def setLeader(self, leader):
        self.leader = leader
    
    def getHosts(self):
        return self.hosts
    
    def setHosts(self, hosts):
        self.hosts = hosts