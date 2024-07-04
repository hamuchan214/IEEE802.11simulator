import random

print_mode = {
        0 : "Only Collision",
        1 : "ALL",
        2 : "No Output"
}

transmission_mode = {
    "a" : {
        "SLOT_TIME" : 9,
        "SIFS" : 16,
        "DIFS" : 34
    },

    "b" : {
        "SLOT_TIME" : 20,
        "SIFS" : 10,
        "DIFS" : 50
    },

    "g" : {
        "SLOT_TIME" : 9,
        "SIFS" : 10,
        "DIFS" : 28
    }
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

def simulate_transmission(users, duration, rate, print_output, mode):
    current_time = 0
    collision_count = 0
    transed_data = 1500 * 8
    trans_rate = rate * 10**6
    n = 0
    
    while current_time < duration:
        cw_times = [(user.id, user.slots) for user in users]
        cw_times.sort(key=lambda x: x[1])
        
        min_user_id, min_slots = cw_times[0]
        
        # collision check
        collisions = [user.id for user in users if user.slots == min_slots and user.id != min_user_id]
        
        if collisions:
            collision_count += 1
            current_time 