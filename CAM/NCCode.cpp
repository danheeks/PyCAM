// NCCode.cpp
/*
 * Copyright (c) 2009, Dan Heeks
 * This program is released under the BSD license. See the file COPYING for
 * details.
 */

#include <stdafx.h>
#include <math.h>
#include "NCCode.h"
#include "strconv.h"
#include "Picking.h"
#include "HeeksFont.h"
#include "GripData.h"

#include <memory>
#include <sstream>

double TOLERANCE = 1.0e-06;


int CNCCode::s_arc_interpolation_count = 20;
int CNCCode::m_type = 0;
int CNCCodeBlock::m_type = 0;

void ColouredText::WriteXML(TiXmlNode *root)
{
	TiXmlElement * element;
	element = new TiXmlElement( "text" );
	root->LinkEndChild(element);

	// add actual text as a child object
   	TiXmlText* text = new TiXmlText(Ttc(m_str.c_str()));
   	element->LinkEndChild(text);

	if(m_color_type != ColorDefaultType)element->SetAttribute( "col", CNCCode::GetColor(m_color_type));
}

void ColouredText::ReadFromXMLElement(TiXmlElement* element)
{
	m_color_type = CNCCode::GetColor(element->Attribute("col"));

	// get the text
	const char* text = element->GetText();
	if(text)m_str = std::wstring(Ctt(text));
}

void PathObject::WriteBaseXML(TiXmlElement *pElem)
{
	pElem->SetDoubleAttribute("x", m_point.x);
	pElem->SetDoubleAttribute("y", m_point.y);
	pElem->SetDoubleAttribute("z", m_point.z);

} // End WriteXML() method

void PathObject::ReadFromXMLElement(TiXmlElement* pElem)
{
	double x;
	m_point = CNCCode::prev_point;
	if(pElem->Attribute("x", &x))m_point.x = x * CNCCodeBlock::multiplier;
	if(pElem->Attribute("y", &x))m_point.y = x * CNCCodeBlock::multiplier;
	if(pElem->Attribute("z", &x))m_point.z = x * CNCCodeBlock::multiplier;
	CNCCode::prev_point = m_point;
}

void PathLine::WriteXML(TiXmlNode *root)
{
	TiXmlElement * element;
	element = new TiXmlElement( "line" );
	root->LinkEndChild(element);

	PathObject::WriteBaseXML(element);
}

void PathLine::ReadFromXMLElement(TiXmlElement* pElem)
{
	PathObject::ReadFromXMLElement(pElem);
}

void PathLine::glVertices()
{
	if(CNCCode::prev_point_valid)glVertex3dv(CNCCode::prev_point.getBuffer());
	glVertex3dv(m_point.getBuffer());
}

void PathArc::GetBox(CBox &box)
{
	if (CNCCode::prev_point_valid)
	{
		double dist = Point(m_point.x, m_point.y).dist(Point(CNCCode::prev_point.x, CNCCode::prev_point.y));
		if (dist > 1.0e-06)
		{
			double radius = 0.0;
			if (IsIncluded(Point3d(0, 1, 0), radius))
				box.Insert(CNCCode::prev_point.x + m_c.x, CNCCode::prev_point.y + m_c.y + radius, 0);
			if (IsIncluded(Point3d(0, -1, 0), radius))
				box.Insert(CNCCode::prev_point.x + m_c.x, CNCCode::prev_point.y + m_c.y - radius, 0);
			if (IsIncluded(Point3d(1, 0, 0), radius))
				box.Insert(CNCCode::prev_point.x + m_c.x + radius, CNCCode::prev_point.y + m_c.y, 0);
			if (IsIncluded(Point3d(-1, 0, 0), radius))
				box.Insert(CNCCode::prev_point.x + m_c.x - radius, CNCCode::prev_point.y + m_c.y, 0);
		}
	}

	PathObject::GetBox(box);
}

bool PathArc::IsIncluded(const Point3d &pnt, double &radius)
{
	double sx = -m_c.x;
	double sy = -m_c.y;
	// e = cs + se = -c + e - s
	double ex = -m_c.x + m_point.x - CNCCode::prev_point.x;
	double ey = -m_c.y + m_point.y - CNCCode::prev_point.y;
	radius = sqrt(sx * sx + sy * sy);

	double start_angle = atan2(sy, sx);
	double end_angle = atan2(ey, ex);

	if(m_dir == 1){
		if(end_angle < start_angle)end_angle += 6.283185307179;
	}
	else{
		if(start_angle < end_angle)start_angle += 6.283185307179;
	}

	// double angle_step = 0;

	if (start_angle == end_angle)
		// It's a full circle.
		return true;

	double the_angle = atan2(pnt.y, pnt.x);
	double the_angle2 = the_angle + 2*PI;
	return (the_angle >= start_angle && the_angle <= end_angle) || (the_angle2 >= start_angle && the_angle2 <= end_angle);
}

