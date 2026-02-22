"""
test_imu_helpers.py
-------------------
Menu-based tester for imu_mpu6050.py

Verifies:
- sensor reads
- magnitudes
- pitch/roll
- feature bundles
"""

import time
from imu_mpu6050 import (
    setup_mpu,
    read_accel,
    read_gyro,
    accel_magnitude,
    gyro_magnitude,
    pitch_roll_from_accel,
    accel_features,
    gyro_features,
)


# ============================
# SMALL TEST FUNCTIONS
# ============================

def test_raw_accel():
    ax, ay, az = read_accel()
    print("\nRAW ACCEL:")
    print(f"ax={ax:+.3f}, ay={ay:+.3f}, az={az:+.3f}")


def test_raw_gyro():
    gx, gy, gz = read_gyro()
    print("\nRAW GYRO:")
    print(f"gx={gx:+.3f}, gy={gy:+.3f}, gz={gz:+.3f}")


def test_magnitudes():
    ax, ay, az = read_accel()
    gx, gy, gz = read_gyro()

    amag = accel_magnitude(ax, ay, az)
    gmag = gyro_magnitude(gx, gy, gz)

    print("\nMAGNITUDES:")
    print(f"Accel magnitude ≈ {amag:.3f} m/s^2 (should be ~9.8 when still)")
    print(f"Gyro magnitude  ≈ {gmag:.3f} rad/s (should be near 0 when still)")


def test_pitch_roll():
    ax, ay, az = read_accel()
    pitch, roll = pitch_roll_from_accel(ax, ay, az)

    print("\nPITCH / ROLL:")
    print(f"Pitch: {pitch:+.2f} deg")
    print(f"Roll : {roll:+.2f} deg")
    print("Tip: tilt the IMU and rerun to see changes.")


def test_feature_bundles():
    ax, ay, az = read_accel()
    gx, gy, gz = read_gyro()

    a = accel_features(ax, ay, az)
    g = gyro_features(gx, gy, gz)

    print("\nACCEL FEATURES:")
    for k, v in a.items():
        print(f"{k:12s}: {v}")

    print("\nGYRO FEATURES:")
    for k, v in g.items():
        print(f"{k:12s}: {v}")


def stream_live(seconds=5, delay=0.2):
    print("\nStreaming live data...\n")
    end = time.time() + seconds

    while time.time() < end:
        ax, ay, az = read_accel()
        gx, gy, gz = read_gyro()

        pitch, roll = pitch_roll_from_accel(ax, ay, az)

        print(
            f"ACC[{ax:+.2f},{ay:+.2f},{az:+.2f}] "
            f"GYR[{gx:+.2f},{gy:+.2f},{gz:+.2f}] "
            f"P={pitch:+.1f} R={roll:+.1f}"
        )
        time.sleep(delay)


# ============================
# MENU (CLASS STYLE)
# ============================

def print_menu():
    print("\nIMU TEST MENU")
    print("1) Setup MPU")
    print("2) Raw accel")
    print("3) Raw gyro")
    print("4) Magnitudes")
    print("5) Pitch/Roll")
    print("6) Feature bundles")
    print("7) Live stream (5s)")
    print("8) Quit")


def main():
    print("Testing imu_mpu6050 helpers...\n")

    while True:
        print_menu()
        choice = input("Choose (1-8): ").strip()

        if choice == "1":
            setup_mpu()
            print("MPU initialized.")

        elif choice == "2":
            test_raw_accel()

        elif choice == "3":
            test_raw_gyro()

        elif choice == "4":
            test_magnitudes()

        elif choice == "5":
            test_pitch_roll()

        elif choice == "6":
            test_feature_bundles()

        elif choice == "7":
            stream_live()

        elif choice == "8":
            break

        else:
            print("Invalid choice.")

    print("Done.")


if __name__ == "__main__":
    main()