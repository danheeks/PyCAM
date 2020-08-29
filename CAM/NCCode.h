// NCCode.h
/*
 * Copyright (c) 2009, Dan Heeks
 * This program is released under the BSD license. See the file COPYING for
 * details.
 */

// This is an object that can go in the tree view as a child of a program.
// It contains lists of NC Code blocks, each one is a line of an NC file, but also contains drawing items
// The text of this is shown in the "output" window.

#pragma once

#include "HeeksObj.h"
#include "HeeksColor.h"
#include "geometry.h"

#include <list>
#include <map>

enum ColorEnum{
	ColorDefaultType,
	ColorBlockType,
	ColorMiscType,
	ColorProgramType,
	ColorToolType,
	ColorCommentType,
	ColorVariableType,
	ColorPrepType,
	ColorAxisType,
	ColorRapidType,
	ColorFeedType,
	MaxColorTypes
};

class ColouredText
{
public:
	std::wstring m_str;
	ColorEnum m_color_type;
	ColouredText():m_color_type(ColorDefaultType){}

	void WriteXML(TiXmlNode *root);
	void ReadFromXMLElement(TiXmlElement* pElem);
};

class PathObject{
public:
	typedef enum {
		eLine = 0,
		eArc
	} eType_t;

public:
	virtual ~PathObject() {}

	Point3d m_point;
	PathObject(){m_point = Point3d(0.0, 0.0, 0.0);}
	virtual int GetType() = 0; // 0 - line, 1 - arc
	virtual void GetBox(CBox &box){box.Insert(m_point.getBuffer());}

	void WriteBaseXML(TiXmlElement *element);

	virtual void WriteXML(TiXmlNode *root) = 0;
	virtual void ReadFromXMLElement(TiXmlElement* pElem) = 0;
	virtual void glVertices(){}
	virtual PathObject *MakeACopy(void)const = 0;
};

class PathLine : public PathObject{
public:
	int GetType(){return int(PathObject::eLine);}
	void WriteXML(TiXmlNode *root);
	void ReadFromXMLElement(TiXmlElement* pElem);
	void glVertices();
	PathObject *MakeACopy(void)const{return new PathLine(*this);}
};

class PathArc : public PathObject{
public:
	Point3d m_c; // defined relative to previous point ( span start point )
	double m_radius;
	int m_dir; // 1 - anti-clockwise, -1 - clockwise
	PathArc(){m_c = Point3d(0,0,0); m_dir = 1;}
	int GetType(){return int(PathObject::eArc);}
	void WriteXML(TiXmlNode *root);
	void ReadFromXMLElement(TiXmlElement* pElem);
	void glVertices();
	void Interpolate(const unsigned int number_of_points, std::list<Point3d>& points ) const;

	PathObject *MakeACopy(void)const{return new PathArc(*this);}

	void GetBox(CBox &box);
	bool IsIncluded(const Point3d &pnt);
	void SetFromRadius();
};

class ColouredPath
{
public:
	ColorEnum m_color_type;
	std::list< PathObject* > m_points;
	ColouredPath():m_color_type(ColorRapidType){}
	ColouredPath(const ColouredPath& c);
	~ColouredPath(){Clear();}

	const ColouredPath &operator=(const ColouredPath& c);

	void Clear();
	void glCommands(bool no_color);
	void GetBox(CBox &box);
	void WriteXML(TiXmlNode *root);
	void ReadFromXMLElement(TiXmlElement* pElem);
};

class CNCCodeBlock:public HeeksObj
{
public:
	std::list<ColouredText> m_text;
	std::list<ColouredPath> m_line_strips;
	int m_tool_number;
	long m_from_pos, m_to_pos; // position of block in text ctrl
	static double multiplier;
	static int m_type;
	int m_line_number;

	CNCCodeBlock() :m_from_pos(-1), m_to_pos(-1), m_line_number(-1){}

	// HeeksObj's virtual functions
	int GetType()const{ return m_type; }
	const wchar_t* GetTypeString(void) const { return L"NC Code Block"; }
	const wchar_t* GetXMLTypeString()const{ return L"ncblock"; }
	HeeksObj *MakeACopy(void)const;
	void glCommands(bool select, bool marked, bool no_color);
	void GetBox(CBox &box);
	void WriteToXML(TiXmlElement *element);
	void ReadFromXML(TiXmlElement *element);
	void AppendText(std::wstring& str);
	void GetGripperPositionsTransformed(std::list<GripData> *list, bool just_for_endof);
	void GetProperties(std::list<Property *> *list);

};

