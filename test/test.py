import random
import time
import tkinter as tk
from tkinter import messagebox

class User:
    def __init__(self, id, n=0):
        self.id = id
        self.n = n
        self.slots_waited = 0
        self.transmissions = 0
        self.CW = self.calculate_CW()
    
    def calculate_CW(self):
        slot_time = 9 * 10**(-6)  # スロットタイム
        cw_max = 2**(4 + self.n) - 1
        slots = random.randint(0, cw_max)
        self.slots_waited = slots
        return slot_time * slots
    
    def wait_for_CW(self):
        time.sleep(self.CW)
    
    def reset_CW(self):
        self.n += 1
        self.CW = self.calculate_CW()

# ユーザーを生成
users = [User(id=i) for i in range(5)]

def simulate_transmission(users, duration=5):
    start_time = time.time()
    collision_count = 0
    
    while time.time() - start_time < duration:
        cw_times = [(user.id, user.CW) for user in users]
        cw_times.sort(key=lambda x: x[1])
        
        # 最小CWのユーザーが送信を試みる
        min_user_id, min_cw = cw_times[0]
        min_user = next(user for user in users if user.id == min_user_id)
        
        # 衝突をチェック
        collisions = [user for user in users if user.CW == min_cw and user.id != min_user_id]
        if collisions:
            print(f"Collision detected! Users: {[user.id for user in collisions] + [min_user_id]}")
            collision_count += 1
            for user in collisions + [min_user]:
                print(f"User {user.id} waited {user.slots_waited} slots before collision.")
                user.reset_CW()
        else:
            print(f"User {min_user_id} transmitted successfully with CW = {min_cw:.6f} seconds (waited {min_user.slots_waited} slots)")
            min_user.transmissions += 1
            
            # 他のユーザーのCWから送信者のCWの差を計算して代入
            for user in users:
                if user.id != min_user_id:
                    user.CW -= min_user.CW
            min_user.CW = 0  # 送信成功後にCWをリセット
        
        # 他のユーザーのCWを出力
        for user in users:
            if user.id != min_user_id:
                print(f"User {user.id} CW = {user.CW:.6f} seconds (waited {user.slots_waited} slots)")
        
        # 再度CWを計算して次のサイクルへ
        for user in users:
            if user.CW <= 0:
                user.CW = user.calculate_CW()
    
    # 各ユーザーの送信回数をプリント
    for user in users:
        print(f"User {user.id} transmitted {user.transmissions} times")
    
    # 衝突回数をプリント
    print(f"Total collisions: {collision_count}")

# シミュレーション開始
overall_start_time = time.time()
simulate_transmission(users)
overall_end_time = time.time()

# 全体の実行時間を計算
total_duration = overall_end_time - overall_start_time
print(f"Total simulation time: {total_duration:.6f} seconds")

# ポップアップで実行時間を表示
root = tk.Tk()
root.withdraw()
messagebox.showinfo("Simulation Time", f"Total simulation time: {total_duration:.6f} seconds")
root.destroy()
