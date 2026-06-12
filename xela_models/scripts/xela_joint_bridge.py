#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from xela_server_ros2.msg import SensStream
from xela_server_ros2.msg import SensorFull 

class XelaJointBridge(Node):
    def __init__(self):
        super().__init__('xela_joint_bridge')
        
        # Subscribtion to the sensor data topic
        self.subscription = self.create_subscription(
            SensStream,
            '/xServTopic',
            self.sensor_callback,
            10
        )
        
        # Publisher for the dot joint states of the sensor
        self.joint_pub = self.create_publisher(JointState, '/dot_xela_joint_states', 10)
        
        # Generate the joint names based on the expected format in the URDF
        self.joint_names = []
        for i in range(1, 17):
            self.joint_names.extend([
                f'1_4x4_{i}_joint_x',
                f'1_4x4_{i}_joint_y',
                f'1_4x4_{i}_joint_z'
            ])

        # Parameters to scale the raw sensor data to joint positions 
        # (these may need tuning based on the actual sensor range and desired visualization)
        self.scale_x = 0.005
        self.scale_y = 0.005
        self.scale_z = -0.005

    def sensor_callback(self, msg):
        # Protection 1: Ensure we have at least one sensor data in the message
        if len(msg.sensors) > 0:
            
            # Extract the first sensor data (assuming we are only interested in one sensor for now)
            sensor_data = msg.sensors[0]
            
            # Protection 2: Ensure we have exactly 16 force readings (for the 4x4 grid)
            if len(sensor_data.forces) == 16:
                joint_msg = JointState()
                joint_msg.header.stamp = self.get_clock().now().to_msg()
                joint_msg.name = self.joint_names
                
                positions = []
                for force in sensor_data.forces:
                    positions.extend([
                        force.x * self.scale_x,
                        force.y * self.scale_y,
                        force.z * self.scale_z
                    ])
                    
                joint_msg.position = positions
                
                # Publish the joint states
                self.joint_pub.publish(joint_msg)

def main(args=None):
    rclpy.init(args=args)
    node = XelaJointBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()