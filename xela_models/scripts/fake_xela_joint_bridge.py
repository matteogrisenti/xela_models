#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class FakeXelaJointBridge(Node):
    def __init__(self):
        super().__init__('fake_xela_joint_bridge')
        
        # Manteniamo lo stesso topic del tuo bridge reale
        self.joint_pub = self.create_publisher(JointState, '/dot_xela_joint_states', 10)
        self.timer = self.create_timer(0.1, self.publish_fake_joints) # Pubblica a 10 Hz
        
        # Generiamo i nomi dei 48 giunti come nel tuo codice originale
        self.joint_names = []
        for i in range(1, 17):
            self.joint_names.extend([
                f'1_4x4_{i}_joint_x',
                f'1_4x4_{i}_joint_y',
                f'1_4x4_{i}_joint_z'
            ])

    def publish_fake_joints(self):
        joint_msg = JointState()
        joint_msg.header.stamp = self.get_clock().now().to_msg()
        joint_msg.name = self.joint_names
        
        # Pubblichiamo 0.0 per tutti i 48 giunti
        joint_msg.position = [0.0] * 48
        
        self.joint_pub.publish(joint_msg)

def main(args=None):
    rclpy.init(args=args)
    node = FakeXelaJointBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()