void PathArc::WriteXML(TiXmlNode *root)
{
	TiXmlElement * element = new TiXmlElement( "arc" );
	root->LinkEndChild(element);

	element->SetDoubleAttribute( "i", m_c.x);
	element->SetDoubleAttribute( "j", m_c.y);
	element->SetDoubleAttribute( "k", m_c.z);
	element->SetDoubleAttribute( "d", m_dir);

	PathObject::WriteBaseXML(element);
}

void PathArc::ReadFromXMLElement(TiXmlElement* pElem)
{
	// get the attributes
	if (pElem->Attribute("i")) pElem->Attribute("i", &m_c.x);
	if (pElem->Attribute("j")) pElem->Attribute("j", &m_c.y);
	if (pElem->Attribute("k")) pElem->Attribute("k", &m_c.z);
	if (pElem->Attribute("d")) pElem->Attribute("d", &m_dir);

	m_c.x *= CNCCodeBlock::multiplier;
	m_c.y *= CNCCodeBlock::multiplier;
	m_c.z *= CNCCodeBlock::multiplier;

	PathObject::ReadFromXMLElement(pElem);
}


void PathArc::glVertices()
{
	if (!CNCCode::prev_point_valid) return;

	std::list<Point3d> vertices;
	Interpolate( CNCCode::s_arc_interpolation_count, vertices);
	glVertex3dv(CNCCode::prev_point.getBuffer());
	for (std::list<Point3d>::const_iterator l_itVertex = vertices.begin(); l_itVertex != vertices.end(); l_itVertex++)
	{
		glVertex3dv(l_itVertex->getBuffer());
	} // End for
}

void PathArc::Interpolate(const unsigned int number_of_points, std::list<Point3d>& points ) const
{
	if (Point(m_point.x, m_point.y) == Point(CNCCode::prev_point.x, CNCCode::prev_point.y))
		return;

	double sx = -m_c.x;
	double sy = -m_c.y;
	// e = cs + se = -c + e - s
	double ex = -m_c.x + m_point.x - CNCCode::prev_point.x;
	double ey = -m_c.y + m_point.y - CNCCode::prev_point.y;
	double rs = sqrt(sx * sx + sy * sy);
	double re = sqrt(ex * ex + ey * ey);

	double start_angle = atan2(sy, sx);
	double end_angle = atan2(ey, ex);

	if(m_dir == 1){
		if(end_angle < start_angle)end_angle += 6.283185307179;
	}
	else{
		if(start_angle < end_angle)start_angle += 6.283185307179;
	}

	double angle_step = 0;

	if (start_angle == end_angle)
	{
		// It's a full circle.
		angle_step = (2 * PI) / number_of_points;
		if (m_dir == -1)
		{
			angle_step = -angle_step; // fix preview of full cw arcs
		}
	} // End if - then
	else
	{
		// It's an arc.
		angle_step = (end_angle - start_angle) / number_of_points;
	} // End if - else

	points.push_back(CNCCode::prev_point);

	for(unsigned int i = 0; i< number_of_points; i++)
	{
		double angle = start_angle + angle_step * (i + 1);
		double r = rs + ((re - rs) * (i + 1)) /number_of_points;
		double x = CNCCode::prev_point.x + m_c.x + r * cos(angle);
		double y = CNCCode::prev_point.y + m_c.y + r * sin(angle);
		double z = CNCCode::prev_point.z + ((m_point.z - CNCCode::prev_point.z) * (i + 1)) / number_of_points;

		points.push_back( Point3d( x, y, z ) );
	}
}

ColouredPath::ColouredPath(const ColouredPath& c)
{
	operator=(c);
}

const ColouredPath &ColouredPath::operator=(const ColouredPath& c)
{
	Clear();
	m_color_type = c.m_color_type;
	for(std::list< PathObject* >::const_iterator It = c.m_points.begin(); It != c.m_points.end(); It++)
	{
		PathObject* object = *It;
		m_points.push_back(object->MakeACopy());
	}
	return *this;
}

