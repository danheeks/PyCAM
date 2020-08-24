#include <stdafx.h>

#include <Python.h>

#ifdef WIN32

#include "windows.h"
#include <GL/gl.h>
#include <GL/glu.h>

#else
#include </usr/include/GL/gl.h>
#include </usr/include/GL/glu.h>
#endif


#include <boost/python.hpp>
#include <boost/python/module.hpp>
#include <boost/python/class.hpp>

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

int GetNcCodeBlockType()
{
	return CNCCodeBlock::m_type;
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

void CNCCodeAddBlock(CNCCode& object, CNCCodeBlock& block)
{
	object.m_blocks.push_back(&block);
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

void CncCodeBlockAddText(CNCCodeBlock& object, ColouredText& text) {
	object.m_text.push_back(text);
}

void CncCodeBlockAddPath(CNCCodeBlock& object, ColouredPath& path) {
	object.m_line_strips.push_back(path);
}

HeeksColor CncColor(ColorEnum i)
{
	return CNCCode::Color(i);
}

ColorEnum CNCCodeGetTextColor(const std::string& s)
{
	return CNCCode::GetColor(s.c_str());
}

void SetMultiplier(double multiplier)
{
	CNCCodeBlock::multiplier = multiplier;
}

CNCCodeBlock* NewNcCodeBlock()
{
	return new CNCCodeBlock();
}

ColouredPath* NewColouredPath()
{
	return new ColouredPath();
}

ColouredText* NewColouredText()
{
	return new ColouredText();
}

PathLine* NewPathLine()
{
	return new PathLine();
}

PathArc* NewPathArc()
{
	return new PathArc();
}

CNCCodeViewport* NewNcCodeViewport()
{
	return new CNCCodeViewport();
}

void AddPathObject(ColouredPath& path, PathObject& path_object)
{
	path.m_points.push_back(&path_object);
}

	BOOST_PYTHON_MODULE(cam) {

		boost::python::class_<CNCCode, boost::python::bases<HeeksObj>, boost::noncopyable>("NcCode")
			.def(boost::python::init<CNCCode>())
			.def("GetHighlightedBlock", &CNCCode::GetHighlightedBlock, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("SetHighlightedBlock", &CNCCode::SetHighlightedBlock)
			.def("GetBlocks", &CncCodeGetBlocks)
			.def("DestroyGLLists", &CNCCode::DestroyGLLists)
			.def("AddBlock", &CNCCodeAddBlock)
			;

		boost::python::class_<CNCCodeBlock, boost::python::bases<HeeksObj>, boost::noncopyable>("NcCodeBlock")
			.def(boost::python::init<CNCCodeBlock>())
			.def_readwrite("to_pos", &CNCCodeBlock::m_to_pos)
			.def_readwrite("from_pos", &CNCCodeBlock::m_from_pos)
			.def_readwrite("line_number", &CNCCodeBlock::m_line_number)
			.def("GetTexts", &CncCodeBlockGetTexts)
			.def("Text", &CncCodeBlockGetText)
			.def("GetLineStrips", &CncCodeBlockGetLineStrips)
			.def("AddText", &CncCodeBlockAddText)
			.def("AddPath", &CncCodeBlockAddPath)
			;

		boost::python::class_<ColouredText, boost::noncopyable>("ColouredText")
			.def(boost::python::init<ColouredText>())
			.def_readwrite("str", &ColouredText::m_str)
			.def_readwrite("color_type", &ColouredText::m_color_type)
			;

		boost::python::class_<ColouredPath, boost::noncopyable>("ColouredPath")
			.def(boost::python::init<ColouredPath>())
			.def_readwrite("color_type", &ColouredPath::m_color_type)
			.def("AddPathObject", &AddPathObject)
			;

		boost::python::class_<PathObject, boost::noncopyable>("PathObject", boost::python::no_init)
			.def_readwrite("point", &PathObject::m_point)
			;

		boost::python::class_<PathLine, boost::python::bases<PathObject>, boost::noncopyable>("PathLine")
			.def(boost::python::init<PathLine>())
			;

		boost::python::class_<PathArc, boost::python::bases<PathObject>, boost::noncopyable>("PathArc")
			.def(boost::python::init<PathArc>())
			.def_readwrite("c", &PathArc::m_c)
			.def_readwrite("radius", &PathArc::m_radius)
			.def_readwrite("dir", &PathArc::m_dir)
			;

		boost::python::class_<CNCCodeViewport, boost::noncopyable>("CNCCodeViewport", boost::python::no_init)
			.def("SetSize", &CNCCodeViewport::SetSize)
			.def("GetWidth", &CNCCodeViewport::GetWidth)
			.def("GetHeight", &CNCCodeViewport::GetHeight)
			.def("Render", &CNCCodeViewport::Render)
			.def("GetCurrentLine", &CNCCodeViewport::GetCurrentLine)
			.def("SetCurrentLine", &CNCCodeViewport::SetCurrentLine)
			.def("GetSelectedLine", &CNCCodeViewport::GetSelectedLine)
			.def("SelectLine", &CNCCodeViewport::SelectLine)
			.def("SetNcCode", &CNCCodeViewport::SetNcCode)
			.def("GetLinesPerPage", &CNCCodeViewport::GetLinesPerPage)
			.def("GetNumberOfLines", &CNCCodeViewport::GetNumberOfLines)
			.def("GetPixelsPerLine", &CNCCodeViewport::GetPixelsPerLine)
			.def("SetPixelsPerLine", &CNCCodeViewport::SetPixelsPerLine)
			.def("GetBlockAtLine", &CNCCodeViewport::GetBlockAtLine, boost::python::return_value_policy<boost::python::reference_existing_object>());
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
		boost::python::def("GetNcCodeBlockType", GetNcCodeBlockType);
		boost::python::def("SetNcCodeBlockType", SetNcCodeBlockType);
		boost::python::def("CncColor", CncColor);
		boost::python::def("GetTextColor", CNCCodeGetTextColor);
		boost::python::def("SetMultiplier", SetMultiplier);
		boost::python::def("NewNcCodeBlock", NewNcCodeBlock, boost::python::return_value_policy<boost::python::reference_existing_object>());
		boost::python::def("NewColouredPath", NewColouredPath, boost::python::return_value_policy<boost::python::reference_existing_object>());
		boost::python::def("NewColouredText", NewColouredText, boost::python::return_value_policy<boost::python::reference_existing_object>());
		boost::python::def("NewPathLine", NewPathLine, boost::python::return_value_policy<boost::python::reference_existing_object>());
		boost::python::def("NewPathArc", NewPathArc, boost::python::return_value_policy<boost::python::reference_existing_object>());
		boost::python::def("NewNcCodeViewport", NewNcCodeViewport, boost::python::return_value_policy<boost::python::reference_existing_object>());
	}