class CNCCode :public HeeksObj
{
public:
	static long pos; // used for setting the CNCCodeBlock objects' m_from_pos and m_to_pos
private:
	static std::map<std::string, ColorEnum> m_colors_s_i;
	static std::map<ColorEnum, std::string> m_colors_i_s;
	static std::vector<HeeksColor> m_colors;
	CNCCodeBlock* m_highlighted_block;

public:
	static void ClearColors(void);
	static void AddColor(const char* name, const HeeksColor& col);
	static ColorEnum GetColor(const char* name, ColorEnum def = ColorDefaultType);
	static const char* GetColor(ColorEnum i, const char* def = "default");
	static int ColorCount(void) { return m_colors.size(); }
	static HeeksColor& Color(ColorEnum i) { return m_colors[i]; }

	std::list<CNCCodeBlock*> m_blocks;
	int m_gl_list;
	int m_select_gl_list;
	CBox m_box;
	bool m_user_edited; // set, if the user has edited the nc code
	static bool prev_point_valid;
	static Point3d prev_point;
	static int s_arc_interpolation_count;	// How many lines to represent an arc for the glCommands() method?
	static int m_type;

	CNCCode() :m_highlighted_block(NULL), m_gl_list(0), m_select_gl_list(0), m_user_edited(false){}
	CNCCode(const CNCCode &p) :m_highlighted_block(NULL), m_gl_list(0), m_select_gl_list(0), m_user_edited(false){ operator=(p); }
	virtual ~CNCCode();

	const CNCCode &operator=(const CNCCode &p);
	void Clear();

	// HeeksObj's virtual functions
	int GetType()const{ return m_type; }
	const wchar_t* GetTypeString(void) const { return L"NC Code"; }
	const wchar_t* GetXMLTypeString()const{ return L"nccode"; }
	void glCommands(bool select, bool marked, bool no_color);
	void GetBox(CBox &box);
	const wchar_t* GetIconFilePath();
	void GetProperties(std::list<Property *> *list);
	HeeksObj *MakeACopy(void)const;
	void CopyFrom(const HeeksObj* object);
	void WriteToXML(TiXmlElement *element);
	void ReadFromXML(TiXmlElement *element);
	bool CanAdd(HeeksObj* object);
	bool CanAddTo(HeeksObj* owner);
	bool OneOfAKind(){return true;}
//	bool SetClickMarkPoint(MarkedObject* marked_object, const Point3d &ray_start, const Point3d &ray_direction);
	bool NeverDelete(){ return true; }  // I think python will already delete this or something.


	static void ReadColorsFromConfig();
	static void WriteColorsToConfig();
	static void GetOptions(std::list<Property *> *list);

	void DestroyGLLists(void); // not void KillGLLists(void), because I don't want the display list recreated on the Redraw button
	void HighlightBlock(long pos);
	void SetHighlightedBlock(CNCCodeBlock* block);
	CNCCodeBlock* GetHighlightedBlock(){ return m_highlighted_block; }
};

class CNCCodeViewport
{
	CNCCode* m_nc_code;
	int m_w;
	int m_h;
	double m_current_line; // the line at the top of the viewport, zero based
	double m_selected_line;
	double m_pixels_per_line;

public:
	CNCCodeViewport() :m_nc_code(NULL), m_w(0), m_h(0), m_current_line(0.0), m_selected_line(0.0), m_pixels_per_line(13.0){}

	void SetSize(int w, int h){ m_w = w; m_h = h; }
	int GetWidth(){ return m_w; }
	int GetHeight(){ return m_h; }
	void Render();// this does all the OpenGL commands
	double GetCurrentLine()const{ return m_current_line; }
	void SetCurrentLine(double line){ m_current_line = line; }
	double GetSelectedLine()const{ return m_selected_line; }
	void SelectLine(double line, bool jump_to_line);
	CNCCodeBlock* GetBlockAtLine(int line_number); // zero based
	void SetNcCode(CNCCode *nc_code);
	double GetLinesPerPage();
	int GetNumberOfLines();
	double GetPixelsPerLine(){ return m_pixels_per_line; }
	void SetPixelsPerLine(double p){ m_pixels_per_line = p; }
};