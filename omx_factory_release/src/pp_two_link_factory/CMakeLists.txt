cmake_minimum_required(VERSION 3.8)
project(pp_two_link_factory)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  urdf
  config
  DESTINATION share/${PROJECT_NAME}
)

install(FILES README.md DESTINATION share/${PROJECT_NAME})

install(PROGRAMS scripts/controller_state_guard.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME controller_state_guard)

ament_package()
