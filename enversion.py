import datetime
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import csv

class TimeTracker:
    def __init__(self):
        self.entries = []
        self.file_path = os.path.join(os.path.dirname(__file__), "time_entries.txt")
    
    def add_entry(self, date, start_time, end_time, pause_time):
        try:
            start = datetime.datetime.strptime(f"{date} {self.format_time(start_time)}", '%d/%m/%y %H:%M')
            end = datetime.datetime.strptime(f"{date} {self.format_time(end_time)}", '%d/%m/%y %H:%M')
            pause = datetime.timedelta(minutes=int(pause_time) if pause_time else 0)
            duration = end - start - pause
            self.entries.append((start, end, duration, pause))
            self.save_to_file(start, end, duration, pause)
        except ValueError as e:
            messagebox.showerror("Error", f"Date/Time format error: {e}")
    
    def total_hours(self):
        total = sum((entry[2].total_seconds() for entry in self.entries), 0)
        return total / 3600
    
    def daily_hours(self, date):
        total = sum((entry[2].total_seconds() for entry in self.entries if entry[0].date() == datetime.datetime.strptime(date, '%d/%m/%y').date()), 0)
        return total / 3600
    
    def save_to_file(self, start, end, duration, pause):
        try:
            with open(self.file_path, "a") as file:
                file.write(f"Start: {start}, End: {end}, Duration: {duration}, Pause: {pause}\n")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied to write to text file.")
    
    def format_hours(self, hours):
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h}h{m:02d}"
    
    def format_time(self, time_str):
        return f"{time_str}:00" if ':' not in time_str else time_str
    
    def export_to_csv(self, file_path):
        try:
            with open(file_path, "w", newline='') as csvfile:
                fieldnames = ['Start', 'End', 'Duration', 'Pause']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entry in self.entries:
                    writer.writerow({'Start': entry[0], 'End': entry[1], 'Duration': entry[2], 'Pause': entry[3]})
            messagebox.showinfo("Success", f"Data successfully exported to {file_path}")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied to write to CSV file.")

class TimeTrackerApp:
    def __init__(self, root):
        self.tracker = TimeTracker()
        self.root = root
        self.root.title("Time Tracker")

        self.create_widgets()
    
    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill='both')

        self.create_label(frame, "Date (DD/MM/YY):")
        self.day_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(1, 32)])
        self.month_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(1, 13)])
        self.year_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(24, 100)])
        self.create_label(frame, "Start Time:")
        self.start_hour = self.create_combobox(frame, [f"{i:02d}" for i in range(24)])
        self.start_minute = self.create_combobox(frame, [f"{i:02d}" for i in range(60)])
        self.create_label(frame, "End Time:")
        self.end_hour = self.create_combobox(frame, [f"{i:02d}" for i in range(24)])
        self.end_minute = self.create_combobox(frame, [f"{i:02d}" for i in range(60)])
        self.create_label(frame, "Pause Time (minutes):")
        self.pause_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(0, 121, 5)])
        self.create_button(frame, "Add", self.add_entry)
        self.create_button(frame, "Total Hours", self.show_total)
        self.create_button(frame, "Hours Worked Today", self.show_daily)
        self.create_button(frame, "Show Entries", self.show_entries)
        self.create_button(frame, "Export to CSV", self.export_to_csv)
    
    def create_label(self, frame, text):
        label = tk.Label(frame, text=text)
        label.pack()
    
    def create_combobox(self, frame, values):
        combobox = ttk.Combobox(frame, values=values)
        combobox.pack()
        return combobox
    
    def create_button(self, frame, text, command):
        button = tk.Button(frame, text=text, command=command)
        button.pack()
    
    def add_entry(self):
        date = f"{self.day_entry.get()}/{self.month_entry.get()}/{self.year_entry.get()}"
        start_time = f"{self.start_hour.get()}:{self.start_minute.get()}"
        end_time = f"{self.end_hour.get()}:{self.end_minute.get()}"
        pause_time = self.pause_entry.get()

        if not self.day_entry.get() or not self.month_entry.get() or not self.year_entry.get():
            messagebox.showerror("Error", "Date must be filled.")
            return

        self.tracker.add_entry(date, start_time, end_time, pause_time)
        messagebox.showinfo("Success", "Entry added successfully!")
    
    def show_total(self):
        total_hours = self.tracker.total_hours()
        formatted_hours = self.tracker.format_hours(total_hours)
        messagebox.showinfo("Total Hours", f"Total hours worked: {formatted_hours}")
    
    def show_daily(self):
        date = f"{self.day_entry.get()}/{self.month_entry.get()}/{self.year_entry.get()}"
        daily_hours = self.tracker.daily_hours(date)
        formatted_hours = self.tracker.format_hours(daily_hours)
        messagebox.showinfo("Hours Worked Today", f"Hours worked on {date}: {formatted_hours}")
    
    def show_entries(self):
        entries_window = tk.Toplevel(self.root)
        entries_window.title("Recorded Entries")
        entries_text = tk.Text(entries_window)
        entries_text.pack()
        for entry in self.tracker.entries:
            entries_text.insert(tk.END, f"Start: {entry[0]}, End: {entry[1]}, Duration: {entry[2]}, Pause: {entry[3]}\n")
    
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.tracker.export_to_csv(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()