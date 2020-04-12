#include "stdafx.h"


#include <Python.h>

#ifdef WIN32

#include "windows.h"
#include <GL/gl.h>
#include <GL/glu.h>

#else
#include </usr/include/GL/gl.h>
#include </usr/include/GL/glu.h>
#endif


#include <boost/progress.hpp>
#include <boost/timer.hpp>
#include <boost/foreach.hpp>
#include <boost/python.hpp>
#include <boost/python/module.hpp>
#include <boost/python/class.hpp>
#include <boost/python/wrapper.hpp>
#include <boost/python/call.hpp>

#include "octree.hpp"
#include "isosurface.hpp"
#include "marching_cubes.hpp"
#include "strconv.h"

std::wstring sim_dir;

CApp* theApp = NULL;

void SetResPath(const std::wstring& dir)
{
	sim_dir = dir;
}

void SetApp(CApp* app)
{
	theApp = app;
}

	BOOST_PYTHON_MODULE(sim) {
		boost::python::class_<Octree>("Octree", boost::python::no_init)
			.def(boost::python::init<double, unsigned int, GLVertex*, GLData*>())
			.def("init", &Octree::init)
			.def("sum", static_cast< void (Octree::*)(const Volume* vol) >(&Octree::sum))
			.def("diff", static_cast< void (Octree::*)(const Volume* vol) >(&Octree::diff))
			.def("get_root_scale", &Octree::get_root_scale)
			.def("get_leaf_scale", &Octree::leaf_scale)
			;

		boost::python::class_<GLVertex>("GLVertex")
			.def(boost::python::init<GLVertex>())
			.def(boost::python::init<GLfloat, GLfloat, GLfloat>())
			.def_readwrite("x", &GLVertex::x)
			.def_readwrite("y", &GLVertex::y)
			.def_readwrite("z", &GLVertex::z)
			;

		boost::python::class_<GLData>("GLData")
			.def(boost::python::init<GLData>())
			.def("swap", &GLData::swap)
			.def("draw", &GLData::draw)
			; 

		boost::python::class_<IsoSurfaceAlgorithm, boost::noncopyable>("IsoSurfaceAlgorithm", boost::python::no_init)
			.def("updateGL", static_cast< void (IsoSurfaceAlgorithm::*)(void) >(&IsoSurfaceAlgorithm::updateGL))
			; 

		boost::python::class_<MarchingCubes, boost::python::bases<IsoSurfaceAlgorithm>>("MarchingCubes", boost::python::no_init)
			.def(boost::python::init<GLData*, Octree*>())
			;

		boost::python::class_<Volume, boost::noncopyable>("Volume", boost::python::no_init)
			.def("setColor", &Volume::setColor)
			.def("Render", &Volume::Render)
			;

		boost::python::class_<SphereVolume, boost::python::bases<Volume>>("SphereVolume")
			.def(boost::python::init<SphereVolume>())
			.def("setRadius", &SphereVolume::setRadius)
			.def("setCenter", &SphereVolume::setCenter)
			;

		boost::python::class_<RectVolume2, boost::python::bases<Volume>>("RectVolume", boost::python::no_init)
			.def(boost::python::init<GLfloat, GLfloat, GLfloat, GLfloat, GLfloat, GLfloat>())
			.def("calcBB", &RectVolume2::calcBB)
			;

		boost::python::class_<CylinderVolume, boost::python::bases<Volume>>("CylinderVolume")
			.def(boost::python::init<CylinderVolume>())
			.def("calcBB", &CylinderVolume::calcBB)
			.def("dist", &CylinderVolume::dist)
			.def("setRadius", &CylinderVolume::setRadius)
			.def("setLength", &CylinderVolume::setLength)
			.def("setCenter", &CylinderVolume::setCenter)
			.def("setRotationCenter", &CylinderVolume::setRotationCenter)
			.def("setAngle", &CylinderVolume::setAngle)
			.def("Render", &CylinderVolume::Render)
			;

		
		boost::python::def("SetResPath", SetResPath);
		boost::python::def("SetApp", SetApp);
	}
