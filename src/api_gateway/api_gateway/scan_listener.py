"""
RVM Scan Listener (ROS 2 service client)
-----------------------------------------
Most barcode/QR scanners used in RVMs emulate a USB keyboard: when a
code is scanned, the scanner "types" the code's text followed by Enter.

On each scan this node does two things at once:
  1. opens the kiosk browser on the user-detail form, passing the
     scanned code as session_id (same as the pre-ROS version), and
  2. calls the `latch_request` service (std_srvs/SetBool) with
     data=True to ask for a latch.

The node that serves `latch_request` and drives the hardware is
separate - this one only asks.

Run this on the machine's controller (Raspberry Pi / mini-PC) that the
scanner is plugged into, alongside the web form:

    ros2 run api_gateway scan_listener
"""

import time
import webbrowser

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class ScanListener(Node):
    def __init__(self):
        super().__init__('scan_listener')

        # Overridable at launch:
        #   ros2 run api_gateway scan_listener --ros-args -p base_url:=http://192.168.1.10:5000/
        self.declare_parameter('base_url', 'http://localhost:5000/')
        self.declare_parameter('service_name', 'latch_request')
        self.declare_parameter('min_code_length', 4)
        self.declare_parameter('service_timeout', 5.0)
        self.declare_parameter('debounce_sec', 1.0)

        self.base_url = self.get_parameter('base_url').value
        service_name = self.get_parameter('service_name').value
        self.min_code_length = self.get_parameter('min_code_length').value
        self.service_timeout = self.get_parameter('service_timeout').value
        self.debounce_sec = self.get_parameter('debounce_sec').value

        self.client = self.create_client(SetBool, service_name)
        self.get_logger().info(
            f"Waiting for scans: form at {self.base_url}, latch requests to '{service_name}'")

    def handle_scan(self, scan_code):
        """Open the form for this scan and ask the latch service to open."""
        # Browser first: webbrowser.open returns immediately, so the user
        # sees the form while the latch request is still in flight.
        self.open_form(scan_code)
        self.request_latch(scan_code)

    def open_form(self, scan_code):
        url = f"{self.base_url}?session_id={scan_code}"
        self.get_logger().info(f"Scan detected: {scan_code} -> opening {url}")
        webbrowser.open(url, new=2)  # new=2 opens in a new browser tab

    def request_latch(self, scan_code):
        """Ask the latch service to open. Returns True if it accepted."""
        if not self.client.wait_for_service(timeout_sec=self.service_timeout):
            self.get_logger().error(
                f"No latch service after {self.service_timeout}s - scan {scan_code} dropped")
            return False

        request = SetBool.Request()
        request.data = True

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=self.service_timeout)

        if not future.done():
            # Drop the call rather than let a late response land on the next scan
            self.client.remove_pending_request(future)
            self.get_logger().error(f"Latch service timed out for scan {scan_code}")
            return False

        response = future.result()
        if response.success:
            self.get_logger().info(f"Scan {scan_code} -> latch granted: {response.message}")
        else:
            self.get_logger().warning(f"Scan {scan_code} refused: {response.message}")
        return response.success


def main(args=None):
    rclpy.init(args=args)
    node = ScanListener()
    try:
        while rclpy.ok():
            # A HID scanner sends characters + Enter, so a plain
            # input() call captures a full scanned code as one line.
            scanned_code = input().strip()

            # Ignore noise / stray keystrokes
            if len(scanned_code) < node.min_code_length:
                continue

            node.handle_scan(scanned_code)

            # Small debounce so a jittery scanner doesn't fire twice
            time.sleep(node.debounce_sec)
    except (EOFError, KeyboardInterrupt):
        node.get_logger().info('Stopped.')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
