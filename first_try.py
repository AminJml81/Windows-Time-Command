import psutil
import time


for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"].lower() == "explorer.exe":
            process_name = proc.info["name"]
            interval = 10
            t1_perf = proc.cpu_times()
            t1_wall = time.time()
            time.sleep(interval)
            t2_perf = proc.cpu_times()
            t2_wall = time.time()
            elapsed_wall_time = t2_wall - t1_wall
    
            delta_user = t2_perf.user - t1_perf.user
            delta_system = t2_perf.system - t1_perf.system
            delta_total_cpu = delta_user + delta_system
            print(delta_user, delta_system, delta_total_cpu)
            cpu_efficiency = (delta_total_cpu / elapsed_wall_time) * 100
            system_efficiency = (delta_system / elapsed_wall_time) * 100
            print("-" * 40)
            print(f" Results for '{process_name}' over {interval}s:")
            print("-" * 40)
            print(f"Elapsed Time (Wall Clock) : {elapsed_wall_time:.4f} sec")
            print(f"CPU Time (User + Sys)     : {delta_total_cpu:.4f} sec")
            print(f"System Time (Kernel)      : {delta_system:.4f} sec")
            print(f"User Time                 : {delta_user:.4f} sec")
            print("-" * 40)
            print(f"CPU Efficiency % : {cpu_efficiency:.2f}%")
            print(f"System Efficiency %: {system_efficiency:.2f}%")
            print("-" * 40)