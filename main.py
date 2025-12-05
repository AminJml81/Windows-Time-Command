import psutil
import time
import argparse
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime


class WTime:

    def __init__(self):
        self.args = None
        self.process_name = None
        self.interval = 5
        self.pid = 0
        self.process = None
        self.total_duration = 0

        self.t1_cpu_times = None
        self.t2_cpu_times = None
        self.t1_time = None
        self.t2_time = None
        self.elapsed_wall_time = 0
        self.delta_user = 0
        self.delta_system = 0
        self.delta_total_cpu = 0
        self.cpu_efficiency = 0
        self.system_efficiency = 0
        self.user_efficiency = 0

        self.x_data = []      
        self.y_total = []      
        self.y_sys = []       
        self.y_user = []
        self.start_timestamp = 0
        self.fig = None
        self.ax = None

        self.line_total = None
        self.line_sys = None
        self.line_user = None

        self.text_elapsed = None
        self.text_cpu = None
        self.text_sys = None
        self.text_user = None

        self.csv_file = None
        self.csv_writer = None
        self.csv_data_buffer = []


    def parse_args(self):
        parser = argparse.ArgumentParser(
        description= "Monitor CPU usage metrics for a specified process over a given time interval."
    )
        parser.add_argument('-p', '--process-name', type=str, help="Name of the process to monitor")
        parser.add_argument('-i', '--interval', type=int, help="Interval in seconds")
        parser.add_argument('-l', '--list', action='store_true', help='List all PIDs for the given process name and exit.')
        parser.add_argument('-id', '--pid', type=int, help='Specify the exact PID to monitor.')
        parser.add_argument('-g', '--graph', action='store_true', help='Show real-time graph.')
        parser.add_argument('-t', '--total-duration', type=int, default=0, help='Total monitoring time in seconds. Closes automatically.')
        parser.add_argument('--csv', type=str, help='Specify the output CSV file path to save monitoring data.')

        self.args = parser.parse_args()

    def handle_arguments(self):
        self.process_name = self.args.process_name if self.args.process_name else input('Process Name: ').lower()

        if not self.args.list:
            if self.args.interval:
                self.interval = self.args.interval
            else:
                try:
                    self.interval = int(input('interval: '))
                except ValueError:
                    print('Invalid Interval. Defaulting to 5 seconds.')
                    self.interval = 5

            if self.args.total_duration:
                self.total_duration = self.args.total_duration
                
        self.pid = self.args.pid if self.args.pid else 0

        if self.args.csv and not self.args.list:
            try:
                self.csv_file = open(self.args.csv, 'w', newline='')
                self.csv_writer = csv.writer(self.csv_file)
                self.csv_writer.writerow(['Timestamp', 'Elapsed', 'Interval', 'Total_CPU_Efficiency', 'System_Efficiency', 'User_Efficiency'])
                print(f"Data will be saved to '{self.args.csv}'")
            except Exception as e:
                print(f"Error opening CSV file: {e}. Monitoring continues without saving.")
                self.csv_file = None
                self.csv_writer = None

    def save_data(self, elapsed):
        if self.csv_writer:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{elapsed:.2f}",
                f"{self.elapsed_wall_time:.2f}",
                f"{self.cpu_efficiency:.2f}",
                f"{self.system_efficiency:.2f}",
                f"{self.user_efficiency:.2f}"
            ]
            self.csv_data_buffer.append(row)
            
            # if not graph mode, add data to csv now and empty the list(buffer). 
            if not self.args.graph:
                self.csv_writer.writerow(row)
                self.csv_data_buffer = [] # بافر را پاک می‌کنیم
        
    def close_csv(self):
        if self.csv_file:
            if self.args.graph and self.csv_data_buffer:
                # for graph mode save data at the end of the monitoring.
                self.csv_writer.writerows(self.csv_data_buffer)
                print(f"\nFinal data written to '{self.args.csv}'")
            self.csv_file.close()  
                  
    def find_process(self):
        processes = []
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'].lower() == self.process_name.lower():
                processes.append(process)

        return processes
    
    
    def list_processes(self, processes):
        print(f'Found pids for {self.process_name}: ')
        print()
        print("-" * 40)        
        for process in processes:
            print(f"pid: {process.info['pid']} | Name: {process.info['name']}")


    def get_target_process(self, pid, processes):
        """returns first process of the list of processes if the pid is not provided, else returns the process with the matching pid."""
        if pid == 0:
            self.pid = processes[0].info['pid']
            return processes[0]
        else:
            for process in processes:
                if process.info['pid'] == pid:
                    return process
            return None
        
    def update_graph(self, frame):
        if not self.process.is_running():
            print("Process terminated.")
            sys.exit(0)
        
        current_time = time.time()
        elapsed = current_time - self.start_timestamp


        if self.total_duration > 0 and elapsed >= (self.total_duration+1):
            print(f"\nMonitoring finished after {elapsed} seconds.")
            plt.close(self.fig)
            return
        
        current_cpu_times = self.process.cpu_times()
        
        # if there is previous data.
        if self.t1_time is not None:
            self.t2_time = current_time
            self.t2_cpu_times = current_cpu_times
            
            self.calculate_parameters()

            self.save_data(elapsed)

            print(f"\rCPU: {self.cpu_efficiency:5.2f}% | Sys: {self.system_efficiency:5.2f}% | User: {self.user_efficiency:5.2f}%", end="")

            # adding these data to their corresponding list.
            elapsed = current_time - self.start_timestamp
            self.x_data.append(elapsed)
            self.y_total.append(self.cpu_efficiency)
            self.y_sys.append(self.system_efficiency)
            self.y_user.append(self.user_efficiency)

            # draw again.
            self.line_total.set_data(self.x_data, self.y_total)
            self.line_sys.set_data(self.x_data, self.y_sys)
            self.line_user.set_data(self.x_data, self.y_user)

            # scrolling x axis.
            self.ax.set_xlim(max(0, elapsed - 30), elapsed + 5)
            
            # updating text data.
            total_str = f" / {self.total_duration} s" if self.total_duration > 0 else ""
            self.text_elapsed.set_text(f"Elapsed: {elapsed:.1f}s / {total_str}")
            self.text_cpu.set_text(f"Total CPU: {self.cpu_efficiency:.1f}%")
            self.text_sys.set_text(f"System: {self.system_efficiency:.1f}%")
            self.text_user.set_text(f"User: {self.user_efficiency:.1f}%")

        
        self.t1_time = current_time
        self.t1_cpu_times = current_cpu_times

    def start_graph_mode(self):
        print(f"Starting Graph Mode for PID {self.pid}...")
        
        self.start_timestamp = time.time()
        self.t1_time = None 
        
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        # initializing lines data parameters.
        self.line_total, = self.ax.plot([], [], label='Total CPU %', color='blue')
        self.line_sys, = self.ax.plot([], [], label='System %', color='red', linestyle='--')
        self.line_user, = self.ax.plot([], [], label='User %', color='green', linestyle=':')

        # initializing live text data parameters.
        self.text_elapsed = self.ax.text(0.98, 0.98, 'Elapsed: 0.0 s', transform=self.ax.transAxes, verticalalignment='top', horizontalalignment='right', color='black')
        self.text_cpu = self.ax.text(0.98, 0.93, 'Total CPU: 0.0%', transform=self.ax.transAxes, verticalalignment='top', horizontalalignment='right', color='blue', weight='bold')
        self.text_sys = self.ax.text(0.98, 0.88, 'System: 0.0%', transform=self.ax.transAxes, verticalalignment='top', horizontalalignment='right', color='red')
        self.text_user = self.ax.text(0.98, 0.83, 'User: 0.0%', transform=self.ax.transAxes, verticalalignment='top', horizontalalignment='right', color='green')
        
        self.ax.set_title(f"Real-time Monitor: {self.process_name} (PID: {self.pid})")
        self.ax.set_xlabel("Elapsed Time (s)")
        self.ax.set_ylabel("Usage (%)")
        self.ax.set_ylim(0, 105)
        self.ax.grid(True)
        self.ax.legend(loc='upper left')

        ani = FuncAnimation(self.fig, self.update_graph, interval=self.interval * 1000)
        
        plt.show()

    def run(self):
        try:
            self.parse_args()
            self.handle_arguments()
            processes = self.find_process()

            if len(processes) == 0:
                print(f"No '{self.process_name}' process found.")
                self.close_csv()
            else:
                if self.args.list:
                    self.list_processes(processes)

                else:
                    self.process = self.get_target_process(self.pid, processes)
                    if self.process:
                        if self.args.graph:
                            self.start_graph_mode()
                            self.close_csv()
                        else:
                            print(f"Monitoring started for PID {self.pid}. Interval: {self.interval}. Total Duration: {self.total_duration if self.total_duration > 0 else 'Infinite'}")
                            
                            self.t1_cpu_times = self.process.cpu_times()
                            self.t1_time = time.time()
                            start_monitor_time = self.t1_time


                            while True:
                                elapsed_total = time.time() - start_monitor_time
                                if self.total_duration > 0 and elapsed_total >= self.total_duration:
                                    print(f"\nMonitoring finished after {elapsed_total:.1f} seconds.")
                                    break
                                
                                time.sleep(self.interval)

                                # getting data of the end of the interval of the process.
                                self.t2_cpu_times = self.process.cpu_times()
                                self.t2_time = time.time()

                                self.calculate_parameters()
                                self.print_parameters()

                                self.save_data(elapsed_total)
                                
                                # update for the next interval.
                                self.t1_cpu_times = self.t2_cpu_times
                                self.t1_time = self.t2_time

                                                        
                            self.close_csv()
                    
                    else:
                        print(f"Found No '{self.process_name}' process with pid {self.pid}.")

        except KeyboardInterrupt:
            print('Monitoring stopped by user.')
            self.close_csv()

        except Exception as e:
            print(f'Monitoring stopped by following Error: {e}')
            self.close_csv()


    def calculate_parameters(self):
        self.elapsed_wall_time = self.t2_time - self.t1_time
        self.delta_user = self.t2_cpu_times.user - self.t1_cpu_times.user
        self.delta_system = self.t2_cpu_times.system - self.t1_cpu_times.system
        self.delta_total_cpu = self.delta_user + self.delta_system
        if self.elapsed_wall_time:
            self.cpu_efficiency = (self.delta_total_cpu / self.elapsed_wall_time) * 100
            self.system_efficiency = (self.delta_system / self.elapsed_wall_time) * 100
            self.user_efficiency = (self.delta_user/self.elapsed_wall_time) * 100
        else:
            self.cpu_efficiency = self.system_efficiency = self.user_efficiency = 0


    def print_parameters(self):
        print()
        print("-" * 40)
        print(f"Results for '{self.process_name}' with pid {self.pid} over {self.interval}s:")
        print("-" * 40)
        print(f"Elapsed Time (Wall Clock) : {self.elapsed_wall_time:.4f} sec")
        print(f"CPU Time (User + Sys)     : {self.delta_total_cpu:.4f} sec")
        print(f"System Time (Kernel)      : {self.delta_system:.4f} sec")
        print(f"User Time                 : {self.delta_user:.4f} sec")
        print("-" * 40)
        print(f"CPU Efficiency % : {self.cpu_efficiency:.2f}%")
        print(f"System Efficiency %: {self.system_efficiency:.2f}%")
        print(f"User Efficiency %: {self.user_efficiency:.2f}%")
        print("-" * 40)


if __name__ == '__main__':
    WTime().run()