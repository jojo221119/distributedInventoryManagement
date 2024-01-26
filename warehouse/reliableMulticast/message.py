class Message(dict):
    def __init__(self, seq, sender, type, content=""):
        dict.__init__(self, seq = seq, sender = sender, content = content, type = type)
