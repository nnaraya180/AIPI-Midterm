"""
deploy.py
================================
Loads the trained model package and runs real-time posture classification
using all 10 IMUs. Two modes selected via physical LCD menu:

  A: Check Now  — single snapshot, 2 beeps = good, 1 beep = bad
  B: Continuous — loops every SAMPLE_INTERVAL seconds, short beep on bad
                  posture with COOLDOWN_SEC cooldown between beeps

Hardware:
  - 10x MPU6050 IMUs (via imu_reader.py)
  - Active buzzer on GPIO 18
  - 16x2 I2C LCD
  - Navigate button on GPIO 27 (cycles A <-> B)
  - Select button on GPIO 22  (confirms selection / exits continuous mode)
"""

import joblib
from time import sleep, time
from gpiozero import Buzzer, Button
from lcd_i2c import LCD_I2C

from imu_reader import setup, read_all_imus


# -----------------------------
# Configuration
# -----------------------------

MODEL_FILE      = "model_package.joblib"

BUZZER_PIN      = 18
NAV_PIN         = 27        # navigate button — cycles A <-> B on LCD menu
SEL_PIN         = 22        # select button  — confirms choice / exits continuous mode

LCD_ADDRESS     = 39        
LCD_COLS        = 16
LCD_ROWS        = 2

BEEP_SHORT      = 0.1       
BEEP_PAUSE      = 0.2       

SAMPLE_INTERVAL = 1.0       # seconds between readings in continuous mode
COOLDOWN_SEC    = 60.0      # seconds between bad posture alerts in continuous mode


# -----------------------------
# Globals
# -----------------------------

model_package   = None
model           = None
feature_cols    = None
encoder         = None

buzzer          = None
lcd             = None
btn_nav         = None      # navigate button (GPIO 27)
btn_sel         = None      # select button  (GPIO 22)


# -----------------------------
# Setup
# -----------------------------

def setup_hardware():
    """
    Initialize IMU buses, buzzer, LCD, and buttons.

    Buzzer uses gpiozero.Buzzer 
    Button uses gpiozero.Button
    """
    global buzzer, lcd, btn_nav, btn_sel

    setup()     # IMU I2C buses from imu_reader.py

    buzzer  = Buzzer(BUZZER_PIN)

    btn_nav = Button(NAV_PIN, pull_up=True)
    btn_sel = Button(SEL_PIN, pull_up=True)

    lcd = LCD_I2C(LCD_ADDRESS, LCD_COLS, LCD_ROWS)
    lcd.backlight.on()

    print("Hardware ready.\n")


def load_model():
    """
    Load the model package saved by train_model.py.
    Recycled: same joblib load + package unpacking as wk3day1_lab4.py
    """
    global model_package, model, feature_cols, encoder

    model_package = joblib.load(MODEL_FILE)
    model         = model_package["model"]
    feature_cols  = model_package["feature_cols"]
    encoder       = model_package["encoder"]

    print(f"Model loaded. Labels: {list(encoder.classes_)}\n")


# -----------------------------
# Buzzer helpers
# -----------------------------

def beep(n):
    """
    Beep n times with a short pause between each.
    Same on/off pattern as led.on()/led.off() in wk5day2_lab4.py.
    """
    for _ in range(n):
        buzzer.on()
        sleep(BEEP_SHORT)
        buzzer.off()
        sleep(BEEP_PAUSE)


# -----------------------------
# LCD helpers
# -----------------------------

def lcd_show(line0, line1=""):
    """Clear the LCD and write two lines of text."""
    lcd.clear()
    lcd.cursor.setPos(0, 0)
    lcd.write_text(line0[:LCD_COLS])
    lcd.cursor.setPos(1, 0)
    lcd.write_text(line1[:LCD_COLS])


def lcd_draw_menu(cursor_pos):
    """
    Draw the two-option menu with a blinking cursor on the selected row.
    cursor_pos 0 = Check Now highlighted, 1 = Continuous highlighted.

    The LCD blink cursor acts as the selector indicator — same blink
    usage as wk1 LCD lab.
    """
    lcd.clear()
    lcd.blink.on()

    if cursor_pos == 0:
        line0 = "> A: Check Now "
        line1 = "  B: Continuous"
    else:
        line0 = "  A: Check Now "
        line1 = "> B: Continuous"

    lcd.cursor.setPos(0, 0)
    lcd.write_text(line0[:LCD_COLS])
    lcd.cursor.setPos(1, 0)
    lcd.write_text(line1[:LCD_COLS])

    # Park the blinking cursor at the start of the selected row
    lcd.cursor.setPos(cursor_pos, 0)


