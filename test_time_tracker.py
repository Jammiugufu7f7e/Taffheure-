import csv
import os
import tempfile
import unittest

from time_tracker import TimeTracker


class TimeTrackerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        self.tmp.close()
        self.path = self.tmp.name
        os.remove(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_reload_restores_saved_entries_and_totals(self):
        tracker = TimeTracker(self.path)
        tracker.add_entry("24/11/24", "08:00", "17:00", "30")

        reloaded = TimeTracker(self.path)

        self.assertEqual(len(reloaded.entries), 1)
        self.assertAlmostEqual(reloaded.total_hours(), 8.5)
        self.assertAlmostEqual(reloaded.daily_hours("24/11/24"), 8.5)

    def test_reload_keeps_multiple_days(self):
        tracker = TimeTracker(self.path)
        tracker.add_entry("24/11/24", "09:00", "12:00", "0")
        tracker.add_entry("25/11/24", "13:00", "18:00", "15")

        reloaded = TimeTracker(self.path)

        self.assertEqual(len(reloaded.entries), 2)
        self.assertAlmostEqual(reloaded.total_hours(), 7.75)
        self.assertAlmostEqual(reloaded.daily_hours("24/11/24"), 3.0)
        self.assertAlmostEqual(reloaded.daily_hours("25/11/24"), 4.75)

    def test_legacy_french_log_is_loaded(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(
                "Début: 2024-11-24 08:00:00, Fin: 2024-11-24 17:00:00, "
                "Durée: 8:30:00, Pause: 0:30:00\n"
            )

        tracker = TimeTracker(self.path)

        self.assertEqual(len(tracker.entries), 1)
        self.assertAlmostEqual(tracker.total_hours(), 8.5)

    def test_legacy_english_log_is_loaded(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(
                "Start: 2024-11-24 08:00:00, End: 2024-11-24 12:00:00, "
                "Duration: 3:45:00, Pause: 0:15:00\n"
            )

        tracker = TimeTracker(self.path)

        self.assertEqual(len(tracker.entries), 1)
        self.assertAlmostEqual(tracker.total_hours(), 3.75)

    def test_mixed_legacy_and_json_lines_are_loaded(self):
        tracker = TimeTracker(self.path)
        tracker.add_entry("25/11/24", "09:00", "10:00", "0")
        with open(self.path, "r", encoding="utf-8") as handle:
            json_line = handle.read()
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(
                "Début: 2024-11-24 08:00:00, Fin: 2024-11-24 09:00:00, "
                "Durée: 1:00:00, Pause: 0:00:00\n"
            )
            handle.write(json_line)

        reloaded = TimeTracker(self.path)

        self.assertEqual(len(reloaded.entries), 2)
        self.assertAlmostEqual(reloaded.total_hours(), 2.0)

    def test_end_before_start_is_rejected(self):
        tracker = TimeTracker(self.path)
        with self.assertRaises(ValueError):
            tracker.add_entry("24/11/24", "17:00", "08:00", "0")
        self.assertEqual(tracker.entries, [])
        self.assertFalse(os.path.exists(self.path))

    def test_pause_longer_than_shift_is_rejected(self):
        tracker = TimeTracker(self.path)
        with self.assertRaises(ValueError):
            tracker.add_entry("24/11/24", "08:00", "09:00", "90")
        self.assertEqual(tracker.entries, [])

    def test_invalid_date_does_not_write_file(self):
        tracker = TimeTracker(self.path)
        with self.assertRaises(ValueError):
            tracker.add_entry("32/11/24", "08:00", "09:00", "0")
        self.assertEqual(tracker.entries, [])
        self.assertFalse(os.path.exists(self.path))

    def test_export_csv_includes_reloaded_entries(self):
        tracker = TimeTracker(self.path)
        tracker.add_entry("24/11/24", "08:00", "16:00", "0")
        reloaded = TimeTracker(self.path)

        csv_path = self.path + ".csv"
        try:
            reloaded.export_to_csv(csv_path)
            with open(csv_path, newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertIn("2024-11-24 08:00:00", rows[0]["Start"])
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    def test_format_hours(self):
        tracker = TimeTracker(self.path)
        self.assertEqual(tracker.format_hours(8.5), "8h30")
        self.assertEqual(tracker.format_hours(0), "0h00")


if __name__ == "__main__":
    unittest.main()
