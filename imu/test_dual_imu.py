from time import sleep
from dual_imu import (
    read_accel_both,
    read_gyro_both,
    imu_summary,
)

print("Streaming dual IMU data...\n")

while True:
    acc_a, acc_b = read_accel_both()
    gyr_a, gyr_b = read_gyro_both()

    print(imu_summary(acc_a, gyr_a, "IMU A"))
    print(imu_summary(acc_b, gyr_b, "IMU B"))
    print("-" * 50)

    sleep(0.3)