void ColouredPath::Clear()
{
	for(std::list< PathObject* >::iterator It = m_points.begin(); It != m_points.end(); It++)
	{
		PathObject* object = *It;
		delete object;
	}
	m_points.clear();
}

void ColouredPath::glCommands(bool no_color)
{
	if(!no_color)CNCCode::Color(m_color_type).glColor();
	glBegin(GL_LINE_STRIP);
	for(std::list< PathObject* >::iterator It = m_points.begin(); It != m_points.end(); It++)
	{
		PathObject* po = *It;
		po->glVertices();
		CNCCode::prev_point = po->m_point;
		CNCCode::prev_point_valid = true;
	}
	glEnd();

}

void ColouredPath::GetBox(CBox &box)
{
	for(std::list< PathObject* >::iterator It = m_points.begin(); It != m_points.end(); It++)
	{
		PathObject* po= *It;
		po->GetBox(box);
		CNCCode::prev_point = po->m_point;
		CNCCode::prev_point_valid = true;
	}
}

void ColouredPath::WriteXML(TiXmlNode *root)
{
	TiXmlElement * element;
	element = new TiXmlElement( "path" );
	root->LinkEndChild(element);

	element->SetAttribute( "col", CNCCode::GetColor(m_color_type));
	for(std::list< PathObject* >::iterator It = m_points.begin(); It != m_points.end(); It++)
	{
		PathObject* po = *It;
		po->WriteXML(element);
	}
}

void ColouredPath::ReadFromXMLElement(TiXmlElement* element)
{
	// get the attributes
	m_color_type = CNCCode::GetColor(element->Attribute("col"), ColorRapidType);

	// loop through all the objects
	for(TiXmlElement* pElem = TiXmlHandle(element).FirstChildElement().Element() ; pElem; pElem = pElem->NextSiblingElement())
	{
		std::string name(pElem->Value());
		if(name == "line")
		{
			PathLine *new_object = new PathLine;
			new_object->ReadFromXMLElement(pElem);
			m_points.push_back(new_object);
		}
		else if(name == "arc")
		{
			PathArc *new_object = new PathArc;
			new_object->ReadFromXMLElement(pElem);
			m_points.push_back(new_object);
		}
	}
}

double CNCCodeBlock::multiplier = 1.0;

HeeksObj *CNCCodeBlock::MakeACopy(void)const{return new CNCCodeBlock(*this);}

void CNCCodeBlock::glCommands(bool select, bool marked, bool no_color)
{
	if(marked)glLineWidth(3);

	for(std::list<ColouredPath>::iterator It = m_line_strips.begin(); It != m_line_strips.end(); It++)
	{
		ColouredPath& line_strip = *It;
		line_strip.glCommands(no_color);
	}

	if(marked)glLineWidth(1);

}

void CNCCodeBlock::GetBox(CBox &box)
{
	for(std::list<ColouredPath>::iterator It = m_line_strips.begin(); It != m_line_strips.end(); It++)
	{
		ColouredPath& line_strip = *It;
		line_strip.GetBox(box);
	}
}

void CNCCodeBlock::WriteToXML(TiXmlElement *element)
{
	for(std::list<ColouredText>::iterator It = m_text.begin(); It != m_text.end(); It++)
	{
		ColouredText &text = *It;
		text.WriteXML(element);
	}

	for(std::list<ColouredPath>::iterator It = m_line_strips.begin(); It != m_line_strips.end(); It++)
	{
		ColouredPath &line_strip = *It;
		line_strip.WriteXML(element);
	}

	element->SetAttribute("tool_number", m_tool_number);

	HeeksObj::WriteToXML(element);
}

void CNCCodeBlock::ReadFromXML(TiXmlElement* element)
{
	m_from_pos = CNCCode::pos;

	// loop through all the objects
	for(TiXmlElement* pElem = TiXmlHandle(element).FirstChildElement().Element() ; pElem; pElem = pElem->NextSiblingElement())
	{
		std::string name(pElem->Value());
		if(name == "text")
		{
			ColouredText t;
			t.ReadFromXMLElement(pElem);
			m_text.push_back(t);
			CNCCode::pos += t.m_str.length();
		}
		else if(name == "path")
		{
			ColouredPath l;
			l.ReadFromXMLElement(pElem);
			m_line_strips.push_back(l);
		}
		else if(name == "mode")
		{
			const char* units = pElem->Attribute("units");
			if(units)pElem->Attribute("units", &CNCCodeBlock::multiplier);
		}
	}

	if(m_text.size() > 0)CNCCode::pos++;

	m_to_pos = CNCCode::pos;

	element->Attribute("tool_number", &m_tool_number);

	HeeksObj::ReadFromXML(element);
}

