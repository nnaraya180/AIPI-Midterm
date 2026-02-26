"""
imu_reader.py
===================================
Reads pitch and roll angles from all 10 MPU6050 IMUs:
  - 8 IMUs via TCA9548A multiplexer (channels 0-7)
  - 2 IMUs directly on I2C bus (0x68, 0x69)

Using MPU6050 and TCA9548A channel switching via smbus2 and adafruit_mpu6050 for sensor reads.

Returns a dictionary of {segment_name: {"pitch": float, "roll": float}}
"""

import smbus2
import board
import busio
import adafruit_mpu6050
from math import atan2, sqrt, pi


# -----------------------------
# Configuration
# -----------------------------

TCA_ADDRESS = 0x70      # TCA9548A multiplexer

# Map each TCA channel to a body part
TCA_CHANNEL_MAP = {
    0: "left_thigh",
    1: "left_calf",
    2: "right_calf",
    3: "right_thigh",
    4: "upper_mid_back",
    5: "upper_back",
    6: "right_shoulder",
    7: "left_shoulder",
}

DIRECT_ADDRESS_MAP = {
    0x68: "lower_mid_back",
    0x69: "lower_back",
}


# -----------------------------
# Globals
# -----------------------------

i2c = None          
bus = None          # smbus2 bus (used only for TCA9548A channel switching)


# -----------------------------
# Setup
# -----------------------------

def setup():
    """
    Initialize both I2C buses.
    - smbus2 bus for TCA9548A channel switching
    - adafruit busio I2C for reading MPU6050 sensors
    """
    global i2c, bus

    bus = smbus2.SMBus(1)                       
    i2c = busio.I2C(board.SCL, board.SDA)       
    print("I2C buses initialized.")



# TCA9548A Channel Control

def select_channel(channel):
    """
    Tell the TCA9548A to open a specific channel (0-7).

    Writes a byte where only the bit corresponding to the channel is set.
     - channel 0 -> 0b00000001 (1)
     - channel 1 -> 0b00000010 (2)
     - channel 2 -> 0b00000100 (4)
     - ...
     - channel 7 -> 0b10000000 (128)
    """
    bus.write_byte(TCA_ADDRESS, 1 << channel)


def close_channels():
    """Close all TCA9548A channels"""
    bus.write_byte(TCA_ADDRESS, 0)


# -----------------------------
# Angle Computation
# Pitch and roll calculations based on raw accelerometer data
# -----------------------------

def compute_angles(ax, ay, az):
    """
    Compute pitch and roll in degrees from raw accelerometer values.

    Pitch: rotation around the left-right axis (forward/backward tilt)
    Roll:  rotation around the front-back axis (side tilt)

    Returns:
        (pitch, roll) as floats in degrees
    """
    pitch = atan2(-ax, sqrt(ay * ay + az * az)) * (180.0 / pi)
    roll  = atan2(ay, az) * (180.0 / pi)
    return pitch, roll


# -----------------------------
# Reading Sensors
# -----------------------------

def read_tca_imu(channel):
    """
    Select a TCA channel, read the MPU6050 on that channel, return angles.

    Returns:
        {"pitch": float, "roll": float} or None on failure
    """
    try:
        select_channel(channel)
        mpu = adafruit_mpu6050.MPU6050(i2c)
        ax, ay, az = mpu.acceleration
        pitch, roll = compute_angles(float(ax), float(ay), float(az))
        close_channels()
        return {"pitch": round(pitch, 3), "roll": round(roll, 3)}
    except Exception as e:
        close_channels()
        print(f"Error reading TCA channel {channel}: {e}")
        return None


def read_direct_imu(address):
    """
    Read an MPU6050 connected directly on I2C (not through TCA).

    Returns:
        {"pitch": float, "roll": float} or None on failure
    """
    try:
        mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
        ax, ay, az = mpu.acceleration
        pitch, roll = compute_angles(float(ax), float(ay), float(az))
        return {"pitch": round(pitch, 3), "roll": round(roll, 3)}
    except Exception as e:
        print(f"Error reading direct IMU at address {hex(address)}: {e}")
        return None


# -----------------------------
# Main Read — returns all 10 IMUs
# -----------------------------

def read_all_imus():
    """
    Read all 10 IMUs and return a dictionary of segment angles.

    Returns:
        dict: {segment_name: {"pitch": float, "roll": float}}
              Value is None if that sensor failed to read.

    Example:
        {
            "left_thigh":     {"pitch": -2.1, "roll": 0.4},
            "lower_back":     {"pitch": 12.3, "roll": 1.1},
            ...
        }
    """
    readings = {}

    # Read 8 IMUs through TCA9548A
    for channel, segment in TCA_CHANNEL_MAP.items():
        readings[segment] = read_tca_imu(channel)

    # Read 2 direct IMUs
    for address, segment in DIRECT_ADDRESS_MAP.items():
        readings[segment] = read_direct_imu(address)

    return readings


# -----------------------------
# Menu
# -----------------------------

def print_menu():
    print("\nMenu:")
    print("  1) Initialize I2C buses")
    print("  2) Read all IMUs (single snapshot)")
    print("  3) Stream all IMUs (Ctrl+C to stop)")
    print("  4) Quit")


def main():
    """Menu-driven test for the IMU reader. Same structure as class labs."""
    from time import sleep

    print("Posture Coach — IMU Reader Utility")

    while True:
        print_menu()
        choice = input("\nChoose an option (1-4): ").strip()

        if choice == "1":
            try:
                setup()
            except Exception as e:
                print(f"Error during setup: {e}")

        elif choice == "2":
            if i2c is None:
                print("\nPlease initialize buses first (option 1).\n")
                continue
            readings = read_all_imus()
            print()
            for segment, angles in readings.items():
                print(f"  {segment:<20}: {angles}")

        elif choice == "3":
            if i2c is None:
                print("\nPlease initialize buses first (option 1).\n")
                continue
            print("\nStreaming... Ctrl+C to stop.\n")
            try:
                while True:
                    readings = read_all_imus()
                    print("-" * 40)
                    for segment, angles in readings.items():
                        print(f"  {segment:<20}: {angles}")
                    sleep(1.0)
            except KeyboardInterrupt:
                print("\nStopped.\n")

        elif choice == "4":
            print("Done.")
            break

        else:
            print("\nInvalid choice. Pick 1-4.\n")


if __name__ == "__main__":
    main()