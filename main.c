#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define SLOT_TIME 9e-6
#define DATA_TRANSMISSION 1500 * 8
#define TRANSMISSION_RATE 12e6
#define DURATION 120
#define NUM_USERS 5
#define SEED 123

typedef struct {
  int id;
  int n;
  int slots;
  int transmitted;
  double CW;
  double total_data_transmitted;
} User;

double calculate_CW(User *user) {
  int cw_max = pow(2, 4 + user->n) - 1;
  user->slots = rand() % (cw_max < 1023 ? cw_max : 1023) + 1;
  return user->slots * SLOT_TIME;
}

void re_transmit(User *user) {
  user->n++;
  user->CW = calculate_CW(user);
}

void reset_CW(User *user) {
  user->n = 0;
  user->CW = calculate_CW(user);
}

void create_users(User users[], int num_users, int seed) {
  srand(seed);
  for (int i = 0; i < num_users; i++) {
    users[i].id = i;
    users[i].n = 0;
    users[i].transmitted = 0;
    users[i].total_data_transmitted = 0;
    users[i].CW = calculate_CW(&users[i]);
  }
}

double transmission_time(double data, double rate) { return data / rate; }

void simulate_transmission(User users[], int num_users, double duration,
                           double rate, int print_output) {
  double current_time = 0;
  int collision_count = 0;
  double data_transmission = DATA_TRANSMISSION;
  double transmission_rate = rate;

  while (current_time < duration) {
    int min_user_id = -1;
    int min_slots = 1024;
    double min_cw = 0;

    for (int i = 0; i < num_users; i++) {
      if (users[i].slots < min_slots) {
        min_slots = users[i].slots;
        min_cw = users[i].CW;
        min_user_id = users[i].id;
      }
    }

    User *min_user = &users[min_user_id];
    int collisions = 0;

    for (int i = 0; i < num_users; i++) {
      if (users[i].slots == min_slots && users[i].id != min_user_id) {
        collisions++;
      }
    }

    if (collisions > 0) {
      collision_count++;
      current_time += min_cw;

      if (print_output == 0 || print_output == 1) {
        for (int i = 0; i < num_users; i++) {
          printf("User %d CW = %.6f seconds (waited %d slots)\n", users[i].id,
                 users[i].CW, users[i].slots);
        }
      }

      double trans_time =
          transmission_time(data_transmission, transmission_rate);
      if (current_time + trans_time <= duration) {
        current_time += trans_time;
      } else {
        current_time = duration;
      }

      if (print_output == 0) {
        printf("\nTime: %.2fs - Collision detected! Users: %d", current_time,
               min_user_id);
        for (int i = 0; i < num_users; i++) {
          if (users[i].slots == min_slots && users[i].id != min_user_id) {
            printf(", %d", users[i].id);
          }
        }
        printf("\n");
        for (int i = 0; i < num_users; i++) {
          if (users[i].slots == min_slots || users[i].id == min_user_id) {
            printf("User %d waited %d slots before collision.\n", users[i].id,
                   users[i].slots);
          }
        }
        printf("\n");
      }

      for (int i = 0; i < num_users; i++) {
        if (users[i].slots == min_slots || users[i].id == min_user_id) {
          re_transmit(&users[i]);
        }
      }

    } else {
      double trans_time =
          transmission_time(data_transmission, transmission_rate);
      if (current_time + trans_time <= duration) {
        current_time += min_cw;
        if (print_output == 1) {
          printf("\nTime: %.2fs - User %d transmitted successfully with CW = "
                 "%.6f seconds (waited %d slots)\n",
                 current_time, min_user_id, min_cw, min_user->slots);
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
        if (print_output == 1) {
          printf("\nTime: %.2fs - User %d partially transmitted %.2f Mbit due "
                 "to time limit\n",
                 current_time, min_user_id, data_transmitted / 1e6);
        }
      }

      for (int i = 0; i < num_users; i++) {
        if (users[i].id != min_user_id) {
          users[i].CW -= min_user->CW;
          users[i].slots -= min_user->slots;
        }
      }

      reset_CW(min_user);
    }
  }

  printf("\nSimulation ended. Results:\n");
  for (int i = 0; i < num_users; i++) {
    double average_transmission_rate =
        users[i].total_data_transmitted / duration / 1e6;
    printf("User %d transmitted %d times, total data transmitted: %.2f bits, "
           "average transmission rate: %.2f Mbps\n",
           users[i].id, users[i].transmitted, users[i].total_data_transmitted,
           average_transmission_rate);
  }

  printf("Total collisions: %d\n", collision_count);
}

int main() {
  User users[NUM_USERS];
  create_users(users, NUM_USERS, SEED);
  simulate_transmission(users, NUM_USERS, DURATION, TRANSMISSION_RATE, 2);

  printf("\n==================================================\n");

  create_users(users, NUM_USERS, SEED);
  simulate_transmission(users, NUM_USERS, DURATION, TRANSMISSION_RATE, 2);

  return 0;
}
