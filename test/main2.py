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

def transmis_time(data, rate):
    return data / rate

def calc_cw(slots, mode):
    return slots * transmission_mode[mode]["SLOT_TIME"] * 10**(-6)

def simulate_transmission(users, duration, rate, print_output, trans_mode):
    current_time = 0
    collision_count = 0
    transed_data = 1500 * 8
    trans_rate = rate * 10**6
    n = 0
    
    while current_time < duration:
        cw_time = [(user.id, user.slots) for user in users]
        cw_time.sort(key=lambda x: x[1])
        
        min_user_id, min_slots = cw_time[0]
        min_user = next(user for user in users if user.id == min_user_id)
        
        collisions = [user for user in users if user.slots == min_slots and user.id != min_user_id]
        
        trans_time = transmis_time(transed_data, trans_rate)
        cw = calc_cw(min_slots, trans_mode)
        
        # 衝突
        if collisions:
            collision_count += 1
            
            if (current_time + cw + trans_time) < duration:
                current_time += trans_time
                
                if print_output == (print_mode[0] or print_mode[1]):
                    print(n)
                    n += 1
                    
                    collision_ids = [min_user_id] + sorted([user.id for user in collisions])
                    print(f"\nTime: {current_time:.2f}s - Collision detected! Users: {collision_ids}")
                    
                    for user in [min_user] + collisions:
                        print(f"User {user.id} waited {user.slots} slots before collision.")
                    print("")
                
                for user in users:
                    if user.slots == min_slots:
                        user.re_transmit()
                    
                    else:
                        user.slots -= min_slots
            
            else:
                current_time = duration
        
        # 成功
        else:
            if (current_time + cw) < duration:
                current_time += cw
                

            else:
                current_time = duration