import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

class STM32LogReceiver(Node):
    def __init__(self):
        super().__init__('stm32_log_receiver')
        self.publisher_ = self.create_publisher(String, 'stm32_logs', 10)
        
        # Update with your serial port and baud rate
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
        self.timer = self.create_timer(0.01, self.read_logs)
        
        # Open a local file to save the incoming log stream
        self.log_file = open("stm32_received_log.txt", "w", encoding="utf-8")

    def read_logs(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8', errors='ignore')
            if line:
                # Save to local text file
                self.log_file.write(line)
                self.log_file.flush()
                
                # Publish to ROS 2 topic
                msg = String()
                msg.data = line.strip()
                self.publisher_.publish(msg)

    def destroy_node(self):
        self.log_file.close()
        self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = STM32LogReceiver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()