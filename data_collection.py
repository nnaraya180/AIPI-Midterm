"""
data_collection.py
================================
Records labeled posture snapshots from all 10 IMUs and saves them to a CSV.
Each row is one sample: timestamp, label, and pitch/roll for every segment.
"""

import csv
import os
from time import sleep, time

from imu_reader import setup, read_all_imus


# -----------------------------
# Configuration
# -----------------------------

CSV_FILE      = "posture_data.csv"
DELAY_SEC     = 0.10        # 10 samples per second
CAPTURE_SEC   = 30.0        # seconds per capture session

LABELS = [
    "sitting_good",
    "sitting_bad",
    "standing_good",
    "standing_bad",
]

# CSV column order — timestamp + label + pitch/roll for each segment
SEGMENTS = [
    "left_thigh", 
    "left_calf",
    "right_thigh", 
    "right_calf",
    "upper_mid_back", 
    "upper_back",
    "right_shoulder", 
    "left_shoulder",
    "lower_mid_back", 
    "lower_back",
]

CSV_HEADER = ["timestamp", "label"] + [
    f"{seg}_{angle}"
    for seg in SEGMENTS
    for angle in ("pitch", "roll")
]


# -----------------------------
# CSV Helpers
# -----------------------------

def write_header_if_needed(path):
    """Write CSV header only if the file doesn't exist yet."""
    if os.path.exists(path):
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)


def append_row(path, row):
    """Append one row to the CSV."""
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# -----------------------------
# Capture
# -----------------------------

def capture_session(label):
    """
    Read all IMUs at DELAY_SEC intervals for CAPTURE_SEC seconds.
    Each sample is saved as one row: timestamp, label, then pitch/roll
    for every segment in SEGMENTS order.

    Returns:
        number of samples saved (int)
    """
    write_header_if_needed(CSV_FILE)

    count = 0
    start = time()

    while time() - start < CAPTURE_SEC:
        readings = read_all_imus()
        timestamp = round(time(), 4)

        # Flatten readings into a single row in SEGMENTS order
        row = [timestamp, label]
        for seg in SEGMENTS:
            angles = readings.get(seg)
            if angles is not None:
                row.append(angles["pitch"])
                row.append(angles["roll"])
            else:
                row.append(None)
                row.append(None)

        append_row(CSV_FILE, row)
        count += 1
        sleep(DELAY_SEC)

    return count


# -----------------------------
# Menu
# -----------------------------

def print_menu():
    print("\nMenu:")
    print("  1) Initialize sensors")
    print("  2) Capture: sitting_good")
    print("  3) Capture: sitting_bad")
    print("  4) Capture: standing_good")
    print("  5) Capture: standing_bad")
    print("  6) Show CSV info")
    print("  7) Quit")


def main():
    """
    Menu-driven data collection. Run each label multiple times
    across different sittings for a robust dataset.
    """
    print("Posture Coach — Data Collection")
    print(f"Capturing {CAPTURE_SEC}s per session at {1/DELAY_SEC:.0f} samples/sec\n")

    initialized = False

    while True:
        print_menu()
        choice = input("\nChoose an option (1-7): ").strip()

        if choice == "1":
            try:
                setup()
                initialized = True
                print("Sensors ready.\n")
            except Exception as e:
                print(f"Error during setup: {e}")

        elif choice in ("2", "3", "4", "5") and not initialized:
            print("\nPlease initialize sensors first (option 1).\n")

        elif choice in ("2", "3", "4", "5"):
            label = LABELS[int(choice) - 2]
            print(f"\nLabel: {label}")
            print(f"Hold the position and stay still. Capturing for {CAPTURE_SEC:.0f} seconds...\n")
            try:
                n = capture_session(label)
                print(f"Saved {n} samples to {CSV_FILE}\n")
            except Exception as e:
                print(f"Error during capture: {e}")

        elif choice == "6":
            print(f"\nCSV file: {CSV_FILE}")
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, "r") as f:
                    row_count = sum(1 for _ in f) - 1  # subtract header
                print(f"Rows collected so far: {row_count}\n")
            else:
                print("No data collected yet.\n")

        elif choice == "7":
            print("Done.")
            break

        else:
            print("\nInvalid choice. Pick 1-7.\n")


if __name__ == "__main__":
    main()