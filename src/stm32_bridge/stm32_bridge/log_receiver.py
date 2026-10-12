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
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 115200)
        port = self.get_parameter('serial_port').value
        baud = self.get_parameter('baud_rate').value

        # Single serial port instance for both reading and writing
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.get_logger().info(f"Opened {port} at {baud} baud")
        self.timer = self.create_timer(0.01, self.read_logs)
        
        self.log_file = open("stm32_received_log.txt", "w", encoding="utf-8")

    def command_callback(self, msg):
        # Write command from ROS 2 topic out to STM32 over serial
        command_str = msg.data.strip() + '\r\n'
        self.ser.write(command_str.encode('utf-8'))
        self.get_logger().info(f"Sent to STM32: {msg.data}")

    def read_logs(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8', errors='ignore')
            if line:
                self.log_file.write(line)
                self.log_file.flush()
                
                out_msg = String()
                out_msg.data = line.strip()
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