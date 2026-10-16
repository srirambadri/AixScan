import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

class STM32BridgeNode(Node):
    def __init__(self):
        super().__init__('stm32_bridge_node')
        
        # Publisher for incoming logs from STM32
        self.log_publisher = self.create_publisher(String, 'stm32_logs', 10)
        
        # Subscriber for outgoing commands to STM32
        self.subscription = self.create_subscription(
            String,
            'command',
            self.command_callback,
            10
        )
        
        # Serial settings, overridable at launch:
        #   ros2 run stm32_bridge log_receiver --ros-args -p serial_port:=/dev/ttyACM0
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        port = self.get_parameter('serial_port').value
        baud = self.get_parameter('baud_rate').value

        # Single serial port instance for both reading and writing
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.get_logger().info(f"Opened {port} at {baud} baud")
        self.timer = self.create_timer(0.01, self.read_logs)

        # Bytes arrive mid-line, so hold the tail until its terminator shows up
        self.rx_buffer = bytearray()

        self.log_file = open("stm32_received_log.txt", "w", encoding="utf-8")

    def command_callback(self, msg):
        # Write command from ROS 2 topic out to STM32 over serial
        command_str = msg.data.strip() + '\r\n'
        self.ser.write(command_str.encode('utf-8'))
        self.get_logger().info(f"Sent to STM32: {msg.data}")

    def is_garbage(self, line):
        """True for lines that aren't real board output.

        A baud mismatch turns clean text into bytes that either fail to decode
        (U+FFFD after errors='replace') or decode to control/box-drawing junk,
        so a line is rejected on either count.
        """
        if '�' in line:
            return True
        # Tabs are legitimate in column-formatted board output, but
        # str.isprintable() rejects them
        printable = sum(1 for ch in line if ch.isprintable() or ch == '\t')
        return printable < len(line) * 0.8

    def read_logs(self):
        # read(in_waiting) never blocks, unlike readline(), which would stall
        # this callback - and the /command subscription with it - for up to
        # the port timeout whenever a line is still only half there.
        waiting = self.ser.in_waiting
        if waiting:
            self.rx_buffer.extend(self.ser.read(waiting))

        # Accept \r\n, \n or bare \r as line endings
        self.rx_buffer = self.rx_buffer.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

        while b'\n' in self.rx_buffer:
            raw, _, rest = self.rx_buffer.partition(b'\n')
            self.rx_buffer = bytearray(rest)

            # errors='replace' marks undecodable bytes so is_garbage can spot
            # them, rather than 'ignore' quietly deleting them
            line = raw.decode('utf-8', errors='replace').strip()
            if not line:
                continue

            if self.is_garbage(line):
                # Keep it out of the topic and the log file, but don't go
                # silent about it - silence here looks exactly like a dead port
                self.get_logger().warning(
                    f"Dropped {len(raw)} unreadable bytes - wrong baud_rate?",
                    throttle_duration_sec=5.0)
                continue

            self.log_file.write(line + '\n')
            self.log_file.flush()

            out_msg = String()
            out_msg.data = line
            self.log_publisher.publish(out_msg)

    def destroy_node(self):
        self.log_file.close()
        self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = STM32BridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Runs on Ctrl-C too, so the log file is flushed and the port released
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()