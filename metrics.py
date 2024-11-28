import psutil
import time
from statistics import mean  # Importing mean to calculate average

def monitor_resources(duration=10):
    print("Monitoring resources...")
    cpu_usage, memory_usage = [], []
    for _ in range(duration):
        cpu_usage.append(psutil.cpu_percent(interval=1))
        memory_usage.append(psutil.virtual_memory().percent)
    print(f"Average CPU Usage: {mean(cpu_usage):.2f}%")
    print(f"Average Memory Usage: {mean(memory_usage):.2f}%")

if __name__ == "__main__":
    monitor_resources()
