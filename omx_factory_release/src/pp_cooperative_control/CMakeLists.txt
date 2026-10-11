cmake_minimum_required(VERSION 3.8)
project(pp_cooperative_control)

# Binary-only distribution. The original PPV18 observer/control implementation
# is precompiled for Linux x86_64 / ROS 2 Jazzy; no research source is shipped.
find_package(ament_cmake REQUIRED)

set(PAPER_EXECUTABLES
  pp_start_sync
  pp_observer1 pp_observer2 pp_observer3
  pp_observer4 pp_observer5 pp_observer6
  pp_tracking1 pp_tracking2 pp_tracking3
  pp_tracking4 pp_tracking5 pp_tracking6
)

foreach(executable IN LISTS PAPER_EXECUTABLES)
  set(binary "${CMAKE_CURRENT_SOURCE_DIR}/bin/${executable}")
  if(NOT EXISTS "${binary}")
    message(FATAL_ERROR "Missing prebuilt paper binary: ${binary}")
  endif()
  install(PROGRAMS "${binary}" DESTINATION lib/${PROJECT_NAME})
endforeach()

# Original paper launch settings are preserved unchanged.
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.launch.py")

# Public, infrastructure-only compatibility relay (no research algorithm source).
install(PROGRAMS scripts/pp_final_path_relay.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME pp_final_path_relay)

ament_package()
