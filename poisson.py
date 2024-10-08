import random
import numpy as np

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
    def __init__(self, id, n=0, seed=None):
        if seed is not None:
            random.seed(seed + id)
        self.id = id
        self.n = n
        self.slots = 0
        self.transmitted = 0
        self.CW = self.calculate_CW()
        self.total_data_transmitted = 0
        self.next_packet_time = self.generate_next_packet_time()
        print(self.next_packet_time)

    def calculate_CW(self):
        slot_time = 9 * 10**(-6)  # スロットタイム
        cw_max = 2**(4 + self.n) - 1
        slots = random.randint(1, min(cw_max, 1023))
        self.slots = slots
        return slots * slot_time

    def re_transmit(self):
        self.n += 1
        self.CW = self.calculate_CW()

    def reset_CW(self):
        self.n = 0
        self.CW = self.calculate_CW()

    def generate_next_packet_time(self, lam=1):
        # ポアソン分布に基づく次のパケット生成時間を生成
        return np.random.poisson(lam)

def create_users(num_users, seed):
    return [User(id=i, seed=seed) for i in range(num_users)]

def transmission_time(data, rate):
    return data / rate

def simulate_transmission(users, duration, rate, print_output, lam=1):
    current_time = 0
    collision_count = 0
    data_transmission = 1500 * 8  # 1500 bytes to bits
    transmission_rate = rate * 10**6  # rate Mbps

    while current_time < duration:
        # 次のパケット生成時間が現在の時間以下のユーザーのみ対象
        active_users = [user for user in users if user.next_packet_time <= current_time]

        if not active_users:
            # 次のイベントまで進む
            next_event_time = min(user.next_packet_time for user in users)
            current_time = next_event_time
            continue

        cw_times = [(user.id, user.slots, user.CW) for user in active_users]
        cw_times.sort(key=lambda x: x[1])

        min_user_id, min_slots, min_cw = cw_times[0]
        min_user = next(user for user in active_users if user.id == min_user_id)

        # 衝突チェック
        collisions = [user for user in active_users if user.slots == min_slots and user.id != min_user_id]

        if collisions:
            collision_count += 1
            current_time += min_cw  # 修正: 衝突時のスロットタイムを追加

            if print_output == (print_mode[0] or print_mode[1]):
                for user in active_users:
                    print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

            trans_time = transmission_time(data_transmission, transmission_rate)
            if current_time + trans_time <= duration:
                current_time += trans_time
            else:
                current_time = duration

            if print_output == print_mode[0]:
                collision_ids = [min_user_id] + sorted([user.id for user in collisions])
                print(f"\nTime: {current_time:.2f}s - Collision detected! Users: {collision_ids}")

                for user in collisions + [min_user]:
                    print(f"User {user.id} waited {user.slots} slots before collision.")
                print("")

            for user in collisions + [min_user]:
                if user.slots == min_user.slots:
                    user.re_transmit()
                else:
                    user.CW -= min_user.CW
                    user.slots -= min_user.slots
                user.next_packet_time = current_time + user.generate_next_packet_time(lam)

        else:
            trans_time = transmission_time(data_transmission, transmission_rate)
            if current_time + trans_time <= duration:
                current_time += min_cw
                if print_output == print_mode[1]:
                    print(f"\nTime: {current_time}s - User {min_user_id} transmitted successfully with CW = {min_cw:.6f} seconds (waited {min_user.slots} slots)")

                    for user in active_users:
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

                for user in active_users:
                    print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

                if print_output == print_mode[1]:
                    print(f"\nTime: {current_time:.2f}s - User {min_user_id} partially transmitted {data_transmitted / 10**6} Mbit due to time limit")

            for user in active_users:
                if user.id != min_user_id:
                    user.CW -= min_user.CW
                    user.slots -= min_user.slots

            min_user.reset_CW()
            min_user.next_packet_time = current_time + min_user.generate_next_packet_time(lam)

    print("\nSimulation ended. Results:")
    for user in users:
        average_transmission_rate = user.total_data_transmitted / duration / 10**6  # 平均伝送速度 (Mbps)
        print(f"User {user.id} transmitted {user.transmitted} times, total data transmitted: {user.total_data_transmitted} bits, average transmission rate: {average_transmission_rate:.2f} Mbps")

    print(f"Total collisions: {collision_count}")

if __name__ == "__main__":
    n = 3
    seed = random.randint(0, 1023)

    users = create_users(n, seed)
    simulate_transmission(users, 120, 12, print_output=print_mode[2], lam=1)

    print("\n" + "="*50 + "\n")

    users = create_users(n, seed)
    simulate_transmission(users, 120, 24, print_output=print_mode[2], lam=0.001)
