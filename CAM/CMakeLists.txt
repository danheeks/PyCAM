project(cam)

cmake_minimum_required(VERSION 2.8.3)

FIND_PACKAGE(Boost 1.73.0 COMPONENTS python3)
FIND_PACKAGE(PythonInterp 3)
FIND_PACKAGE(PythonLibs 3 REQUIRED)

message(STATUS "PYTHON_LIBRARIES = ${PYTHON_LIBRARIES}")
message(STATUS "PYTHON_EXECUTABLE = ${PYTHON_EXECUTABLE}")
message(STATUS "PYTHON_INCLUDE_DIRS = ${PYTHON_INCLUDE_DIRS}")
message(STATUS "Boost_LIBRARIES = ${Boost_LIBRARIES}")

ENABLE_TESTING()
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})
LINK_LIBRARIES(${Boost_LIBRARIES} ${PYTHON_LIBRARIES}) # Deprecated but so convenient!

add_definitions( -Wall -Wno-deprecated -Werror -pedantic-errors -fPIC -Wno-psabi)

option(BUILD_TYPE
  "Build type: Release=ON/Debug=OFF  " ON)

add_definitions(-DUNICODE)

if (BUILD_TYPE)
    MESSAGE(STATUS " CMAKE_BUILD_TYPE = Release")
    set(CMAKE_BUILD_TYPE Release)
endif(BUILD_TYPE)

if (NOT BUILD_TYPE)
    MESSAGE(STATUS " CMAKE_BUILD_TYPE = Debug")
    set(CMAKE_BUILD_TYPE Debug)
endif(NOT BUILD_TYPE)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

find_package( OpenGL REQUIRED )

if (NOT WIN32)
    message("opengl directory is")
    message(${OPENGL_INCLUDE_DIR})

    include_directories(OPENGL_INCLUDE_DIR)
endif (NOT WIN32)

include_directories("../../PyCAD/Geom")
include_directories("../../PyCAD/CAD")

# this defines the source-files for library
set(CAM_SRC
    ../../PyCAD/Geom/Arc.cpp
    ../../PyCAD/Geom/Area.cpp
    ../../PyCAD/Geom/AreaClipper.cpp
    ../../PyCAD/Geom/AreaOrderer.cpp
    ../../PyCAD/Geom/AreaPocket.cpp
    ../../PyCAD/Geom/Circle.cpp
    ../../PyCAD/Geom/clipper.cpp
    ../../PyCAD/Geom/Construction.cpp
    ../../PyCAD/Geom/Curve.cpp
    ../../PyCAD/Geom/Finite.cpp
    ../../PyCAD/Geom/Matrix.cpp
    ../../PyCAD/Geom/Offset.cpp
    ../../PyCAD/Geom/Arc.cpp
    ../../PyCAD/CAD/HeeksColor.cpp
    ../../PyCAD/CAD/HeeksObj.cpp
    ../../PyCAD/CAD/Picking.cpp
    ../../PyCAD/CAD/Property.cpp
    ../../PyCAD/CAD/strconv.cpp
    ../../PyCAD/CAD/tinystr.cpp
    ../../PyCAD/CAD/tinyxml.cpp
    ../../PyCAD/CAD/tinyxmlerror.cpp
    ../../PyCAD/CAD/tinyxmlparser.cpp
    NCCode.cpp
    PythonStuff.cpp
)


# this defines the headers
if(DEFINED INCLUDE_INSTALL_DIR)
    set(includedir ${INCLUDE_INSTALL_DIR})
else(DEFINED INCLUDE_INSTALL_DIR)
    set(INCLUDE_INSTALL_DIR include)
    set(includedir ${CMAKE_INSTALL_PREFIX}/${INCLUDE_INSTALL_DIR})
endif(DEFINED INCLUDE_INSTALL_DIR)

# include directories

# this part allow to support multi-arch
# ie. Debian builder sets correctly the target path according to architecture
# e.g. /usr/lib/i386-linux-gnu, /usr/lib/x86_64-linux-gnu
# TODO: Support this feature
#if(DEFINED CMAKE_INSTALL_LIBDIR)
#    set(CMAKE_INSTALL_LIBDIR ${CMAKE_INSTALL_LIBDIR})
#else(DEFINED CMAKE_INSTALL_LIBDIR)
#    set(CMAKE_INSTALL_LIBDIR ${CMAKE_INSTALL_PREFIX}/lib)
#endif(DEFINED CMAKE_INSTALL_LIBDIR)


# this makes the Python module
  add_library(
      cam
      MODULE
      ${CAM_SRC}
  )

target_link_libraries(cam ${Boost_LIBRARIES} ${OPENGL_LIBRARIES} ${GLUT_LIBRARY})
set_target_properties(cam PROPERTIES PREFIX "") 
