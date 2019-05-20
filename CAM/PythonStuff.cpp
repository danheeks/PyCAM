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

#include "NCCode.h"
#include "strconv.h"

std::wstring cam_dir;

CApp* theApp = NULL;

void SetResPath(const std::wstring& dir)
{
	cam_dir = dir;
}

void AddNcCodeColor(const std::wstring& name, const HeeksColor& col)
{
	CNCCode::AddColor(Ttc(name.c_str()), col);
}

void SetApp(CApp* app)
{
	theApp = app;
}

int GetNcCodeType()
{
	return CNCCode::m_type;
}

void SetNcCodeType(int type)
{
	CNCCode::m_type = type;
}

	BOOST_PYTHON_MODULE(cam) {

		boost::python::class_<CNCCode, boost::python::bases<HeeksObj>, boost::noncopyable>("NcCode")
			.def(boost::python::init<CNCCode>())
			;

		boost::python::def("SetResPath", SetResPath);
		boost::python::def("ClearNcCodeColors", CNCCode::ClearColors);
		boost::python::def("AddNcCodeColor", AddNcCodeColor);
		boost::python::def("SetApp", SetApp);
		boost::python::def("GetNcCodeType", GetNcCodeType);
		boost::python::def("SetNcCodeType", SetNcCodeType);

	}
