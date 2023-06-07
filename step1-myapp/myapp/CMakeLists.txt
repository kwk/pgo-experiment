cmake_minimum_required(VERSION 3.13.4)

project(myapp)

add_executable(myapp myapp.cpp)
target_link_libraries(myapp)
install(TARGETS myapp RUNTIME DESTINATION bin)