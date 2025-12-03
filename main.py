import psutil
from psutil._common import pcputimes
import time
import argparse


def calculate_parameters(t1_cpu_times:pcputimes, t1_time:time, t2_cpu_times:pcputimes, t2_time:time):
    """
      calculates and return the followings:
        elapsed_wall_time
        delta_user
        delta_system
        delta_total_cpu
        cpu_efficiency
        system_efficiency
    """

    elapsed_wall_time = t2_time - t1_time
    delta_user = t2_cpu_times.user - t1_cpu_times.user
    delta_system = t2_cpu_times.system - t1_cpu_times.system
    delta_total_cpu = delta_user + delta_system
    if elapsed_wall_time:
        cpu_efficiency = (delta_total_cpu / elapsed_wall_time) * 100
        system_efficiency = (delta_system / elapsed_wall_time) * 100
    else:
        cpu_efficiency = system_efficiency = 0

    return  elapsed_wall_time, delta_user, delta_system, delta_total_cpu, cpu_efficiency, system_efficiency


def print_parameters(process_name:str, interval:int, elapsed_wall_time:float, delta_user:float, delta_system:float,
                                       delta_total_cpu:float, cpu_efficiency:float, system_efficiency:float):
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
     

def parse_args():
    parser = argparse.ArgumentParser(
         description= "Monitor CPU usage metrics for a specified process over a given time interval."
    )
    parser.add_argument('-p', '--process-name', type=str, help="Name of the process to monitor")
    parser.add_argument('-i', '--interval', type=int, help="Interval in seconds")
    return parser.parse_args()

def handle_arguments(args):
    parameters = dict()
    parameters['process_name'] = args.process_name if args.process_name else input('Process Name: ').lower()

    if args.interval:
        interval = args.interval
    else:
        try:
            interval = int(input('interval: '))
        except ValueError:
            print('Invalid Interval. Defaulting to 5 seconds.')
            interval = 5
    
    parameters['interval'] = interval
    return parameters

def wtime_run():
    args = parse_args()
    parameters = handle_arguments(args)

    for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"].lower() == parameters['process_name']:
                # getting data of current time(start of the interval) of the process.
                t1_cpu_times = proc.cpu_times()
                t1_time = time.time()
                time.sleep(parameters['interval'])
                # getting data of the end of the interval of the process.
                t2_cpu_times = proc.cpu_times()
                t2_time = time.time()

                elapsed_wall_time, delta_user, delta_system, delta_total_cpu, cpu_efficiency, system_efficiency = calculate_parameters(
                    t1_cpu_times, t1_time, t2_cpu_times, t2_time
                )

                print_parameters(
                    parameters['process_name'], parameters['interval'], elapsed_wall_time, delta_user, delta_system,
                                                delta_total_cpu, cpu_efficiency, system_efficiency
                )

if __name__=='__main__':
    wtime_run()