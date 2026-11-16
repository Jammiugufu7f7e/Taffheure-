import csv
import datetime
import json
import os

OLD_FR_PREFIX = "Début:"
OLD_EN_PREFIX = "Start:"


class TimeTracker:
    """Work-hour tracker that persists entries and reloads them on startup."""

    def __init__(self, file_path=None):
        self.entries = []
        self.file_path = file_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "time_entries.txt"
        )
        self.load_from_file()

    def add_entry(self, date, start_time, end_time, pause_time):
        start = datetime.datetime.strptime(
            f"{date} {self.format_time(start_time)}", "%d/%m/%y %H:%M"
        )
        end = datetime.datetime.strptime(
            f"{date} {self.format_time(end_time)}", "%d/%m/%y %H:%M"
        )
        pause_minutes = int(pause_time) if pause_time else 0
        if pause_minutes < 0:
            raise ValueError("Pause time cannot be negative.")
        pause = datetime.timedelta(minutes=pause_minutes)
        duration = end - start - pause
        if end <= start:
            raise ValueError("End time must be after start time.")
        if duration.total_seconds() <= 0:
            raise ValueError("Worked duration must be greater than zero after pause.")
        self.entries.append((start, end, duration, pause))
        self.save_to_file(start, end, duration, pause)

    def total_hours(self):
        total = sum((entry[2].total_seconds() for entry in self.entries), 0)
        return total / 3600

    def daily_hours(self, date):
        day = datetime.datetime.strptime(date, "%d/%m/%y").date()
        total = sum(
            (entry[2].total_seconds() for entry in self.entries if entry[0].date() == day),
            0,
        )
        return total / 3600

    def save_to_file(self, start, end, duration, pause):
        record = {
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds"),
            "duration_seconds": int(duration.total_seconds()),
            "pause_seconds": int(pause.total_seconds()),
        }
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

    def load_from_file(self):
        self.entries = []
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line:
                    continue
                entry = self._parse_line(line)
                if entry is not None:
                    self.entries.append(entry)

    def _parse_line(self, line):
        if line.startswith("{"):
            return self._parse_json_line(line)
        if line.startswith(OLD_FR_PREFIX) or line.startswith(OLD_EN_PREFIX):
            return self._parse_legacy_line(line)
        return None

    def _parse_json_line(self, line):
        data = json.loads(line)
        start = datetime.datetime.fromisoformat(data["start"])
        end = datetime.datetime.fromisoformat(data["end"])
        pause = datetime.timedelta(seconds=int(data.get("pause_seconds", 0)))
        if "duration_seconds" in data:
            duration = datetime.timedelta(seconds=int(data["duration_seconds"]))
        else:
            duration = end - start - pause
        return (start, end, duration, pause)

    def _parse_legacy_line(self, line):
        if line.startswith(OLD_FR_PREFIX):
            start_s = _between(line, "Début: ", ", Fin: ")
            end_s = _between(line, ", Fin: ", ", Durée: ")
            pause_s = _after(line, ", Pause: ")
        else:
            start_s = _between(line, "Start: ", ", End: ")
            end_s = _between(line, ", End: ", ", Duration: ")
            pause_s = _after(line, ", Pause: ")
        if not start_s or not end_s or pause_s is None:
            return None
        start = datetime.datetime.fromisoformat(start_s.strip())
        end = datetime.datetime.fromisoformat(end_s.strip())
        pause = _parse_timedelta(pause_s.strip())
        duration = end - start - pause
        return (start, end, duration, pause)

    def format_hours(self, hours):
        sign = "-" if hours < 0 else ""
        abs_hours = abs(hours)
        h = int(abs_hours)
        m = int(round((abs_hours - h) * 60))
        if m == 60:
            h += 1
            m = 0
        return f"{sign}{h}h{m:02d}"

    def format_time(self, time_str):
        return f"{time_str}:00" if ":" not in time_str else time_str

    def export_to_csv(self, file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Start", "End", "Duration", "Pause"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.entries:
                writer.writerow(
                    {
                        "Start": entry[0],
                        "End": entry[1],
                        "Duration": entry[2],
                        "Pause": entry[3],
                    }
                )


def _between(text, start_token, end_token):
    start = text.find(start_token)
    end = text.find(end_token)
    if start == -1 or end == -1 or end < start:
        return None
    return text[start + len(start_token) : end]


def _after(text, token):
    start = text.find(token)
    if start == -1:
        return None
    return text[start + len(token) :]


def _parse_timedelta(value):
    parts = value.strip().split(":")
    if len(parts) != 3:
        raise ValueError(f"Unrecognized duration format: {value}")
    hours, minutes, seconds = (int(part) for part in parts)
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
