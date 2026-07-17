cmake_minimum_required(VERSION 3.8)
project(xela_models)

# Search ROS2 build tools
find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf mesh rviz launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/xela_image_viz.py
  scripts/xela_joint_bridge.py
  scripts/fake_xela_joint_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()