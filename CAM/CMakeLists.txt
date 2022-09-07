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

include_directories("/usr/share/PyCAD/Geom")
include_directories("/usr/share/PyCAD/CAD")


# this defines the source-files for library
set(CAM_SRC
    /usr/share/PyCAD/Geom/Arc.cpp
    /usr/share/PyCAD/Geom/Area.cpp
    /usr/share/PyCAD/Geom/AreaClipper.cpp
    /usr/share/PyCAD/Geom/AreaOrderer.cpp
    /usr/share/PyCAD/Geom/AreaPocket.cpp
    /usr/share/PyCAD/Geom/Circle.cpp
    /usr/share/PyCAD/Geom/clipper.cpp
    /usr/share/PyCAD/Geom/Construction.cpp
    /usr/share/PyCAD/Geom/Curve.cpp
    /usr/share/PyCAD/Geom/Finite.cpp
    /usr/share/PyCAD/Geom/Matrix.cpp
    /usr/share/PyCAD/Geom/Offset.cpp
    /usr/share/PyCAD/CAD/HeeksColor.cpp
    /usr/share/PyCAD/CAD/HeeksFont.cpp
    /usr/share/PyCAD/CAD/HeeksObj.cpp
    /usr/share/PyCAD/CAD/Picking.cpp
    /usr/share/PyCAD/CAD/Property.cpp
    /usr/share/PyCAD/CAD/strconv.cpp
    /usr/share/PyCAD/CAD/tinystr.cpp
    /usr/share/PyCAD/CAD/tinyxml.cpp
    /usr/share/PyCAD/CAD/tinyxmlerror.cpp
    /usr/share/PyCAD/CAD/tinyxmlparser.cpp
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

# this figures out where to install the Python modules
execute_process(
    COMMAND python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
    OUTPUT_VARIABLE Python_site_packages
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

# strip away /usr/local/ because that is what CMAKE_INSTALL_PREFIX is set to
# also, since there is no leading "/", it makes ${Python_site_packages} a relative path.
STRING(REGEX REPLACE "/usr/local/(.*)$" "\\1" Python_site_packages "${Python_site_packages}" )
STRING(REGEX REPLACE "/usr/(.*)$" "\\1" Python_site_packages "${Python_site_packages}" )

message(STATUS "Python module will be installed to: " ${CMAKE_INSTALL_PREFIX}/${Python_site_packages})

# this installs the python library
install(
    TARGETS cam
    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/${Python_site_packages}
)

