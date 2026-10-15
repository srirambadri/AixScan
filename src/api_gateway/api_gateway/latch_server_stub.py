"""
Latch service stub
-------------------
A stand-in for the real latch node so scan_listener can be tested end to
end before that node exists. It accepts every request and touches no
hardware. Drop it once the real server is wired up.

    ros2 run api_gateway latch_server_stub
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class LatchServerStub(Node):
    def __init__(self):
        super().__init__('latch_server_stub')

        self.declare_parameter('service_name', 'latch_request')
        service_name = self.get_parameter('service_name').value

        self.srv = self.create_service(SetBool, service_name, self.handle_request)
        self.get_logger().info(f"Stub latch service up on '{service_name}'")

    def handle_request(self, request, response):
        self.get_logger().info(f"Latch requested (data={request.data})")
        response.success = True
        response.message = 'stub: no hardware actuated'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = LatchServerStub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