void CNCCodeBlock::AppendText(std::wstring& str)
{
	if(m_text.size() == 0)return;

	for(std::list<ColouredText>::iterator It = m_text.begin(); It != m_text.end(); It++)
	{
		ColouredText &text = *It;
		str.append(text.m_str);
	}
	str.append(L"\n");
}

void CNCCodeBlock::GetGripperPositionsTransformed(std::list<GripData> *list, bool just_for_endof)
{
	for (std::list<ColouredPath>::iterator It = m_line_strips.begin(); It != m_line_strips.end(); It++)
	{
		ColouredPath& line_strip = *It;
		for (std::list< PathObject* >::const_iterator It = line_strip.m_points.begin(); It != line_strip.m_points.end(); It++)
		{
			PathObject* object = *It;
			list->push_back(GripData(GripperTypeTranslate, object->m_point, NULL));
		}
	}
}

void CNCCodeBlock::GetProperties(std::list<Property *> *list)
{

}

long CNCCode::pos = 0;
// static
bool CNCCode::prev_point_valid = false;
Point3d CNCCode::prev_point = Point3d(0,0,0);
std::map<std::string,ColorEnum> CNCCode::m_colors_s_i;
std::map<ColorEnum,std::string> CNCCode::m_colors_i_s;
std::vector<HeeksColor> CNCCode::m_colors;

const wchar_t* CNCCode::GetIconFilePath()
{
	static std::wstring iconpath = cam_dir + L"/icons/nccode.png";
	return iconpath.c_str();
}

void CNCCode::ClearColors(void)
{
	CNCCode::m_colors_s_i.clear();
	CNCCode::m_colors_i_s.clear();
	CNCCode::m_colors.clear();
}

void CNCCode::AddColor(const char* name, const HeeksColor& col)
{
	ColorEnum i = (ColorEnum)ColorCount();
	m_colors_s_i.insert(std::pair<std::string,ColorEnum>(std::string(name), i));
	m_colors_i_s.insert(std::pair<ColorEnum,std::string>(i, std::string(name)));
	m_colors.push_back(col);
}

ColorEnum CNCCode::GetColor(const char* name, ColorEnum def)
{
	if (name == NULL) return def;
	std::map<std::string,ColorEnum>::iterator it = m_colors_s_i.find(std::string(name));
	if (it != m_colors_s_i.end()) return it->second;
	else return def;
}

const char* CNCCode::GetColor(ColorEnum i, const char* def)
{
	std::map<ColorEnum,std::string>::iterator it = m_colors_i_s.find(i);
	if (it != m_colors_i_s.end()) return it->second.c_str();
	else return def;
}

CNCCode::~CNCCode()
{
	Clear();
}

const CNCCode &CNCCode::operator=(const CNCCode &rhs)
{
	HeeksObj::operator =(rhs);
	Clear();
	for(std::list<CNCCodeBlock*>::const_iterator It = rhs.m_blocks.begin(); It != rhs.m_blocks.end(); It++)
	{
		CNCCodeBlock* block = *It;
		CNCCodeBlock* new_block = new CNCCodeBlock(*block);
		m_blocks.push_back(new_block);
		new_block->m_owner = this;
	}
	return *this;
}

void CNCCode::Clear()
{
	for(std::list<CNCCodeBlock*>::iterator It = m_blocks.begin(); It != m_blocks.end(); It++)
	{
		CNCCodeBlock* block = *It;
		delete block;
	}
	m_blocks.clear();
	DestroyGLLists();
	m_box = CBox();
	m_highlighted_block = NULL;
}

void CNCCode::glCommands(bool select, bool marked, bool no_color)
{
	int* plist = select ? &m_select_gl_list : &m_gl_list;
	if (*plist)
	{
		glCallList(*plist);
	}
	else{
		*plist = glGenLists(1);
		glNewList(*plist, GL_COMPILE_AND_EXECUTE);

		// render all the blocks
		CNCCode::prev_point_valid = false;

		for(std::list<CNCCodeBlock*>::iterator It = m_blocks.begin(); It != m_blocks.end(); It++)
		{
			CNCCodeBlock* block = *It;
			if(select)SetPickingColor(block->GetIndex());
			block->glCommands(select, block == m_highlighted_block, no_color);
		}

		glEndList();
	}
}

