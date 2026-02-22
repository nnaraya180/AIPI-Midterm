"""
test_flex.py
------------
Menu-based flex sensor tester (MCP3008 CH0).
"""

from time import sleep, time
from flex_mcp3008 import setup_mcp3008, read_flex_raw, read_flex_voltage


def print_once():
    raw = read_flex_raw()
    v = read_flex_voltage()
    print(f"\nFLEX CH0: raw={raw}  voltage={v:.3f} V\n")


def stream(seconds=10.0, delay=0.10):
    end_t = time() + seconds
    try:
        while time() < end_t:
            raw = read_flex_raw()
            v = read_flex_voltage()
            print(f"raw={raw:5d}  V={v:.3f}")
            sleep(delay)
    except KeyboardInterrupt:
        print("\nStopped.\n")


def _safe_float(prompt, default):
    s = input(prompt).strip()
    try:
        return float(s)
    except Exception:
        return float(default)


def print_menu():
    print("\nMenu:")
    print("  1) Setup MCP3008 (CE0)")
    print("  2) Read one sample")
    print("  3) Stream (live)")
    print("  4) Quit")


def main():
    print("Flex Sensor Test (MCP3008 CH0)\n")

    while True:
        print_menu()
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            setup_mcp3008(cs_pin="D8")  # CE0
            print("\nMCP3008 configured on CE0.\n")

        elif choice == "2":
            print_once()

        elif choice == "3":
            seconds = _safe_float("Seconds (default 10): ", 10.0)
            delay = _safe_float("Delay (default 0.10): ", 0.10)
            stream(seconds=seconds, delay=delay)

        elif choice == "4":
            break

        else:
            print("\nInvalid choice.\n")

    print("\nDone.")


if __name__ == "__main__":
    main()
