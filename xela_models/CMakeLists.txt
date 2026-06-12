cmake_minimum_required(VERSION 3.8)
project(xela_models)

# Search ROS2 build tools
find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf mesh rviz launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()