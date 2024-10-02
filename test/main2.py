import random

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
        # if seed is not None:
        #     random.seed(seed+id)

        self.id = id
        self.n = n
        self.slots = self.calc_slots()
        self.num_transmitted = 0
        self.total_data_transmitted = 0

    def calc_slots(self):
        cw_max = 2 ** (4 + self.n) - 1
        self.slots = random.randint(1, min(cw_max, 1023))
        return self.slots

    def re_transmit(self):
        self.n += 1
        self.slots = self.calc_slots()

    def reset_slots(self):
        self.n = 0
        self.slots = self.calc_slots()


def create_users(num_users, seed=None):
    return [User(id=i, seed=seed) for i in range(num_users)]


def trans_time(data, rate):
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

        # print(cw_time[0])

        min_user_id, min_user_slots = cw_time[0]
        min_user = next(user for user in users if user.id == min_user_id)

        collisions = [user for user in users if user.slots == min_user_slots]
        collision_ids = sorted([user.id for user in collisions])

        trans_time = trans_time(transed_data, trans_rate)
        cw = calc_cw(min_user_slots, trans_mode)

        # 衝突
        if collisions:
            collision_count += 1

            if (current_time + cw + trans_time) < duration:
                current_time += (cw + trans_time)
                # ここにDIFSを足す

                if print_output == (print_mode[0] or print_mode[1]):
                    print(n)
                    n += 1

                    print(f"\nTime: {current_time:.2f}s - Collision detected! Users: {collision_ids}")

                    for user in [min_user] + collisions:
                        print(f"User {user.id} waited {user.slots} slots before collision.")

                    if print_output == print_mode[1]:
                        print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

                for user in users:
                    if user.id in collision_ids:
                        user.re_transmit()

                    else:
                        user.slots -= min_user_slots

            else:
                current_time = duration

        # 成功
        else:
            # これいらない
            if (current_time + cw + trans_time) < duration:

                if print_output == print_mode[1]:
                    print(n)
                    n += 1
                    print(
                        f"\nTime: {current_time}s - User {min_user_id} transmitted successfully with CW = {cw:.6f} seconds (waited {min_user.slots} slots)")

                    # ユーザーのCWを出力
                    for user in users:
                        print(
                            f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

                min_user.num_transmitted += 1
                min_user.total_data_transmitted += transed_data
                current_time += (cw + trans_time)
                # ここにSIFS+ACK+DIFSを足す

                for user in users:
                    if user.id == min_user.id:
                        user.reset_slots()

                    else:
                        user.slots -= min_user_slots

            else:
                if (current_time + cw) > duration:
                    current_time = duration

                else:
                    if print_output == print_mode[1]:
                        print(n)

                        current_time += cw
                        remaining_time = duration - current_time

                        min_user.total_data_transmitted += remaining_time * trans_rate

                        print(f"\nTime: {current_time}s - User {min_user_id} transmitted successfully with CW ={cw:.6f} seconds (waited {min_user.slots} slots)")

                        # ユーザーのCWを出力
                        for user in users:
                            print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots} slots)")

                        current_time = duration

    # 各ユーザーの送信回数と送信データ量をプリント
    print("\nSimulation ended. Results:")
    for user in users:
        average_transmission_rate = user.total_data_transmitted / \
            current_time / 10**6  # 平均伝送速度 (Mbps)
        print(f"User {user.id} transmitted {user.transmitted} times, total data transmitted: {user.total_data_transmitted} bits, average transmission rate: {average_transmission_rate:.2f} Mbps")

    # 衝突回数をプリント
    print(f"Total collisions: {collision_count}")


if __name__ == "__main__":
    n = 3
    # seed = 123
    # seed = random.randint(0, 1023)

    # シミュレーションを実行し、途中の出力も表示する
    users = create_users(n)  # ユーザーリストを初期化
    simulate_transmission(
        users, 1, 12, print_output=print_mode[0], trans_mode="g")

    print("\n" + "="*50 + "\n")

    # シミュレーションを実行し、結果のみ表示する
    # users = create_users(n, seed)  # ユーザーリストを初期化
    # simulate_transmission(users, 10, 24, print_output=print_mode[2], trans_mode="g")
