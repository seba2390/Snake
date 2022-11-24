set(OUTPUT_EXENAME Snake)
set(EXENAME Snake-exe)


add_executable(${EXENAME} main.cpp)
target_link_libraries(${EXENAME} MyProgram Boost::boost)
target_link_libraries(${EXENAME} MyProgram Eigen3::Eigen)
set_target_properties(${EXENAME} PROPERTIES OUTPUT_NAME ${OUTPUT_EXENAME})