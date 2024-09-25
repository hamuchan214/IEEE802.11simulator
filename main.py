import random

# Slot time
SLOT_TIME = 9 * 10**(-6)

# Output modes
print_mode = {
    0: "Only Collision",
    1: "ALL",
    2: "No Output"
}


transmission_mode = {
    "a": {
        "SLOT_TIME": 9,
        "SIFS": 16,
        "DIFS": 34
    },

    "b": {
        "SLOT_TIME": 20,
        "SIFS": 10,
        "DIFS": 50
    },

    "g": {
        "SLOT_TIME": 9,
        "SIFS": 10,
        "DIFS": 28
    }
}


class User:
    # Initialization of User class
    def __init__(self, id, n=0, seed=None):
        if seed is not None:
            # Set random seed
            random.seed(seed + id)
        self.id = id
        self.n = n  # Number of retries (for CW extension)
        self.slots = 0  # Number of waiting slots
        self.transmitted = 0  # Number of successful transmissions
        self.CW = self.calculate_CW()  # Contention window
        self.total_data_transmitted = 0  # Total data transmitted

    # Calculate the Contention Window (CW)
    def calculate_CW(self):
        cw_max = 2**(4 + self.n) - 1  # Maximum value of CW
        self.slots = random.randint(1, min(cw_max, 1023))  # Limit number of slots to 1023
        return self.slots * SLOT_TIME

    # Update CW when retransmitting
    def re_transmit(self):
        self.n += 1
        self.CW = self.calculate_CW()

    # Reset CW after successful transmission
    def reset_CW(self):
        self.n = 0
        self.CW = self.calculate_CW()


# Function to create users
def create_users(num_users, seed):
    return [User(id=i, seed=seed) for i in range(num_users)]


# Calculate transmission time
def transmission_time(data, rate):
    return data / rate


# Transmission simulation
def simulate_transmission(users, duration, rate, print_output):
    current_time = 0
    collision_count = 0
    data_transmission = 1500 * 8  # Data size
    transmission_rate = rate * 10**6  # Transmission rate (Mbps)

    while current_time < duration:
        # Sort each user's CW and slot count
        cw_times = [(user.id, user.slots, user.CW) for user in users]
        cw_times.sort(key=lambda x: x[1])

        # Identify the user with the minimum slot
        min_user_id, min_slots, min_cw = cw_times[0]
        min_user = next(user for user in users if user.id == min_user_id)

        # Check for collisions
        collisions = [user for user in users if user.slots == min_slots and user.id != min_user_id]

        if collisions:
            collision_count += 1
            current_time += min_cw

            # Display CW of each user (based on output mode)
            if print_output == (print_mode[0] or print_mode[1]):
                for user in users:
                    print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

            # Calculate data transmission time
            trans_time = transmission_time(data_transmission, transmission_rate)
            if current_time + trans_time <= duration:
                current_time += trans_time
            else:
                current_time = duration

            # Display collided users (in collision mode)
            if print_output == print_mode[0]:
                collision_ids = [min_user_id] + sorted([user.id for user in collisions])
                print(f"\nTime: {current_time:.2f}s - Collision detected! Users: {collision_ids}")
                for user in collisions + [min_user]:
                    print(f"User {user.id} waited {user.slots} slots before collision.")
                print("")

            # Retransmit for all collided users
            for user in collisions + [min_user]:
                user.re_transmit()

        else:
            # Handle successful data transmission
            trans_time = transmission_time(data_transmission, transmission_rate)
            if current_time + trans_time <= duration:
                current_time += min_cw
                if print_output == print_mode[1]:
                    print(n)
                    n += 1
                    print(f"\nTime: {current_time}s - User {min_user_id} transmitted successfully with CW = {min_cw:.6f} seconds (waited {min_user.slots} slots)")

                    # ユーザーのCWを出力
                    for user in users:
                        print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

                min_user.transmitted += 1
                min_user.total_data_transmitted += data_transmission
                current_time += trans_time

            else:
                remaining_time = duration - current_time
                current_time = duration

                data_transmitted = remaining_time * transmission_rate
                min_user.total_data_transmitted += data_transmitted
                min_user.transmitted += 1

                # ユーザーのCWを出力
                for user in users:
                    print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

                if print_output == print_mode[1]:
                    print(f"\nTime: {current_time:.2f}s - User {min_user_id} partially transmitted {data_transmitted / 10**6} Mbit due to time limit")

            # Update CW and slots of other users
            for user in users:
                if user.id != min_user_id:
                    user.CW -= min_user.CW
                    user.slots -= min_user.slots

            # Reset CW after successful transmission
            min_user.reset_CW()

    # Display simulation results
    print("\nSimulation ended. Results:")
    for user in users:
        average_transmission_rate = user.total_data_transmitted / duration / 10**6  # 平均伝送速度 (Mbps)
        print(f"User {user.id} transmitted {user.transmitted} times, total data transmitted: {user.total_data_transmitted} bits, average transmission rate: {average_transmission_rate:.2f} Mbps")

    # Display total collisions
    print(f"Total collisions: {collision_count}")


if __name__ == "__main__":
    n = 3
    seed = 123
    # seed = random.randint(0, 1023)

    # Run simulation and display intermediate output
    users = create_users(n, seed)
    simulate_transmission(users, 120, 24, print_output=print_mode[2])

    print("\n" + "="*50 + "\n")

    # Run simulation and display only final results
    users = create_users(n, seed)
    simulate_transmission(users, 120, 24, print_output=print_mode[2])
