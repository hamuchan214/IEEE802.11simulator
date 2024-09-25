import time
import random
import threading

# Function to simulate traffic generation by a single terminal
def generate_traffic(terminal_id, traffic_per_terminal, duration, results):
    """Simulates the traffic generation for a single terminal and logs the packet generation time."""
    start_time = time.time()
    total_packets = 0
    
    # Run for the given duration
    while (time.time() - start_time) < duration:
        # Simulate packet generation every 1 ms
        time.sleep(0.001)
        
        # Randomly decide how many packets (if any) to generate in this 1 ms interval
        packets_this_ms = random.randint(0, int(traffic_per_terminal / 1000))
        
        if packets_this_ms > 0:
            current_time = time.time() - start_time  # Time in seconds since the start
            total_packets += packets_this_ms
            print(f"Terminal {terminal_id}: {packets_this_ms} packets generated at {current_time:.3f} seconds")
    
    results[terminal_id] = total_packets

# Main function to simulate traffic from multiple terminals
def simulate_traffic(n, G, duration):
    """Simulates traffic from n terminals generating a total of G packets over a specified duration."""
    traffic_per_terminal = G / n  # Total traffic is divided equally among terminals
    
    # Store results of each terminal
    results = {}
    
    # Start threads for each terminal to simulate traffic concurrently
    threads = []
    for i in range(n):
        thread = threading.Thread(target=generate_traffic, args=(i+1, traffic_per_terminal, duration, results))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return results

# Example usage:
n = 3        # Number of terminals
G = 10000    # Total traffic to generate
duration = 2 # Simulate for 2 seconds

# Running the simulation and capturing the results
traffic_results = simulate_traffic(n, G, duration)
print("Final traffic results:", traffic_results)
