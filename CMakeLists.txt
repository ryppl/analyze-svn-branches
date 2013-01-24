cmake_minimum_required(VERSION 2.8)

add_subdirectory(svndumpparse)

find_package(Boost  REQUIRED)

include_directories(
  ${CMAKE_CURRENT_LIST_DIR} 
  ${SUBVERSION_INCLUDE_DIRS}
  ${APR_INCLUDE_DIRS} 
  ${Boost_INCLUDE_DIRS}
  svndumpparse
  )

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  list(APPEND CMAKE_CXX_FLAGS "-Werror")
endif()

add_executable(analyze-svn-branches
  main.cpp svn_branch_analyzer.cpp
)

target_link_libraries(analyze-svn-branches
  svndumpparse
  ${SUBVERSION_LIBRARIES} ${APR_LIBRARY}
)



