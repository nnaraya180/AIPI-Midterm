"""
imu_mpu6050_dual.py
-------------------
Dual MPU6050 helper functions (class-style).

Extends your existing single-IMU helpers
to support two sensors: 0x68 and 0x69
"""

import math
from math import degrees, atan2, sqrt

# Globals
i2c = None
mpu_a = None  # 0x68
mpu_b = None  # 0x69


def setup_dual_mpu():
    global i2c, mpu_a, mpu_b

    if i2c is not None:
        return

    import board, busio
    import adafruit_mpu6050

    i2c = busio.I2C(board.SCL, board.SDA)
    
    mpu_a = adafruit_mpu6050.MPU6050(i2c, address=0x68)
    mpu_b = adafruit_mpu6050.MPU6050(i2c, address=0x69)


def read_accel_both():
    setup_dual_mpu()
    ax1, ay1, az1 = mpu_a.acceleration
    ax2, ay2, az2 = mpu_b.acceleration
    return (ax1, ay1, az1), (ax2, ay2, az2)


def read_gyro_both():
    setup_dual_mpu()
    gx1, gy1, gz1 = mpu_a.gyro
    gx2, gy2, gz2 = mpu_b.gyro
    return (gx1, gy1, gz1), (gx2, gy2, gz2)


def accel_magnitude(ax, ay, az):
    return math.sqrt(ax**2 + ay**2 + az**2)

def gyro_magnitude(gx, gy, gz):
    return math.sqrt(gx**2 + gy**2 + gz**2)

def pitch_roll_from_accel(ax, ay, az):
    pitch = degrees(atan2(-ax, sqrt(ay*ay + az*az)))
    roll  = degrees(atan2(ay, az))
    return pitch, roll


def round_vec(v, n=2):
    return [round(x, n) for x in v]


def imu_summary(accel, gyro, label="IMU"):
    ax, ay, az = accel
    gx, gy, gz = gyro

    amag = accel_magnitude(ax, ay, az)
    gmag = gyro_magnitude(gx, gy, gz)
    pitch, roll = pitch_roll_from_accel(ax, ay, az)

    acc_r = round_vec(accel, 2)
    gyr_r = round_vec(gyro, 2)

    return (
        f"{label} | ACC: {acc_r} | mag={amag:.2f} "
        f"| pitch={pitch:.1f}° roll={roll:.1f}°\n"
        f"      GYR: {gyr_r} | mag={gmag:.2f}"
    )