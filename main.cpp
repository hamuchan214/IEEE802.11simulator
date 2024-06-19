#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define SLOT_TIME 9e-6                // スロット時間（秒）
#define DATA_TRANSMISSION 1500 * 8    // データ伝送量（ビット）
#define TRANSMISSION_RATE 12e6        // 伝送速度（ビット/秒）
#define DURATION 120                  // シミュレーションの持続時間（秒）
#define NUM_USERS 5                   // ユーザーの数
#define SEED 123                      // 乱数生成のシード

class User {
public:
    int id;                       // ユーザーID
    int n;                        // 再送回数
    int slots;                    // 待機スロット数
    int transmitted;              // 送信成功回数
    double CW;                    // コンテンダウィンドウ（秒）
    double total_data_transmitted;// 総送信データ量（ビット）

    User(int id) : id(id), n(0), transmitted(0), total_data_transmitted(0) {
        CW = calculate_CW();
    }

    double calculate_CW() {
        int cw_max = std::pow(2, 4 + n) - 1;
        slots = rand() % (cw_max < 1023 ? cw_max : 1023) + 1;
        return slots * SLOT_TIME;
    }

    void re_transmit() {
        n++;
        CW = calculate_CW();
    }

    void reset_CW() {
        n = 0;
        CW = calculate_CW();
    }
};
class Simulation {
private:
    std::vector<User> users;
    double duration;
    double transmission_rate;
    int collision_count;
    double current_time;

    double transmission_time(double data, double rate) {
        return data / rate;
    }

public:
    Simulation(int num_users, double duration, double rate) 
        : duration(duration), transmission_rate(rate), collision_count(0), current_time(0) {
        for (int i = 0; i < num_users; i++) {
            users.emplace_back(i);
        }
    }

    void simulate_transmission(int print_output) {
        while (current_time < duration) {
            int min_user_id = -1;
            int min_slots = 1024;
            double min_cw = 0;

            for (auto& user : users) {
                if (user.slots < min_slots) {
                    min_slots = user.slots;
                    min_cw = user.CW;
                    min_user_id = user.id;
                }
            }

            User& min_user = users[min_user_id];
            int collisions = 0;

            for (auto& user : users) {
                if (user.slots == min_slots && user.id != min_user_id) {
                    collisions++;
                }
            }

            if (collisions > 0) {
                collision_count++;
                current_time += min_cw;

                if (print_output == 0 || print_output == 1) {
                    for (auto& user : users) {
                        printf("User %d CW = %.6f seconds (waited %d slots)\n", user.id, user.CW, user.slots);
                    }
                }

                double trans_time = transmission_time(DATA_TRANSMISSION, transmission_rate);
                if (current_time + trans_time <= duration) {
                    current_time += trans_time;
                } else {
                    current_time = duration;
                }

                if (print_output == 0) {
                    printf("\nTime: %.2fs - Collision detected! Users: %d", current_time, min_user_id);
                    for (auto& user : users) {
                        if (user.slots == min_slots && user.id != min_user_id) {
                            printf(", %d", user.id);
                        }
                    }
                    printf("\n");
                    for (auto& user : users) {
                        if (user.slots == min_slots || user.id == min_user_id) {
                            printf("User %d waited %d slots before collision.\n", user.id, user.slots);
                        }
                    }
                    printf("\n");
                }

                for (auto& user : users) {
                    if (user.slots == min_slots || user.id == min_user_id) {
                        user.re_transmit();
                    }
                }

            } else {
                double trans_time = transmission_time(DATA_TRANSMISSION, transmission_rate);
                if (current_time + trans_time <= duration) {
                    current_time += min_cw;
                    if (print_output == 1) {
                        printf("\nTime: %.2fs - User %d transmitted successfully with CW = %.6f seconds (waited %d slots)\n",
                               current_time, min_user_id, min_cw, min_user.slots);
                    }
                    min_user.transmitted++;
                    min_user.total_data_transmitted += DATA_TRANSMISSION;
                    current_time += trans_time;
                } else {
                    double remaining_time = duration - current_time;
                    current_time = duration;
                    double data_transmitted = remaining_time * transmission_rate;
                    min_user.total_data_transmitted += data_transmitted;
                    min_user.transmitted++;
                    if (print_output == 1) {
                        printf("\nTime: %.2fs - User %d partially transmitted %.2f Mbit due to time limit\n",
                               current_time, min_user_id, data_transmitted / 1e6);
                    }
                }

                for (auto& user : users) {
                    if (user.id != min_user_id) {
                        user.CW -= min_user.CW;
                        user.slots -= min_user.slots;
                    }
                }

                min_user.reset_CW();
            }
        }

        printf("\nSimulation ended. Results:\n");
        for (auto& user : users) {
            double average_transmission_rate = user.total_data_transmitted / duration / 1e6;
            printf("User %d transmitted %d times, total data transmitted: %.2f bits, average transmission rate: %.2f Mbps\n",
                   user.id, user.transmitted, user.total_data_transmitted, average_transmission_rate);
        }

        printf("Total collisions: %d\n", collision_count);
    }
};

int main() {
    srand(SEED);

    Simulation sim1(NUM_USERS, DURATION, TRANSMISSION_RATE);
    sim1.simulate_transmission(2);

    printf("\n==================================================\n");

    Simulation sim2(NUM_USERS, DURATION, TRANSMISSION_RATE);
    sim2.simulate_transmission(2);

    return 0;
}