

class Memory:
    def __init__(self):
        self.memory = []
        self.limit = 20

    def get_memory(self):
        return self.memory
    
    def add(self, message):
        self.memory.append(message)
        if len(self.memory) > self.limit:
            self.memory = self.memory[-self.limit:]