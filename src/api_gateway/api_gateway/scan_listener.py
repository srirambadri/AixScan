"""
RVM Scan Listener
------------------
Most barcode/QR scanners used in RVMs emulate a USB keyboard: when a
code is scanned, the scanner "types" the code's text followed by Enter.

This script listens for that input and opens the default web browser
to the user-detail form, passing the scanned code as session_id so
the submission can be linked back to that specific scan/session.

Opening the form is what puts the scan on ROS: app.py publishes on
/scan_event when it serves the page. Nothing here talks to ROS.

Run this on the machine's controller (Raspberry Pi / mini-PC) that has
a display attached, alongside app.py.

Usage:
    ros2 run api_gateway scan_listener
"""

import webbrowser
import time

# Change this to wherever your Flask app is actually reachable from
# the machine's kiosk browser (localhost if same device, or the
# controller's IP if the browser runs elsewhere).
BASE_URL = "http://localhost:5000/"

# Minimum code length to filter out accidental keystrokes/noise
MIN_CODE_LENGTH = 4


def open_form_for_scan(scan_code: str):
    url = f"{BASE_URL}?session_id={scan_code}"
    print(f"[scan_listener] Scan detected: {scan_code} -> opening {url}")
    webbrowser.open(url, new=2)  # new=2 opens in a new browser tab


def listen():
    print("[scan_listener] Waiting for scans... (Ctrl+C to stop)")
    while True:
        try:
            # A HID scanner sends characters + Enter, so a plain
            # input() call captures a full scanned code as one line.
            scanned_code = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[scan_listener] Stopped.")
            break

        if len(scanned_code) >= MIN_CODE_LENGTH:
            open_form_for_scan(scanned_code)
        else:
            # Ignore noise / stray keystrokes
            continue

        # Small debounce so a jittery scanner doesn't fire twice
        time.sleep(1)


def main():
    """Entry point for `ros2 run api_gateway scan_listener`."""
    listen()


if __name__ == "__main__":
    main()
