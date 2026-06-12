#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from xela_server_ros2.msg import SensStream
from cv_bridge import CvBridge

import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class XelaImageViz(Node):
    def __init__(self):
        super().__init__('xela_image_viz')
        
        # Subscription to the sensor data topic
        self.subscription = self.create_subscription(
            SensStream,
            '/xServTopic',
            self.sensor_callback,
            10
        )

        # Baseline for tara calculation
        self.baseline = None
        self.calibration_frames = 60
        self.calibration_buffer = []
        
        # Publisher for the grid image
        self.image_pub = self.create_publisher(Image, '/xela_grid_image', 10)
        self.bridge = CvBridge()
        
        # Matplotlib setup for the 4x4 grid visualization
        self.max_z = 0.1            # force value that corresponds to the most intense color 
        self.noise_filter = 0.05    # forces below this threshold will be considered as zero to reduce visual noise 

        self.grid_x = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
        self.grid_y = [3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0]
        
        self.fig, self.ax = plt.subplots(figsize=(6, 6), dpi=100) 
        self.ax.set_xlim(-0.5, 3.5)
        self.ax.set_ylim(-0.5, 3.5)
        self.ax.set_xticks([]) 
        self.ax.set_yticks([])
        self.ax.set_aspect('equal') 
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')

        custom_colors = ["#00008B", "#ADD8E6", "#FFFFFF", "#FFD700", "#8B4513"]
        self.cmap = mcolors.LinearSegmentedColormap.from_list("BlueWhiteBrown", custom_colors)
        self.norm = mcolors.TwoSlopeNorm(vmin=-self.max_z, vcenter=0.0, vmax=self.max_z)

        self.rects = []
        self.text_artists = []
        
        for i in range(16):
            rect = plt.Rectangle((self.grid_x[i]-0.5, self.grid_y[i]-0.5), 1, 1, facecolor='white', edgecolor='#333333', linewidth=2)
            self.ax.add_patch(rect)
            self.rects.append(rect)

            # Circle with taxel number inside
            circle_x = self.grid_x[i] - 0.35
            circle_y = self.grid_y[i] + 0.35
            circle = plt.Circle((circle_x, circle_y), radius=0.12, facecolor='white', edgecolor='black', linewidth=1, zorder=5)
            self.ax.add_patch(circle)
            self.ax.text(circle_x, circle_y, str(i + 1), color='black', ha='center', va='center', fontsize=8, fontweight='bold', zorder=6)

            # Text for live values
            t = self.ax.text(self.grid_x[i], self.grid_y[i], "X: 0.00\nY: 0.00\nZ: 0.00", 
                             color='black', ha='center', va='center', 
                             fontsize=10, family='monospace', fontweight='bold', zorder=4)
            self.text_artists.append(t)

        # Baseline for tara calculation Flag
        self.baseline = None

    def sensor_callback(self, msg):
        if len(msg.sensors) > 0 and len(msg.sensors[0].forces) == 16:
            forces = msg.sensors[0].forces
            
            # Calibration Phase
            if self.baseline is None:
                # Save the current frame of forces in the calibration buffer
                current_frame_forces = [(f.x, f.y, f.z) for f in forces]
                self.calibration_buffer.append(current_frame_forces)
                
                if len(self.calibration_buffer) < self.calibration_frames:
                    if len(self.calibration_buffer) % 10 == 0:
                        self.get_logger().info(f"Calibration in progress... {len(self.calibration_buffer)}/{self.calibration_frames}")
                    return
                else:
                    # Once we have enough frames, calculate the baseline as the average of the buffered frames
                    buffer_array = np.array(self.calibration_buffer) # Shape: (30, 16, 3)
                    self.baseline = np.mean(buffer_array, axis=0).tolist() # Shape: (16, 3)
                    self.get_logger().info("Tara calcolata con successo facendo la media su 30 frame!")
                    return
            
            # Update the visualization based on the forces compared to the baseline
            for i in range(16):
                base_x, base_y, base_z = self.baseline[i]
                
                delta_x = forces[i].x - base_x
                delta_y = forces[i].y - base_y
                delta_z = forces[i].z - base_z
                
                if abs(delta_x) < self.noise_filter: delta_x = 0.0
                if abs(delta_y) < self.noise_filter: delta_y = 0.0
                if abs(delta_z) < self.noise_filter: delta_z = 0.0
                
                # Set the background color of the cell based on the Z force (pressure)
                self.rects[i].set_facecolor(self.cmap(self.norm(delta_z)))
                
                # Update the text with the live force values
                text_str = f"X: {delta_x:.2f}\nY: {delta_y:.2f}\nZ: {delta_z:.2f}"
                self.text_artists[i].set_text(text_str)

            # Redraw the canvas to update the visualization
            self.fig.canvas.draw()
            
            # Convert the Matplotlib figure to a NumPy array
            img_array = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
            img_array = img_array.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
            
            # Convert to ROS 2 Image message and publish
            img_msg = self.bridge.cv2_to_imgmsg(img_array, encoding="rgb8")
            self.image_pub.publish(img_msg)

def main(args=None):
    rclpy.init(args=args)
    node = XelaImageViz()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()