void CNCCode::GetBox(CBox &box)
{
	if(!m_box.m_valid)
	{
		CNCCode::prev_point_valid = false;
		for(std::list<CNCCodeBlock*>::iterator It = m_blocks.begin(); It != m_blocks.end(); It++)
		{
			CNCCodeBlock* block = *It;
			block->GetBox(m_box);
		}
	}

	box.Insert(m_box);
}

void CNCCode::GetProperties(std::list<Property *> *list)
{
#if 0 // to do
	list->push_back(new PropertyInt(_("Arc Interpolation Count"), CNCCode::s_arc_interpolation_count, this, on_set_arc_interpolation_count));
#endif
	HeeksObj::GetProperties(list);
}

HeeksObj *CNCCode::MakeACopy(void)const{return new CNCCode(*this);}

void CNCCode::CopyFrom(const HeeksObj* object){operator=(*((CNCCode*)object));}

void CNCCode::WriteToXML(TiXmlElement* element)
{
	for(std::list<CNCCodeBlock*>::iterator It = m_blocks.begin(); It != m_blocks.end(); It++)
	{
		CNCCodeBlock* block = *It;
		block->WriteXML(element);
	}

	element->SetAttribute( "edited", m_user_edited ? 1:0);

	HeeksObj::WriteToXML(element);
}

bool CNCCode::CanAdd(HeeksObj* object)
{
	return ((object != NULL) && (object->GetType() == CNCCodeBlock::m_type));
}

bool CNCCode::CanAddTo(HeeksObj* owner)
{
	if (owner == NULL)
		return false;

	std::wstring type_string(owner->GetTypeString());
	lowerCase(type_string);
	return type_string.compare(L"program") == 0;
}

#if 0
bool CNCCode::SetClickMarkPoint(MarkedObject* marked_object, const Point3d &ray_start, const Point3d &ray_direction)
{
	if(marked_object->m_map.size() > 0)
	{
		MarkedObject* sub_marked_object = marked_object->m_map.begin()->second;
		if(sub_marked_object)
		{
			if(sub_marked_object->m_map.size() > 0)
			{
				HeeksObj* object = sub_marked_object->m_map.begin()->first;
				if(object && object->GetType() == CNCCodeBlock::m_type)
				{
					SetHighlightedBlock((CNCCodeBlock*)object);
					int from_pos = m_highlighted_block->m_from_pos;
					int to_pos = m_highlighted_block->m_to_pos;
					DestroyGLLists();
#if 0
					//to do
					wxGetApp().m_output_canvas->m_textCtrl->ShowPosition(from_pos);
					wxGetApp().m_output_canvas->m_textCtrl->SetSelection(from_pos, to_pos);
#endif
					return true;
				}
			}
		}
	}
	return false;
}
#endif

void CNCCode::ReadFromXML(TiXmlElement* element)
{
	pos = 0;

	CNCCodeBlock::multiplier = 1.0;
	CNCCode::prev_point = Point3d(0, 0, 0);
	int line_number = 0;

	// loop through all the objects
	for(TiXmlElement* pElem = TiXmlHandle(element).FirstChildElement().Element() ; pElem;	pElem = pElem->NextSiblingElement())
	{
		std::string name(pElem->Value());
		if(name == "ncblock")
		{
			CNCCodeBlock* new_object = new CNCCodeBlock;
			new_object->ReadFromXML(pElem);
			new_object->m_line_number = line_number;
			m_blocks.push_back(new_object);
			new_object->m_owner = this;
			line_number++;
		}
	}

	// loop through the attributes
	int i;
	element->Attribute("edited", &i);
	m_user_edited = (i != 0);

	HeeksObj::ReadFromXML(element);

	// to do
	//new_object->SetTextCtrl(wxGetApp().m_output_canvas->m_textCtrl);
}

void CNCCode::DestroyGLLists(void)
{
	if (m_gl_list)
	{
		glDeleteLists(m_gl_list, 1);
		m_gl_list = 0;
	}
	if (m_select_gl_list)
	{
		glDeleteLists(m_select_gl_list, 1);
		m_select_gl_list = 0;
	}
}

void CNCCode::HighlightBlock(long pos)
{
	SetHighlightedBlock(NULL);

	for(std::list<CNCCodeBlock*>::iterator It = m_blocks.begin(); It != m_blocks.end(); It++)
	{
		CNCCodeBlock* block = *It;
		if(pos < block->m_to_pos)
		{
			SetHighlightedBlock(block);
			break;
		}
	}
	DestroyGLLists();
}

