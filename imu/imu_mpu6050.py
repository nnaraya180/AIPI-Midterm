"""
imu_mpu6050.py
--------------
Small, reusable MPU6050 helper functions (class-style).
Each function does ONE thing so you can reuse them later.

Install:
    pip install adafruit-circuitpython-mpu6050
"""

import time 
import math
from math import degrees, atan2, sqrt


# We'll create these once and reuse them
i2c = None
mpu = None

def setup_mpu():
    """
    Initialize the I2C bus and MPU6050 sensor (once).
    Store the sensor in the global variable `mpu`.
    """
    
    global i2c, mpu

    if mpu is not None:
        return
    
    import board
    import busio
    import adafruit_mpu6050

    i2c = busio.I2C(board.SCL, board.SDA)
    mpu = adafruit_mpu6050.MPU6050(i2c)

def read_accel():
    """
    Read ONE accelerometer measurement from the MPU6050.
    """
    setup_mpu()

    ax, ay, az = mpu.acceleration
    return ax, ay, az

def read_gyro():
    """
    Read ONE gyroscope measurement from the MPU6050.
    """
    setup_mpu()

    gx, gy, gz = mpu.gyro
    return gx, gy, gz

def accel_magnitude(ax, ay, az):
    """
    Compute the magnitude of acceleration from x/y/z components.
    """
    return math.sqrt(ax**2 + ay**2 + az**2)

def gyro_magnitude(gx, gy, gz):
    """
    Compute the magnitude of gyroscope from x/y/z components.
    """
    return math.sqrt(gx**2 + gy**2 + gz**2)

def pitch_roll_from_accel(ax, ay, az):
    """
    Compute pitch and roll from accelerometer.

    Returns:
        (pitch_deg, roll_deg)
    """
    pitch = degrees(atan2(-ax, sqrt(ay*ay + az*az)))
    roll  = degrees(atan2(ay, az))
    return pitch, roll


def accel_features(ax, ay, az):
    """
    Convenience bundle for accel features.

    Returns:
        dict with:
            magnitude
            pitch
            roll
    """
    mag = accel_magnitude(ax, ay, az)
    pitch, roll = pitch_roll_from_accel(ax, ay, az)

    return {
        "accel_mag": mag,
        "pitch_deg": pitch,
        "roll_deg": roll,
        "ax": ax,
        "ay": ay,
        "az": az,
    }


def gyro_features(gx, gy, gz):
    """
    Convenience bundle for gyro features.
    """
    mag = gyro_magnitude(gx, gy, gz)
    return {
        "gyro_mag": mag,
        "gx": gx,
        "gy": gy,
        "gz": gz,
    }