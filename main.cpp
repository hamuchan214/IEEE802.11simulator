#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <ctime>
#include <cmath>

using namespace std;

enum PrintMode {
    OnlyCollision,
    All,
    NoOutput
};

struct TransmissionMode {
    int SLOT_TIME;
    int SIFS;
    int DIFS;
};

class User {
public:
    int id;
    int n;
    int slots;
    int transmitted;
    double CW;
    double total_data_transmitted;

    User(int id, int n = 0, int seed = -1) : id(id), n(n), slots(0), transmitted(0), total_data_transmitted(0.0) {
        if (seed != -1) {
            srand(seed + id);
        }
        CW = calculate_CW();
    }

    double calculate_CW() {
        double slot_time = 9e-6;  // スロットタイム
        int cw_max = pow(2, 4 + n) - 1;
        slots = rand() % min(cw_max, 1023) + 1;
        return slots * slot_time;
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

vector<User> create_users(int num_users, int seed) {
    vector<User> users;
    for (int i = 0; i < num_users; ++i) {
        users.emplace_back(i, 0, seed);
    }
    return users;
}

double transmission_time(int data, double rate) {
    return data / rate;
}

void simulate_transmission(vector<User>& users, double duration, double rate, PrintMode print_output) {
    double current_time = 0.0;
    int collision_count = 0;
    int data_transmission = 1500 * 8;  // 1500 bytes to bits
    double transmission_rate = rate * 1e6;  // rate in Mbps

    while (current_time < duration) {
        vector<tuple<int, int, double>> cw_times;
        for (auto& user : users) {
            cw_times.emplace_back(user.id, user.slots, user.CW);
        }
        sort(cw_times.begin(), cw_times.end(), [](const auto& a, const auto& b) {
            return get<1>(a) < get<1>(b);
        });

        int min_user_id = get<0>(cw_times[0]);
        int min_slots = get<1>(cw_times[0]);
        double min_cw = get<2>(cw_times[0]);
        User* min_user = &users[min_user_id];

        vector<User*> collisions;
        for (auto& user : users) {
            if (user.slots == min_slots && user.id != min_user_id) {
                collisions.push_back(&user);
            }
        }

        if (!collisions.empty()) {
            collision_count++;
            current_time += min_cw;

            if (print_output == OnlyCollision || print_output == All) {
                for (auto& user : users) {
                    cout << "User " << user.id << " CW = " << user.CW << " seconds (waited " << user.slots << " slots)\n";
                }
            }

            double trans_time = transmission_time(data_transmission, transmission_rate);
            if (current_time + trans_time <= duration) {
                current_time += trans_time;
            } else {
                current_time = duration;
            }

            if (print_output == OnlyCollision) {
                vector<int> collision_ids = {min_user_id};
                for (auto& user : collisions) {
                    collision_ids.push_back(user->id);
                }
                sort(collision_ids.begin(), collision_ids.end());

                cout << "\nTime: " << current_time << "s - Collision detected! Users: ";
                for (int id : collision_ids) {
                    cout << id << " ";
                }
                cout << "\n";
                for (auto& user : collisions) {
                    cout << "User " << user->id << " waited " << user->slots << " slots before collision.\n";
                }
                cout << "\n";
            }

            for (auto& user : collisions) {
                if (user->slots == min_user->slots) {
                    user->re_transmit();
                } else {
                    user->slots -= min_user->slots;
                }
            }
            min_user->re_transmit();
        } else {
            double trans_time = transmission_time(data_transmission, transmission_rate);
            if (current_time + trans_time <= duration) {
                current_time += min_cw;
                if (print_output == All) {
                    cout << "\nTime: " << current_time << "s - User " << min_user_id << " transmitted successfully with CW = " << min_cw << " seconds (waited " << min_user->slots << " slots)\n";
                    for (auto& user : users) {
                        cout << "User " << user.id << " CW = " << user.CW << " seconds (waited " << user.slots << " slots)\n";
                    }
                }
                min_user->transmitted++;
                min_user->total_data_transmitted += data_transmission;
                current_time += trans_time;
            } else {
                double remaining_time = duration - current_time;
                current_time = duration;

                double data_transmitted = remaining_time * transmission_rate;
                min_user->total_data_transmitted += data_transmitted;
                min_user->transmitted++;

                for (auto& user : users) {
                    cout << "User " << user.id << " CW = " << user.CW << " seconds (waited " << user.slots << " slots)\n";
                }
                if (print_output == All) {
                    cout << "\nTime: " << current_time << "s - User " << min_user_id << " partially transmitted " << data_transmitted / 1e6 << " Mbit due to time limit\n";
                }
            }

            for (auto& user : users) {
                if (user.id != min_user_id) {
                    user.CW -= min_user->CW;
                    user.slots -= min_user->slots;
                }
            }
            min_user->reset_CW();
        }
    }

    cout << "\nSimulation ended. Results:\n";
    for (auto& user : users) {
        double average_transmission_rate = user.total_data_transmitted / duration / 1e6;  // 平均伝送速度 (Mbps)
        cout << "User " << user.id << " transmitted " << user.transmitted << " times, total data transmitted: " << user.total_data_transmitted << " bits, average transmission rate: " << average_transmission_rate << " Mbps\n";
    }
    cout << "Total collisions: " << collision_count << "\n";
}

int main() {
    int n = 3;
    int seed = rand() % 1024;

    vector<User> users = create_users(n, seed);
    simulate_transmission(users, 10, 12, All);

    cout << "\n==================================================\n\n";

    users = create_users(n, seed);
    simulate_transmission(users, 10, 24, NoOutput);

    return 0;
}
