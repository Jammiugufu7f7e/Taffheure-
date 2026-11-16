import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

from time_tracker import TimeTracker


class TimeTrackerApp:
    def __init__(self, root):
        self.tracker = TimeTracker(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "time_entries.txt")
        )
        self.root = root
        self.root.title("Time Tracker")

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill="both")

        self.create_label(frame, "Date (JJ/MM/AA):")
        self.day_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(1, 32)])
        self.month_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(1, 13)])
        self.year_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(24, 100)])
        self.create_label(frame, "Heure de début:")
        self.start_hour = self.create_combobox(frame, [f"{i:02d}" for i in range(24)])
        self.start_minute = self.create_combobox(frame, [f"{i:02d}" for i in range(60)])
        self.create_label(frame, "Heure de fin:")
        self.end_hour = self.create_combobox(frame, [f"{i:02d}" for i in range(24)])
        self.end_minute = self.create_combobox(frame, [f"{i:02d}" for i in range(60)])
        self.create_label(frame, "Temps de pause (minutes):")
        self.pause_entry = self.create_combobox(frame, [f"{i:02d}" for i in range(0, 121, 5)])
        self.create_button(frame, "Ajouter", self.add_entry)
        self.create_button(frame, "Total d'heures", self.show_total)
        self.create_button(frame, "Heures travaillées aujourd'hui", self.show_daily)
        self.create_button(frame, "Afficher les entrées", self.show_entries)
        self.create_button(frame, "Exporter en CSV", self.export_to_csv)

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
            messagebox.showerror("Erreur", "La date doit être remplie.")
            return

        try:
            self.tracker.add_entry(date, start_time, end_time, pause_time)
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de format de date/heure: {e}")
            return
        except PermissionError:
            messagebox.showerror("Erreur", "Permission refusée pour écrire dans le fichier texte.")
            return

        messagebox.showinfo("Succès", "Entrée ajoutée avec succès!")

    def show_total(self):
        total_hours = self.tracker.total_hours()
        formatted_hours = self.tracker.format_hours(total_hours)
        messagebox.showinfo("Total d'heures", f"Total d'heures travaillées: {formatted_hours}")

    def show_daily(self):
        date = f"{self.day_entry.get()}/{self.month_entry.get()}/{self.year_entry.get()}"
        try:
            daily_hours = self.tracker.daily_hours(date)
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de format de date/heure: {e}")
            return
        formatted_hours = self.tracker.format_hours(daily_hours)
        messagebox.showinfo("Heures travaillées aujourd'hui", f"Heures travaillées le {date}: {formatted_hours}")

    def show_entries(self):
        entries_window = tk.Toplevel(self.root)
        entries_window.title("Entrées enregistrées")
        entries_text = tk.Text(entries_window)
        entries_text.pack()
        for entry in self.tracker.entries:
            entries_text.insert(tk.END, f"Début: {entry[0]}, Fin: {entry[1]}, Durée: {entry[2]}, Pause: {entry[3]}\n")

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.tracker.export_to_csv(file_path)
            except PermissionError:
                messagebox.showerror("Erreur", "Permission refusée pour écrire dans le fichier CSV.")
                return
            messagebox.showinfo("Succès", f"Données exportées avec succès dans {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
