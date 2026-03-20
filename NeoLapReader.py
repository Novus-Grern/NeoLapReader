import ast
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np

class LogAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Log File Analyzer")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Store the selected files and parsed data
        self.selected_files = []
        self.all_lap_data = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Log File Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.select_btn = ttk.Button(file_frame, text="Select Log File(s)", 
                                    command=self.select_files, width=20)
        self.select_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.file_status = ttk.Label(file_frame, text="No files selected", 
                                    foreground="gray")
        self.file_status.grid(row=0, column=1)

        #this should probably be where the popup goes for the session statistics
        
        # Analysis section
        analysis_frame = ttk.LabelFrame(main_frame, text="Analysis", padding="10")
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.plot_btn = ttk.Button(analysis_frame, text="Show Lap Times Graph", 
                                  command=self.show_lap_times_graph, width=25, 
                                  state="disabled")
        self.plot_btn.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Additional analysis buttons
        self.analysis_btn1 = ttk.Button(analysis_frame, text="Session Statistics", 
                                       command=self.show_session_statistics, width=25, 
                                       state="disabled")
        self.analysis_btn1.grid(row=1, column=0, padx=(0, 5), pady=2)
        
        self.analysis_btn2 = ttk.Button(analysis_frame, text="Analysis 3", 
                                       command=self.placeholder_action, width=12, 
                                       state="disabled")
        self.analysis_btn2.grid(row=1, column=1, padx=(5, 0), pady=2)
        
        self.analysis_btn3 = ttk.Button(analysis_frame, text="Analysis 4", 
                                       command=self.placeholder_action, width=25, 
                                       state="disabled")
        self.analysis_btn3.grid(row=2, column=0, columnspan=2, pady=(5, 0))
    
    def select_files(self):
        """Open file dialog to select log files"""
        file_types = [
            ("Log files", "*.txt *.log *.acl"),
            ("Text files", "*.txt"),
            ("Log files", "*.log"),
            ("ACL files", "*.acl"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Log Files",
            filetypes=file_types
        )
        
        if files:
            self.selected_files = files
            self.parse_all_files()
            
            # Update UI
            file_count = len(files)
            self.file_status.config(text=f"{file_count} file(s) selected", 
                                   foreground="green")
            
            # Enable analysis buttons
            self.plot_btn.config(state="normal")
            self.analysis_btn1.config(state="normal")
            self.analysis_btn2.config(state="normal")
            self.analysis_btn3.config(state="normal")
        else:
            self.file_status.config(text="No files selected", foreground="gray")
            # Disable analysis buttons
            self.plot_btn.config(state="disabled")
            self.analysis_btn1.config(state="disabled")
            self.analysis_btn2.config(state="disabled")
            self.analysis_btn3.config(state="disabled")
    
    def parse_all_files(self):
        """Parse all selected files and combine lap data"""
        self.all_lap_data = []
        
        for filepath in self.selected_files:
            if filepath.endswith((".txt", ".log", ".acl")):
                lap_data = self.parse_log_file(filepath)
                self.all_lap_data.extend(lap_data)
        
        # Sort by lap number
        self.all_lap_data.sort(key=lambda x: x[0])
    
    def parse_log_file(self, filepath):
        """Parse a single log file for lap times"""
        lap_times = []
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("{") and "lap" in line and "time" in line:
                        try:
                            lap_entry = ast.literal_eval(line)
                            if not lap_entry.get('invalidated', True):
                                lap_times.append((lap_entry['lap'], lap_entry['time']))
                        except Exception as e:
                            print(f"Error parsing line: {line}\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file {filepath}:\n{e}")
        
        return lap_times
    
    def ms_to_readable(self, ms):
        """Convert milliseconds to readable time format"""
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        millis = ms % 1000
        return f"{minutes}:{seconds:02}.{millis:03}"
    
    def show_session_statistics(self):
        """Display session statistics in a popup table"""
        if not self.all_lap_data:
            messagebox.showwarning("No Data", "No valid lap data found in selected files.")
            return
        
        # Calculate statistics
        times_ms = [time for _, time in self.all_lap_data]
        fastest_lap = min(self.all_lap_data, key=lambda x: x[1])
        slowest_lap = max(self.all_lap_data, key=lambda x: x[1])
        average_time = np.mean(times_ms)
        median_time = np.median(times_ms)
        std_deviation = np.std(times_ms)
        
        # Create popup window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Session Statistics")
        stats_window.geometry("450x400")
        stats_window.resizable(False, False)
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Center the window
        stats_window.geometry("+{}+{}".format(
            int(self.root.winfo_x() + self.root.winfo_width()/2 - 225),
            int(self.root.winfo_y() + self.root.winfo_height()/2 - 200)
        ))
        
        # Main frame for the popup
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Session Statistics", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create treeview for the table
        columns = ('Statistic', 'Value')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        tree.heading('Statistic', text='Statistic')
        tree.heading('Value', text='Value')
        
        # Configure column widths
        tree.column('Statistic', width=200, anchor='w')
        tree.column('Value', width=200, anchor='w')
        
        # Prepare statistics data
        stats_data = [
            ("Total Laps", str(len(self.all_lap_data))),
            ("", ""),  # Empty row for spacing
            ("Fastest Lap", f"Lap {fastest_lap[0]}"),
            ("Fastest Time", self.ms_to_readable(fastest_lap[1])),
            ("", ""),  # Empty row for spacing
            ("Slowest Lap", f"Lap {slowest_lap[0]}"),
            ("Slowest Time", self.ms_to_readable(slowest_lap[1])),
            ("", ""),  # Empty row for spacing
            ("Average Lap Time", self.ms_to_readable(int(average_time))),
            ("Median Lap Time", self.ms_to_readable(int(median_time))),
            ("Standard Deviation", self.ms_to_readable(int(std_deviation))),
            ("", ""),  # Empty row for spacing
            ("Time Difference", self.ms_to_readable(slowest_lap[1] - fastest_lap[1])),
            ("Range (Max - Min)", f"{((slowest_lap[1] - fastest_lap[1]) / fastest_lap[1] * 100):.1f}%")
        ]
        
        # Insert data into treeview
        for i, (stat, value) in enumerate(stats_data):
            if stat == "":  # Empty row for spacing
                tree.insert('', 'end', values=("", ""))
            else:
                item = tree.insert('', 'end', values=(stat, value))
                
                # Highlight fastest and slowest lap rows
                if "Fastest" in stat:
                    tree.set(item, 'Statistic', stat)
                    tree.set(item, 'Value', value)
                elif "Slowest" in stat:
                    tree.set(item, 'Statistic', stat)
                    tree.set(item, 'Value', value)
        
        # Pack the treeview
        tree.pack(pady=(0, 20), fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", 
                              command=stats_window.destroy, width=15)
        close_btn.pack(pady=(10, 0))
        
        # Style the treeview with alternating row colors
        style = ttk.Style()
        style.configure("Treeview", background="white")
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Configure tag for alternating colors
        tree.tag_configure('oddrow', background='#f0f0f0')
        tree.tag_configure('evenrow', background='white')
        
        # Apply alternating colors
        for i, item in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(item, tags=('evenrow',))
            else:
                tree.item(item, tags=('oddrow',))
    
    def show_lap_times_graph(self):
        """Display the lap times graph"""
        if not self.all_lap_data:
            messagebox.showwarning("No Data", "No valid lap data found in selected files.")
            return
        
        self.plot_lap_times(self.all_lap_data)
    
    def plot_lap_times(self, lap_data):
        """Plot lap times graph only"""
        laps = [lap for lap, _ in lap_data]
        times_ms = [time for _, time in lap_data]
        
        mean_time = np.mean(times_ms)
        threshold = mean_time * 1.5
        
        # Calculate statistics
        fastest_lap = min(lap_data, key=lambda x: x[1])
        slowest_lap = max(lap_data, key=lambda x: x[1])
        
        # Identify slow laps (outliers)
        slow_laps = [(lap, time) for lap, time in lap_data if time > threshold]
        print(f"Flagged {len(slow_laps)} unusually slow laps (>{int(threshold)} ms):")
        for lap, time in slow_laps:
            print(f"Lap {lap}: {self.ms_to_readable(time)}")
        
        print(f"The fastest lap was lap {fastest_lap[0]} with a time of {self.ms_to_readable(fastest_lap[1])}.")
        
        # Separate laps for plotting
        normal_laps = [(lap, time) for lap, time in lap_data if time <= threshold]
        slow_laps_plot = [(lap, time) for lap, time in lap_data if time > threshold]
        
        # Unpack for plotting
        normal_x = [lap for lap, _ in normal_laps]
        normal_y = [time for _, time in normal_laps]
        slow_x = [lap for lap, _ in slow_laps_plot]
        slow_y = [time for _, time in slow_laps_plot]
        
        # Create figure with single plot
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='lightskyblue')
        
        # Plot the data
        ax.plot(normal_x, normal_y, marker='o', label='Normal Laps', color='blue')
        ax.scatter(slow_x, slow_y, marker='o', label='Slow Laps', color='red')
        
        # Annotate all laps
        fastest_lap_number = fastest_lap[0]
        for i, (lap, time) in enumerate(lap_data):
            offset = 10 if i % 2 == 0 else -15
            
            # Check if this is the fastest lap
            if lap == fastest_lap_number:
                # Apply bold and a different color
                ax.annotate(self.ms_to_readable(time), (lap, time), 
                           textcoords="offset points", xytext=(0, offset), 
                           ha='center', fontsize=8, fontweight='bold', color='#d900ff')
            else:
                # Normal annotation
                ax.annotate(self.ms_to_readable(time), (lap, time), 
                           textcoords="offset points", xytext=(0, offset), 
                           ha='center', fontsize=8)
        
        # Labels and formatting
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time")
        ax.set_title("Lap Times Over Session")
        ax.grid(True)
        ax.legend()
        
        plt.tight_layout()
        plt.show()
    
    def placeholder_action(self):
        """Placeholder function for future analysis buttons"""
        messagebox.showinfo("Coming Soon", "This analysis feature will be implemented later!")

def main():
    root = tk.Tk()
    app = LogAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()