# -----------------------------
# LCD physical menu
# btn_nav cycles the cursor, btn_sel confirms selection
# -----------------------------

def run_lcd_menu():
    """
    Show the two-option menu on the LCD and wait for button input.
    Navigate button (GPIO 27) toggles cursor between A and B.
    Select button  (GPIO 22) confirms and returns the chosen mode.

    Returns:
        "check"      if A selected
        "continuous" if B selected
    """
    cursor = 0      # 0 = Check Now, 1 = Continuous
    lcd_draw_menu(cursor)

    while True:
        if btn_nav.is_pressed:
            # Toggle between the two options
            cursor = 1 if cursor == 0 else 0
            lcd_draw_menu(cursor)
            sleep(0.3)      

        if btn_sel.is_pressed:
            lcd.blink.off()
            sleep(0.2)      
            return "check" if cursor == 0 else "continuous"

        sleep(0.05)   


# -----------------------------
# Inference
# -----------------------------

def predict_posture():
    """
    Read all IMUs, build a feature row, and return the predicted label string.
    Returns None if any sensor read fails.

    Building the feature row follows the same SEGMENTS order as
    data_collection.py so the column order matches what the model was trained on.
    """
    import pandas as pd

    readings = read_all_imus()

    row = {}
    for col in feature_cols:

        seg   = "_".join(col.split("_")[:-1])
        angle = col.split("_")[-1]

        angles = readings.get(seg)
        if angles is None:
            return None     # sensor failure — skip this sample
        row[col] = angles[angle]

    X_row        = pd.DataFrame([row], columns=feature_cols)
    pred_encoded = model.predict(X_row)[0]
    pred_label   = encoder.inverse_transform([pred_encoded])[0]
    return pred_label


# -----------------------------
# Modes
# -----------------------------

def check_now():
    """
    Single snapshot mode.
    2 beeps = good posture, 1 beep = bad posture.
    Shows result on LCD.
    """
    lcd_show("Checking...", "Hold still")
    label = predict_posture()

    if label is None:
        lcd_show("Sensor error", "Try again")
        print("Sensor read failed.\n")
        return

    is_good = "good" in label

    lcd_show(label, "Good!" if is_good else "Fix posture")
    print(f"Detected: {label}")

    if is_good:
        beep(2)
    else:
        beep(1)


def continuous_mode():
    """
    Continuous monitoring mode. Samples every SAMPLE_INTERVAL seconds.
    Beeps once on bad posture detection with a COOLDOWN_SEC cooldown
    before the next alert.
    Press select button (GPIO 22) to stop and return to LCD menu.

    Recycled: same loop + exit pattern as run_live_inference() in wk3day1_lab5.py
    New: btn_sel.is_pressed replaces KeyboardInterrupt as the exit trigger
    """
    last_alert = 0.0    # timestamp of the last bad posture beep

    lcd_show("Monitoring...", "SEL to stop")
    print("Continuous mode running. Press select button to stop.\n")

    while True:
        # Exit back to menu when select button is pressed
        if btn_sel.is_pressed:
            sleep(0.2) 
            lcd_show("Stopped", "")
            print("Stopped continuous mode.\n")
            return

        label = predict_posture()

        if label is None:
            print("Sensor read failed — skipping sample.")
            sleep(SAMPLE_INTERVAL)
            continue

        is_good = "good" in label
        now     = time()

        print(f"Posture: {label}")
        lcd_show(label, "OK" if is_good else "Fix posture")

        # Only beep if bad posture and cooldown has expired
        if not is_good and (now - last_alert) >= COOLDOWN_SEC:
            beep(1)
            last_alert = now

        sleep(SAMPLE_INTERVAL)


# -----------------------------
# Main
# -----------------------------

def main():
    """
    Startup: initialize hardware and load model, then hand control
    to the physical LCD menu. Loops back to the menu after each mode finishes.
    """
    print("Posture Coach — Live Inference\n")

    # Step 1 — hardware
    try:
        setup_hardware()
    except Exception as e:
        print(f"Hardware setup error: {e}")
        return

    # Step 2 — model
    try:
        load_model()
    except FileNotFoundError:
        print(f"ERROR: {MODEL_FILE} not found. Train the model first.")
        return

    # Startup splash — same idea as wk1 LCD lab
    lcd_show("Posture Coach", "Starting...")
    sleep(1.5)

    # Step 3 — physical menu loop
    while True:
        choice = run_lcd_menu()

        if choice == "check":
            check_now()
            sleep(2.0)      # leave result on LCD before returning to menu

        elif choice == "continuous":
            continuous_mode()


if __name__ == "__main__":
    main()