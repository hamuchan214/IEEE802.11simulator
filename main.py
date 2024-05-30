import random

random.seed(123)

class User:
    def __init__(self, id, n=0):
        self.id = id
        self.n = n
        self.slots = 0
        self.transmitted = 0
        self.CW = self.calculate_CW()
        self.total_data_transmitted = 0

    def calculate_CW(self):
        slot_time = 9 * 10**(-6)
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

users = [User(id=i) for i in range(5)]

def transmission_time(data, rate):
    return data / rate

def simulate_transmission(users, duration):
    current_time = 0
    collision_count = 0
    data_transmission = 1500 # 1500bit
    transmission_rate = 12 * 10**6 # 12Mbps

    while current_time < duration:
        cw_times = [(user.id, user.CW) for user in users]
        cw_times.sort(key=lambda x: x[1])

        min_user_id, min_cw = cw_times[0]
        min_user = next(user for user in users if user.id == min_user_id)

        # 衝突チェック
        collisions = [user for user in users if user.CW == min_cw and user.id != min_user_id]

        if collisions:
            print([user.id for user in collisions])
            # ユーザーのCWを出力
            for user in users:
                print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

            trans_time = transmission_time(data_transmission, transmission_rate)
            if current_time + min_cw + trans_time <= duration:

                current_time += min_cw
                current_time += trans_time
                collision_count += 1

            else:
                current_time = duration
                collision_count += 1

            print(f"\nTime: {current_time}s - Collision detected! Users: {[user.id for user in collisions] + [min_user_id]}")

            for user in collisions + [min_user]:
                print(f"User {user.id} waited {user.slots} slots before collision.")
                user.re_transmit()

            print("")

        else:
            trans_time = transmission_time(data_transmission, transmission_rate)
            if current_time + trans_time <= duration:
                current_time += min_cw
                # print(f"\nTime: {current_time}s - User {min_user_id} transmitted successfully with CW = {min_cw:.6f} seconds (waited {min_user.slots} slots)")

                min_user.transmitted += 1
                min_user.total_data_transmitted += data_transmission
                current_time += trans_time

            else:
                remaining_time = duration - current_time
                current_time = duration

                data_transmitted = remaining_time * transmission_rate
                min_user.total_data_transmitted += data_transmitted
                min_user.transmitted += 1

                # print(f"\nTime: {current_time:.2f}s - User {min_user_id} partially transmitted {data_transmitted / 10**6} Mbit due to time limit")

            # 他のユーザーのCWとスロット待機時間から送信者のCWとスロット待機時間の差を計算して代入
            for user in users:
                if user.id != min_user_id:
                    user.CW -= min_user.CW
                    user.slots -= min_user.slots

            min_user.reset_CW()  # 送信成功後にCWをリセット

    # 各ユーザーの送信回数と送信データ量をプリント
    print("\nSimulation ended. Results:")
    for user in users:
        average_transmission_rate = user.total_data_transmitted / duration / 10**6 # 平均伝送速度 (Mbps)
        print(f"User {user.id} transmitted {user.transmitted} times, total data transmitted: {user.total_data_transmitted} bits, average transmission rate: {average_transmission_rate:.2f} Mbps")

    # 衝突回数をプリント
    print(f"Total collisions: {collision_count}")

if __name__ == "__main__":
    simulate_transmission(users, 120)