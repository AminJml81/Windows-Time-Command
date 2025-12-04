import psutil
import time
import argparse


class WTime:

    def __init__(self):
        pass
    

    def parse_args(self):
        parser = argparse.ArgumentParser(
        description= "Monitor CPU usage metrics for a specified process over a given time interval."
    )
        parser.add_argument('-p', '--process-name', type=str, help="Name of the process to monitor")
        parser.add_argument('-i', '--interval', type=int, help="Interval in seconds")
        parser.add_argument('-l', '--list', action='store_true', help='List all PIDs for the given process name and exit.')
        parser.add_argument('-id', '--pid', type=int, help='Specify the exact PID to monitor.')
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

        self.pid = self.args.pid if self.args.pid else 0
            
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
        """returns first process if the pid is not provided, else returns the process with the matching pid."""
        if pid == 0:
            self.pid = processes[0].info['pid']
            return processes[0]
        else:
            for process in processes:
                if process.info['pid'] == pid:
                    return process
            return None
        
    def run(self):
        try:
            self.parse_args()
            self.handle_arguments()
            processes = self.find_process()

            if len(processes) == 0:
                print(f"No '{self.process_name}' process found.")
            else:
                if self.args.list:
                    self.list_processes(processes)

                else:
                    process = self.get_target_process(self.pid, processes)
                    if process:
                        self.t1_cpu_times = process.cpu_times()
                        self.t1_time = time.time()
                        time.sleep(self.interval)

                        # getting data of the end of the interval of the process.
                        self.t2_cpu_times = process.cpu_times()
                        self.t2_time = time.time()

                        self.calculate_parameters()

                        self.print_parameters()
                    else:
                        print(f"Found No '{self.process_name}' process with pid {self.pid}.")

        except KeyboardInterrupt:
            print('Monitoring stopped by user.')
        
        except Exception as e:
            print(f'Monitoring stopped by following Error: {e}')


    def calculate_parameters(self):
        self.elapsed_wall_time = self.t2_time - self.t1_time
        self.delta_user = self.t2_cpu_times.user - self.t1_cpu_times.user
        self.delta_system = self.t2_cpu_times.system - self.t1_cpu_times.system
        self.delta_total_cpu = self.delta_user + self.delta_system
        if self.elapsed_wall_time:
            self.cpu_efficiency = (self.delta_total_cpu / self.elapsed_wall_time) * 100
            self.system_efficiency = (self.delta_system / self.elapsed_wall_time) * 100
        else:
            self.cpu_efficiency = self.system_efficiency = 0


    def print_parameters(self):
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
        print("-" * 40)



if __name__ == '__main__':
    WTime().run()