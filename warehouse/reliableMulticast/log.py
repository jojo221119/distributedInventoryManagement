class Log:
    def __init__(self):
        self.log = {}
    
    def addMessage(self, message):
        entry = {
            "message": message,
            "commit": False,
            "acknowledgedBy": []
        }
        self.log[message["seq"]] = entry
    
    def commitMessage(self, message):
        self.log[message["seq"]]["commit"] = True
    
    def acknowledgeMessage(self, message):
        sender = message["sender"]
        if sender not in self.log[message["seq"]]["acknowledgedBy"]:
            self.log[message["seq"]]["acknowledgedBy"].append(sender)
        return len(self.log[message["seq"]]["acknowledgedBy"])
    
    def getAckCount(self, message):
        return len(self.log[message["seq"]]["acknowledgedBy"])

    def messageInLog(self, message):
        return message["seq"] in self.log.keys()
    
    def getMessage(self, seq):
        if seq in self.log.keys():
            return self.log[seq]["message"]
        else:
            return {}
    def isMessageCommited(self,message):
        return self.log[message["seq"]]["commit"]