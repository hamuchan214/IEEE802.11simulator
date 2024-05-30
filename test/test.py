import random

class User:
    def __init__(self, id, n=0):
        self.id = id
        self.n = n
        self.slots_waited = 0
        self.transmissions = 0
        self.CW = self.calculate_CW()
        self.total_data_transmitted = 0  # 送信されたデータの総量
    
    def calculate_CW(self):
        slot_time = 9 * 10**(-6)  # スロットタイム
        cw_max = 2**(4 + self.n) - 1
        slots = random.randint(0, cw_max)
        if slots > 1023:
            slots = 1023
        self.slots_waited = slots
        return slot_time * slots

    def reset_CW(self):
        self.n += 1
        self.CW = self.calculate_CW()

# ユーザーを生成
users = [User(id=i) for i in range(5)]

def simulate_transmission(users, duration=120):
    current_time = 0
    collision_count = 0
    data_per_transmission = 1500  # 1500bit
    transmission_rate = 12 * 10**6  # 12Mbps
    
    while current_time < duration:
        cw_times = [(user.id, user.CW) for user in users]
        cw_times.sort(key=lambda x: x[1])
        
        # 最小CWのユーザーが送信を試みる
        min_user_id, min_cw = cw_times[0]
        min_user = next(user for user in users if user.id == min_user_id)
        
        # 他のユーザーのCWを出力
        for user in users:
            if user.id != min_user_id:
                print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots_waited} slots)")
        
        # 衝突をチェック
        collisions = [user for user in users if user.CW == min_cw and user.id != min_user_id]
        if collisions:
            print(f"\nTime: {current_time:.2f}s - Collision detected! Users: {[user.id for user in collisions] + [min_user_id]}")
            collision_count += 1
            for user in collisions + [min_user]:
                print(f"User {user.id} waited {user.slots_waited} slots before collision.")
                user.reset_CW()
        else:
            transmission_time = data_per_transmission / transmission_rate  # 送信時間を計算
            if current_time + transmission_time <= duration:  # 残り時間内に送信可能かをチェック
                print(f"\nTime: {current_time:.2f}s - User {min_user_id} transmitted successfully with CW = {min_cw:.6f} seconds (waited {min_user.slots_waited} slots)")
                min_user.transmissions += 1
                min_user.total_data_transmitted += data_per_transmission  # 送信データ量を追加
                current_time += transmission_time  # 経過時間を送信時間分だけ進める
            else:
                # 時間を超えてしまう場合の処理
                remaining_time = duration - current_time
                data_transmitted = remaining_time * transmission_rate
                min_user.total_data_transmitted += data_transmitted  # 送信データ量を追加
                current_time = duration  # 経過時間をdurationに設定
                print(f"\nTime: {current_time:.2f}s - User {min_user_id} partially transmitted {data_transmitted / 10**6} Mbit due to time limit")
            
            # 他のユーザーのCWとスロット待機時間から送信者のCWとスロット待機時間の差を計算して代入
            for user in users:
                if user.id != min_user_id:
                    user.CW -= min_user.CW
                    user.slots_waited -= min_user.slots_waited
            min_user.CW = 0  # 送信成功後にCWをリセット
        
        # 再度CWを計算して次のサイクルへ
        for user in users:
            if user.CW <= 0:
                user.CW = user.calculate_CW()

    # 各ユーザーの送信回数と送信データ量をプリント
    print("\nSimulation ended. Results:")
    for user in users:
        average_transmission_rate = user.total_data_transmitted / duration / 10**6 # 平均伝送速度 (Mbps)
        print(f"User {user.id} transmitted {user.transmissions} times, total data transmitted: {user.total_data_transmitted} bits, average transmission rate: {average_transmission_rate:.2f} Mbps")
    
    # 衝突回数をプリント
    print(f"Total collisions: {collision_count}")

# シミュレーション開始
simulate_transmission(users)
