cmake_minimum_required(VERSION 3.8)
project(pp_factory_world)

find_package(ament_cmake REQUIRED)

install(DIRECTORY worlds DESTINATION share/${PROJECT_NAME})

ament_package()
