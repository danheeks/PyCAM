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

void SetNcCodeBlockType(int type)
{
	CNCCodeBlock::m_type = type;
}

boost::python::list CncCodeGetBlocks(CNCCode& object) {
	boost::python::list return_list;

	for (std::list<CNCCodeBlock*>::const_iterator It = object.m_blocks.begin(); It != object.m_blocks.end(); It++)
	{
		CNCCodeBlock* block = *It;
		return_list.append(boost::python::ptr<CNCCodeBlock*>(block));
	}

	return return_list;
}

std::wstring CncCodeBlockGetText(CNCCodeBlock& object)
{
	std::wstring str;
	for (std::list<ColouredText>::iterator It = object.m_text.begin(); It != object.m_text.end(); It++)
	{
		ColouredText& text = *It;
		str.append(text.m_str);
	}

	return str;
}

boost::python::list CncCodeBlockGetTexts(CNCCodeBlock& object) {
	boost::python::list return_list;

	for (std::list<ColouredText>::iterator It = object.m_text.begin(); It != object.m_text.end(); It++)
	{
		ColouredText& text = *It;
		return_list.append(boost::python::ptr<ColouredText*>(&text));
	}

	return return_list;
}

boost::python::list CncCodeBlockGetLineStrips(CNCCodeBlock& object) {
	boost::python::list return_list;

	for (std::list<ColouredPath>::iterator It = object.m_line_strips.begin(); It != object.m_line_strips.end(); It++)
	{
		ColouredPath& line_strip = *It;
		return_list.append(boost::python::ptr<ColouredPath*>(&line_strip));
	}

	return return_list;
}

HeeksColor CncColor(ColorEnum i)
{
	return CNCCode::Color(i);
}

	BOOST_PYTHON_MODULE(cam) {

		boost::python::class_<CNCCode, boost::python::bases<HeeksObj>, boost::noncopyable>("NcCode")
			.def(boost::python::init<CNCCode>())
			.def("GetHighlightedBlock", &CNCCode::GetHighlightedBlock, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("SetHighlightedBlock", &CNCCode::SetHighlightedBlock)
			.def("GetBlocks", &CncCodeGetBlocks)
			.def("DestroyGLLists", &CNCCode::DestroyGLLists)
			;

		boost::python::class_<CNCCodeBlock, boost::python::bases<HeeksObj>, boost::noncopyable>("NcCodeBlock")
			.def(boost::python::init<CNCCodeBlock>())
			.def_readwrite("formatted", &CNCCodeBlock::m_formatted)
			.def_readwrite("to_pos", &CNCCodeBlock::m_to_pos)
			.def_readwrite("from_pos", &CNCCodeBlock::m_from_pos)
			.def("GetTexts", &CncCodeBlockGetTexts)
			.def("Text", &CncCodeBlockGetText)
			.def("GetLineStrips", &CncCodeBlockGetLineStrips)
			;

		boost::python::class_<ColouredText, boost::noncopyable>("ColouredText")
			.def(boost::python::init<ColouredText>())
			.def_readwrite("str", &ColouredText::m_str)
			.def_readwrite("color_type", &ColouredText::m_color_type)
			;

		boost::python::enum_<ColorEnum>("ColorEnum")
		.value("COLOR_DEFAULT_TYPE", ColorDefaultType)
			.value("COLOR_BLOCK_TYPE", ColorBlockType)
			.value("COLOR_MISC_TYPE", ColorMiscType)
			.value("COLOR_PROGRAM_TYPE", ColorProgramType)
			.value("COLOR_TOOL_TYPE", ColorToolType)
			.value("COLOR_COMMENT_TYPE", ColorCommentType)
			.value("COLOR_VARIABLE_TYPE", ColorVariableType)
			.value("COLOR_PREP_TYPE", ColorPrepType)
			.value("COLOR_AXIS_TYPE", ColorAxisType)
			.value("COLOR_RAPID_TYPE", ColorRapidType)
			.value("COLOR_FEED_TYPE", ColorFeedType)
			.value("MAX_COLOR_TYPES", MaxColorTypes)
			;

		boost::python::def("SetResPath", SetResPath);
		boost::python::def("ClearNcCodeColors", CNCCode::ClearColors);
		boost::python::def("AddNcCodeColor", AddNcCodeColor);
		boost::python::def("SetApp", SetApp);
		boost::python::def("GetNcCodeType", GetNcCodeType);
		boost::python::def("SetNcCodeType", SetNcCodeType);
		boost::python::def("SetNcCodeBlockType", SetNcCodeBlockType);
		boost::python::def("CncColor", CncColor);

	}
