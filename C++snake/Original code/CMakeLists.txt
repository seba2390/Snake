cmake_minimum_required(VERSION 3.22)
project(Snake)
set(CMAKE_CXX_STANDARD 17)

find_package(Eigen3 3.4)
find_package(Boost)

include_directories(Include)   # For header files of static library
add_subdirectory(src)          # For main.cpp and library *.cpp files