void CNCCode::SetHighlightedBlock(CNCCodeBlock* block)
{
//	if(m_highlighted_block)m_highlighted_block->FormatText(wxGetApp().m_output_canvas->m_textCtrl, false, true);
	m_highlighted_block = block;
	if (m_gl_list)
	{
		glDeleteLists(m_gl_list, 1);
		m_gl_list = 0;
	}

//	if(m_highlighted_block)m_highlighted_block->FormatText(wxGetApp().m_output_canvas->m_textCtrl, true, true);
}

void CNCCodeViewport::Render()
{
	glViewport(0, 0, m_w, m_h);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	glDrawBuffer(GL_BACK);
	glPixelStorei(GL_UNPACK_ALIGNMENT, 1);

	glClearColor(1, 1, 1, 1);
	glClear(GL_COLOR_BUFFER_BIT);

	if (m_nc_code == NULL)
		return;

	if (m_nc_code->m_blocks.size() == 0)
		return;

	glOrtho(0.0f, m_w, 0.0f, m_h, 0.0f, 1.0f);

	double lines_to_draw = GetLinesPerPage() + 1;
	int start_line = (int)m_current_line;
	double extra = m_current_line - start_line;

	// move up to start, just above top of window
	glTranslated(0, (extra - 0.8) * m_pixels_per_line + m_h, 0);

	std::list<CNCCodeBlock*>::iterator It = m_nc_code->m_blocks.begin();
	std::advance(It, start_line);
	glColor3ub(0, 0, 0);
	int line_number = start_line;
	for (int i = 0; i < lines_to_draw; i++, line_number++)
	{
		CNCCodeBlock* block = *It;
		if (line_number == (int)m_selected_line)
		{
			// draw a rectangle
			glColor3ub(128, 192, 192);
			glBegin(GL_QUADS);
			double y0 = m_pixels_per_line * -0.1;
			double y1 = m_pixels_per_line * 0.9;
			glVertex2d(0, y0);
			glVertex2d(m_w, y0);
			glVertex2d(m_w, y1);
			glVertex2d(0, y1);
			glEnd();
		}
		glPushMatrix();
		glScaled(m_pixels_per_line * 0.7, m_pixels_per_line * 0.7, 0);
		for (std::list<ColouredText>::iterator TextIt = block->m_text.begin(); TextIt != block->m_text.end(); TextIt++)
		{
			ColouredText &text = *TextIt;
			CNCCode::Color(text.m_color_type).glColor();
			//DrawHeeksFontStringAntialiased(Ttc(text.m_str.c_str()), 0.1 / m_pixels_per_line, false, true);
			DrawHeeksFontString(Ttc(text.m_str.c_str()), false, true);
		}
		glPopMatrix();
		glTranslated(0, -m_pixels_per_line, 0);
		It++;
		if (It == m_nc_code->m_blocks.end())
			break;
	}
}

void CNCCodeViewport::SetNcCode(CNCCode *nc_code)
{
	m_nc_code = nc_code;
}

void CNCCodeViewport::SelectLine(double line, bool jump_to_line)
{
	m_selected_line = line;

	if (jump_to_line)
	{
		m_current_line = line - GetLinesPerPage() * 0.5;
		if (m_current_line < 0.0)m_current_line = 0.0;
		double last_first_line = m_nc_code->m_blocks.size() - GetLinesPerPage();
		if (m_current_line > last_first_line)m_current_line = last_first_line;
	}

	int i = 1;
	for (std::list<CNCCodeBlock*>::iterator It = m_nc_code->m_blocks.begin(); It != m_nc_code->m_blocks.end(); It++, i++)
	{
		if (i > line)
		{
			m_nc_code->SetHighlightedBlock(*It);
			break;
		}
	}
}

CNCCodeBlock* CNCCodeViewport::GetBlockAtLine(int line_number)
{
	if (m_nc_code == NULL)
		return NULL;

	if (m_nc_code->m_blocks.size() <= (size_t)line_number)
		return NULL;

	std::list<CNCCodeBlock*>::iterator It = m_nc_code->m_blocks.begin();
	std::advance(It, line_number);

	return *It;
}

double CNCCodeViewport::GetLinesPerPage()
{
	return ((double)m_h + 0.5) / m_pixels_per_line;
}

int CNCCodeViewport::GetNumberOfLines()
{
	if (m_nc_code)
		return m_nc_code->m_blocks.size();
	return 0;
}
