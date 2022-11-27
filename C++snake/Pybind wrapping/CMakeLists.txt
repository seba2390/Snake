cmake_minimum_required(VERSION 3.4)
#set (CMAKE_CXX_STANDARD 11)
project(SnakeLogicProject)


find_package(Eigen3 3.4)
find_package(Boost)

add_subdirectory(pybind11)
pybind11_add_module(SnakeLogic main.cpp)
#target_link_libraries(SnakeLogic Boost::boost)
