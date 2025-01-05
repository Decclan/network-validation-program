import subprocess
import threading
import tkinter as tk
from tkinter import ttk
import time 
from tkinter import filedialog
from datetime import datetime
import csv

class BandwidthTesterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bandwidth Tester")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Packet sizes options
        self.packet_size_list_1 = [54, 70, 92, 134, 198, 262, 310, 422, 582, 742, 902, 1046, 1206, 1350]
        self.packet_size_list_2 = [128, 256]

        # bandwidth sizes option
        self.bandwidth_range_list_1 = ["1M", "5M", "10M", "15M", "20M", "25M", "30M", "35M", "40M", "45M", "50M", "55M", "60M", "65M", "70M", "75M", "80M", "85M", "90M"]
        self.bandwidth_range_list_2 = ["5M", "50M"]

        # Variables
        self.serial_number = tk.StringVar(value='A-0000')
        self.server_ip = tk.StringVar(value='192.168.1.')
        self.port = tk.IntVar(value=5201)
        self.mode = tk.StringVar(value='Server')
        self.protocol = tk.StringVar(value='UDP')
        self.duration = tk.IntVar(value=2)


        # Widgets
        ttk.Label(self, text="Serial Number:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.serial_number).grid(row=0, column=1, sticky=tk.EW)
        #ttk.Label(self, text="Enter the serial number of your device.").grid(row=0, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)

        ttk.Label(self, text="Server IP:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.server_ip).grid(row=1, column=1, sticky=tk.EW)

        ttk.Label(self, text="Port:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.port).grid(row=2, column=1, sticky=tk.EW)

        # Mode selection ComboBox
        ttk.Label(self, text="Mode:").grid(row=3, column=0, sticky=tk.W)
        mode_combobox = ttk.Combobox(self, textvariable=self.mode, values=["Client", "Server"], state="readonly")
        mode_combobox.grid(row=3, column=1, sticky=tk.EW)
        mode_combobox.current(0)

        ttk.Label(self, text="Protocol:").grid(row=4, column=0, sticky=tk.W)
        protocol_combobox = ttk.Combobox(self, textvariable=self.protocol, values=["UDP", "TCP"], state="readonly")
        protocol_combobox.grid(row=4, column=1, sticky=tk.EW)
        protocol_combobox.current(0)

        # Packet Size Group Selector
        ttk.Label(self, text="Packet Size Group:").grid(row=5, column=0, sticky=tk.W)
        ttk.Label(self, text="Long Test Packets: 54 to 1350. Short Test Packets: 128 and 256.").grid(row=5, column=2, columnspan=2, sticky=tk.W)
        self.packet_size_group = tk.StringVar(value="Long Test Packets")
        packet_size_group_combobox = ttk.Combobox(
            self, 
            textvariable=self.packet_size_group, 
            values=["Long Test Packets", "Short Test Packets"], 
            state="readonly"
        )
        packet_size_group_combobox.grid(row=5, column=1, sticky=tk.EW)
        packet_size_group_combobox.current(1)

        # Bandwidth Range Group Selector
        ttk.Label(self, text="Bandwith Range Group:").grid(row=6, column=0, sticky=tk.W)
        ttk.Label(self, text="Long Test Bandwidth: 1M and 90M. Short Test Bandwidth: 5M to 50M.").grid(row=6, column=2, columnspan=2, sticky=tk.W)
        self.bandwidth_range_group = tk.StringVar(value="Long Test Bandwidth")
        bandwidth_range_group_combobox = ttk.Combobox(
            self, 
            textvariable=self.bandwidth_range_group, 
            values=["Long Test Bandwidth", "Short Test Bandwidth"], 
            state="readonly"
        )
        bandwidth_range_group_combobox.grid(row=6, column=1, sticky=tk.EW)
        bandwidth_range_group_combobox.current(1)

        ttk.Label(self, text="Duration:").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.duration).grid(row=7, column=1, sticky=tk.EW)


        # Buttons 

        self.start_button = ttk.Button(self, text="Start Test", command=self.start_test)
        self.start_button.grid(row=8, column=0)

        self.stop_button = ttk.Button(self, text="Stop Test", command=self.stop_test, state=tk.DISABLED)
        self.stop_button.grid(row=8, column=1)

        self.clear_button = ttk.Button(self, text="Clear Log", command=self.clear_log)
        self.clear_button.grid(row=9, column=0)

        self.export_button = ttk.Button(self, text="Export Results", command=self.export_results, state=tk.DISABLED)
        self.export_button.grid(row=9, column=1)

        self.csv_export_button = ttk.Button(self, text="Export CSV Results", command=self.export_csv_results, state=tk.DISABLED)
        self.csv_export_button.grid(row=10, column=0)

        self.log_view = tk.Text(self, width=100, height=20)
        self.log_view.grid(row=11, columnspan=2, sticky=tk.EW)

        self.columnconfigure(1, weight=1)

        self.test_process = None
        self.logs = []

    def on_close(self):
        if self.test_process:
            self.stop_test()
        self.destroy()

    def start_test(self):
        if not self.test_process:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.export_button.config(state=tk.DISABLED)
            self.csv_export_button.config(state=tk.DISABLED)
            self.clear_button.config(state=tk.DISABLED)
            self.logs = []  # Clear the previous logs

            test_thread = threading.Thread(target=self.start_test_thread, daemon=True)
            test_thread.start()

    def start_test_thread(self):
        server_ip = self.server_ip.get()
        port = self.port.get()
        mode = self.mode.get()
        protocol = self.protocol.get()
        serial_number = self.serial_number.get()
        duration = self.duration.get()
        if self.packet_size_group.get() == "Long Test Packets":
            packet_size_final = self.packet_size_list_1
        else:
            packet_size_final = self.packet_size_list_2
        # bandwidth range selection
        if self.bandwidth_range_group.get() == "Long Test Bandwidth":
            bandwidth_range_final = self.bandwidth_range_list_1
        else:
            bandwidth_range_final = self.bandwidth_range_list_2

        # Server mode
        if mode == "Server":
            command = ["iperf3", "-s", "-p", str(port)]
            self.test_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            for line in iter(self.test_process.stdout.readline, b''):
                log = line.decode("utf-8")
                self.update_log(log)

            self.end_test()
            return

        # Client mode
        for bandwidth_range in bandwidth_range_final:
            for packet_size in packet_size_final:
                command = ["iperf3", "-c", server_ip, "-p", str(port), "-t", str(duration), "-l", str(packet_size), "-b", str(bandwidth_range),"-i", "1"]

                if protocol == "UDP":
                    command.append("-u")
            
                print(f"Executing command: {''.join(command)}")
                page_break = 80 * "*"
                self.update_log(f"{page_break}\n")
                self.update_log(f"Testing packet size: {packet_size} bytes with bandwidth of {bandwidth_range}\n")

                self.test_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                for line in iter(self.test_process.stdout.readline, b''):
                    log = line.decode("utf-8")
                    self.update_log(log)

                if self.test_process:
                    self.test_process.terminate()
                    self.test_process.wait()
            
                time.sleep(2)
        
        # Append date/device information to end of logs
        self.logs.append(datetime.now().strftime('Test Complete. Report Generated: %Y-%m-%d %H:%M:%S'))
        self.logs.append(f'Device Serial Number: {serial_number}')
        self.end_test()

    def update_log(self, log):
        """Thread-safe log updates."""
        self.logs.append(log.strip())
        self.after(0, self._append_log_to_view, log)

    def _append_log_to_view(self, log):
        self.log_view.insert(tk.END, log)
        self.log_view.see(tk.END)


    def end_test(self):
        if self.test_process:
            self.test_process = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL if self.logs else tk.DISABLED)
        self.csv_export_button.config(state=tk.NORMAL if self.logs else tk.DISABLED)
        self.clear_button.config(state=tk.NORMAL)

    def stop_test(self):
        if self.test_process and self.test_process.poll() is None:  # Check if the process is running
            self.test_process.terminate()
            try:
                self.test_process.wait(timeout=2)  # Time to exit gracefully
            except subprocess.TimeoutExpired:
                self.test_process.kill()
            self.update_log("Test stopped by user.\n")
        self.after(0, self.end_test)

    def clear_log(self):
        self.log_view.delete(1.0, tk.END)
        self.logs = []

    def export_results(self):
        if self.logs:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt", 
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                with open(file_path, 'w') as f:
                    for log in self.logs:
                        f.write(f"{log}\n")
                print(f"Data exported to {file_path}")
                self.export_button.config(state=tk.DISABLED)

    def export_csv_results(self):
        if self.logs:  # Ensure logs exist
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if file_path:
                #main_header = [test_date]
                test_header = ['Packet Size:', 'Bandwidth:', 'Client IP:', 'Client Port:', 'Server IP:', 'Server Port:', 'Duration:', 'Transfer:', 'Bitrate:', 'Jitter:', 'Lost/Total']

                rows = []
                for log in self.logs:
                    lines = log.split('\n')
                    for line in lines:
                        # Row 1 of test log with test packet/bandwidth size
                        if "Testing" in line:
                            # Main row for each test
                            result_row = []
                            test_size_parts = line.split()
                            try:
                                log_packet_size = f"{test_size_parts[3]} {test_size_parts[4]}"
                                log_bandwidth_size = test_size_parts[8]
                                result_row.extend([log_packet_size, log_bandwidth_size])
                            except IndexError:
                                continue
                        # Row 3 of test log with server client info
                        if "[  5] local" in line:
                            client_server_parts = line.split()
                            try:
                                client_ip = client_server_parts[3]
                                client_port = client_server_parts[5]
                                server_ip = client_server_parts[8]
                                server_port = client_server_parts[10]
                                result_row.extend([client_ip, client_port, server_ip, server_port])
                            except IndexError:
                                continue
                        # Row 8 of test log with final results of each test
                        if "%)  receiver" in line:
                            final_result_parts = line.split()
                            try:
                                iperf_duration = final_result_parts[2]
                                duration = iperf_duration[5:]
                                #duration = f"{final_result_parts[2]} {final_result_parts[3]}"
                                transfer = f"{final_result_parts[4]} {final_result_parts[5]}"
                                bitrate = f"{final_result_parts[6]} {final_result_parts[7]}"
                                jitter = f"{final_result_parts[8]} {final_result_parts[9]}"
                                loss = f"{final_result_parts[10]} {final_result_parts[11]}"
                                result_row.extend([duration, transfer, bitrate, jitter, loss])
                                rows.append(result_row)
                            except IndexError:
                                continue

                # Write parsed data to the CSV file
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(test_header)
                    writer.writerows(rows)

                print(f"Data exported to {file_path}")
                self.csv_export_button.config(state=tk.DISABLED)

if __name__ == '__main__':
    app = BandwidthTesterApp()
    app.mainloop()
