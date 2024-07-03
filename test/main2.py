import random

print_mode = {
        0 : "Only Collision",
        1 : "ALL",
        2 : "No Output"
}

class User:
    def __init__(self, id, n=0, seed=None):
        if seed is not None:
            random.seed(seed+id)
        
        self.id = id
        self.n = n
        self.slots = self.calc_slots()
        self.num_transmitted = 0
        self.total_data_transmitted = 0
    
    def calc_slots(self):
        cw_max = 2 ** (4 + self.n) - 1
        self.slots = random.randint(1, min(cw_max, 1023))
    
    def re_transmit(self):
        self.n += 1
        self.slots = self.calc_slots()
    
    def reset_slots(self):
        self.n = 0
        self.slots = self.calc_slots()


def create_users(num_users, seed):
    return [User(id=i, seed=seed) for i in range(num_users)]

def transmission_time(data, rate):
    return data / rate


        