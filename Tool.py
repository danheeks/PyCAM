from CamObject import CamObject
from consts import *
import wx
import cad
from Object import PyChoiceProperty
from Object import PyProperty
from Object import PyPropertyLength
from nc.nc import *

type = 0

tool_types_for_choices = [
                          [TOOL_TYPE_DRILL, 'Drill Bit'],
                          [TOOL_TYPE_CENTREDRILL, 'Centre Drill Bit'],
                          [TOOL_TYPE_ENDMILL, 'End Mill'],
                          [TOOL_TYPE_SLOTCUTTER, 'Slot Cutter'],
                          [TOOL_TYPE_BALLENDMILL, 'Ball End Mill'],
                          [TOOL_TYPE_CHAMFER, 'Chamfer'],
                          [TOOL_TYPE_ENGRAVER, 'Engraving Bit'],
                          ]

class Tool(CamObject):
    def __init__(self, diameter = 3.0, title = None, tool_number = 0, type = TOOL_TYPE_SLOTCUTTER):
        CamObject.__init__(self, type)
        self.tool_number = tool_number
        self.type = type
        self.diameter = diameter
        self.material = TOOL_MATERIAL_UNDEFINED
        self.tool_length_offset = 0.0
        
        '''
        // also m_corner_radius, see below, is used for turning tools and milling tools


        /**
                The next three parameters describe the cutting surfaces of the bit.

                The two radii go from the centre of the bit -> flat radius -> corner radius.
                The vertical_cutting_edge_angle is the angle between the centre line of the
                milling bit and the angle of the outside cutting edges.  For an end-mill, this
                would be zero.  i.e. the cutting edges are parallel to the centre line
                of the milling bit.  For a chamfering bit, it may be something like 45 degrees.
                i.e. 45 degrees from the centre line which has both cutting edges at 2 * 45 = 90
                degrees to each other

                For a ball-nose milling bit we would have
                        - m_corner_radius = m_diameter / 2
                        - m_flat_radius = 0    // No middle bit at the bottom of the cutter that remains flat
                                                // before the corner radius starts.
                        - m_vertical_cutting_edge_angle = 0

                For an end-mill we would have
                        - m_corner_radius = 0
                        - m_flat_radius = m_diameter / 2
                        - m_vertical_cutting_edge_angle = 0

                For a chamfering bit we would have
                        - m_corner_radius = 0
                        - m_flat_radius = 0    // sharp pointed end.  This may be larger if we can't use the centre point.
                        - m_vertical_cutting_edge_angle = 45    // degrees from centre line of tool
         */
        '''
        self.corner_radius = 0.0
        self.flat_radius = 0.0
        self.cutting_edge_angle = 0.0
        self.cutting_edge_height = 0.0    # How far, from the bottom of the cutter, do the flutes extend?
        self.max_advance_per_revolution = 0.0
        '''    // This is the maximum distance a tool should advance during a single
                                                // revolution.  This value is often defined by the manufacturer in
                                                // terms of an advance no a per-tooth basis.  This value, however,
                                                // must be expressed on a per-revolution basis.  i.e. we don't want
                                                // to maintain the number of cutting teeth so a per-revolution
                                                // value is easier to use.
        '''
        self.automatically_generate_title = True    #// Set to true by default but reset to false when the user edits the title.
        '''
        // The following coordinates relate ONLY to touch probe tools.  They describe
        // the error the probe tool has in locating an X,Y point.  These values are
        // added to a probed point's location to find the actual point.  The values
        // should come from calibrating the touch probe.  i.e. set machine position
        // to (0,0,0), drill a hole and then probe for the centre of the hole.  The
        // coordinates found by the centre finding operation should be entered into
        // these values verbatim.  These will represent how far off concentric the
        // touch probe's tip is with respect to the quil.  Of course, these only
        // make sense if the probe's body is aligned consistently each time.  I will
        // ASSUME this is correct.
        '''
        self.probe_offset_x = 0.0
        self.probe_offset_y = 0.0
        '''
        // The following  properties relate to the extrusions created by a reprap style 3D printer.
        // using temperature, speed, and the height of the nozzle, and the nozzle size it's possible to create
        // many different sizes and shapes of extrusion.
        typedef std::pair< eExtrusionMaterial_t, wxString > ExtrusionMaterialDescription_t
        typedef std::vector<ExtrusionMaterialDescription_t > ExtrusionMaterialsList_t

        static ExtrusionMaterialsList_t GetExtrusionMaterialsList()
        {
                ExtrusionMaterialsList_t ExtrusionMaterials_list

                ExtrusionMaterials_list.push_back( ExtrusionMaterialDescription_t( eABS, wxString(_("ABS Plastic")) ))
                ExtrusionMaterials_list.push_back( ExtrusionMaterialDescription_t( ePLA, wxString(_("PLA Plastic")) ))
                ExtrusionMaterials_list.push_back( ExtrusionMaterialDescription_t( eHDPE, wxString(_("HDPE Plastic")) ))

                return(ExtrusionMaterials_list)
        }
        '''
        self.extrusion_material = EXTRUSION_MATERIAL_ABS
        self.feedrate = 0.0
        self.layer_height = 0.1
        self.width_over_thickness = 1.0
        self.temperature = 200
        self.flowrate = 10
        self.filament_diameter = 0.2
        '''
        // The gradient is the steepest angle at which this tool can plunge into the material.  Many
        // tools behave better if they are slowly ramped down into the material.  This gradient
        // specifies the steepest angle of decsent.  This is expected to be a negative number indicating
        // the 'rise / run' ratio.  Since the 'rise' will be downward, it will be negative.
        // By this measurement, a drill bit's straight plunge would have an infinite gradient (all rise, no run).
        // To cater for this, a value of zero will indicate a straight plunge.
        '''
        self.gradient = 0.0
        '''
        // properties for tapping tools
        int m_direction    // 0.. right hand tapping, 1..left hand tapping
        double m_pitch     // in units/rev
        '''
        
        if title != None:
            self.title = title
        else:
            self.title = self.GenerateMeaningfulName()
            
        self.ResetParametersToReasonableValues()
        
    def TypeName(self):
        return "Tool"

    def GetType(self):
        return type
    
    def GetTitle(self):
        return self.title

    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "tool"
        
    def MakeACopy(self):
        object = Tool()
        object.CopyFrom(self)
        return object
    
    def CopyFrom(self, object):
        self.tool_number = object.tool_number
        self.type = object.type
        self.diameter = object.diameter
        self.material = object.material
        self.tool_length_offset = object.tool_length_offset
        CamObject.CopyFrom(self, object)
    
    def ResetParametersToReasonableValues(self):
        if self.type != TOOL_TYPE_TURNINGTOOL:
            self.tool_length_offset = (5 * self.diameter)

            self.gradient = self.ReasonableGradient(self.type)

            if self.type == TOOL_TYPE_DRILL:
                self.corner_radius = 0.0
                self.flat_radius = 0.0
                self.cutting_edge_angle = 59.0
                self.cutting_edge_height = self.diameter * 3.0
                self.ResetTitle()

            elif self.type == TOOL_TYPE_CENTREDRILL:
                self.corner_radius = 0.0
                self.flat_radius = 0.0
                self.cutting_edge_angle = 59.0
                self.cutting_edge_height = self.diameter * 1.0
                self.ResetTitle()

            elif self.type == TOOL_TYPE_ENDMILL:
                self.corner_radius = 0.0
                self.flat_radius = self.diameter / 2
                self.cutting_edge_angle = 0.0
                self.cutting_edge_height = self.diameter * 3.0
                self.ResetTitle()

            elif self.type == TOOL_TYPE_SLOTCUTTER:
                self.corner_radius = 0.0
                self.flat_radius = self.diameter / 2
                self.cutting_edge_angle = 0.0
                self.cutting_edge_height = self.diameter * 3.0
                self.ResetTitle()

            elif self.type == TOOL_TYPE_BALLENDMILL:
                self.corner_radius = (self.diameter / 2)
                self.flat_radius = 0.0
                self.cutting_edge_angle = 0.0
                self.cutting_edge_height = self.diameter * 3.0
                self.ResetTitle()
            '''
                case CToolParams::eTouchProbe:
                self.corner_radius = (self.diameter / 2)
                self.flat_radius = 0
                                ResetTitle()
                                break

                case CToolParams::eExtrusion:
                self.corner_radius = (self.diameter / 2)
                self.flat_radius = 0
                                ResetTitle()
                                break

                case CToolParams::eToolLengthSwitch:
                self.corner_radius = (self.diameter / 2)
                                ResetTitle()
                                break

                case CToolParams::eChamfer:
                self.corner_radius = 0
                self.flat_radius = 0
                self.cutting_edge_angle = 45
                                height = (self.diameter / 2.0) * tan( degrees_to_radians(90.0 - self.cutting_edge_angle))
                self.cutting_edge_height = height
                                ResetTitle()
                                break

                case CToolParams::eTurningTool:
                                // No special constraints for this.
                                ResetTitle()
                                break

                case CToolParams::eTapTool:
                                self.tool_length_offset = (5 * self.diameter)
                self.automatically_generate_title = 1
                self.diameter = 6.0
                self.direction = 0
                self.pitch = 1.0
                self.cutting_edge_height = self.diameter * 3.0
                                ResetTitle()
                                break

                default:
                                wxMessageBox(_T("That is not a valid tool type. Aborting value change."))
                                return
            '''

    def ReasonableGradient(self, type):
        if self.type == TOOL_TYPE_SLOTCUTTER or self.type == TOOL_TYPE_ENDMILL or self.type == TOOL_TYPE_BALLENDMILL:
            return -0.1
        return 0.0

    def GenerateMeaningfulName(self):
        name_str = ""
        if self.type != TOOL_TYPE_TURNINGTOOL and self.type != TOOL_TYPE_TOUCHPROBE and self.type != TOOL_TYPE_TOOLLENGTHSWITCH:
            if wx.GetApp().program.units == 1.0:
                # We're using metric.  Leave the diameter as a floating point number.  It just looks more natural.
                name_str = name_str + str(self.diameter) + " mm "
            else:
                # We're using inches.
                # to do, Find a fractional representation if one matches.
                name_str = name_str + str(self.diameter/wx.GetApp().program.units) + " inch "
                
        if self.type != TOOL_TYPE_EXTRUSION and self.type != TOOL_TYPE_TOUCHPROBE and self.type != TOOL_TYPE_TOOLLENGTHSWITCH:
            if self.material == TOOL_MATERIAL_HSS:
                name_str = name_str + "HSS "
            elif self.material == TOOL_MATERIAL_CARBIDE:
                name_str = name_str + "Carbide "
        
        if self.type == TOOL_TYPE_EXTRUSION:
            if self.extrusion_material == EXTRUSION_MATERIAL_ABS:
                name_str = name_str + "ABS "
            elif self.extrusion_material == EXTRUSION_MATERIAL_PLA:
                name_str = name_str + "PLA "
            elif self.extrusion_material == EXTRUSION_MATERIAL_HDPE:
                name_str = name_str + "HDPE "

        if self.type == TOOL_TYPE_DRILL:
            name_str = name_str + "Drill Bit"
        elif self.type == TOOL_TYPE_CENTREDRILL:
            name_str = name_str + "Centre Drill Bit"
        elif self.type == TOOL_TYPE_ENDMILL:
            name_str = name_str + "End Mill"
        elif self.type == TOOL_TYPE_SLOTCUTTER:
            name_str = name_str + "Slot Cutter"
        elif self.type == TOOL_TYPE_BALLENDMILL:
            name_str = name_str + "Ball End Mill"
        elif self.type == TOOL_TYPE_CHAMFER:
            # Remove all that we've already prepared.
            name_str = str(self.cutting_edge_angle) + " degree" + "Chamfering Bit"
        elif self.type == TOOL_TYPE_TURNINGTOOL:
            name_str = name_str + "Turning Tool"
        elif self.type == TOOL_TYPE_TOUCHPROBE:
            name_str = name_str + "Touch Probe"
        elif self.type == TOOL_TYPE_EXTRUSION:
            name_str = name_str + "Extrusion"
        elif self.type == TOOL_TYPE_TOOLLENGTHSWITCH:
            name_str = name_str + "Tool Length Switch"
        elif self.type == TOOL_TYPE_TAPTOOL:
            # to do, copy code from CTool.cpp
            name_str = name_str + "Tap Tool"
            
        if self.type == 0:
            raise NameError('tool type is 0')
        
        return name_str
    
    def ResetTitle(self):
        if self.automatically_generate_title:
            self.title = self.GenerateMeaningfulName()
        
    def GetProperties(self):
        properties = []
        properties.append(PyProperty("Tool Number", 'tool_number', self))
        properties.append(PyChoiceProperty("Automatic Title", 'automatically_generate_title', ['Leave manually assigned title', 'Automatically generate title'], self))
        properties.append(PyChoiceProperty("Material", 'material', ['High Speed Steel', 'Carbide'], self))
        properties.append(PyChoiceProperty("Type", 'type', GetToolTypeNames(), self, GetToolTypeValues()))
        properties.append(PyPropertyLength("Diameter", 'diameter', self))
        properties.append(PyPropertyLength("Tool Length Offset", 'tool_length_offset', self))
        properties.append(PyPropertyLength("Flat Radius", 'flat_radius', self))
        properties.append(PyPropertyLength("Corner Radius", 'corner_radius', self))
        properties.append(PyProperty("Cutting Edge Angle", 'cutting_edge_angle', self))
        properties.append(PyPropertyLength("Cutting Edge Height", 'cutting_edge_height', self))
        properties += CamObject.GetBaseProperties(self)
        return properties
    
    def HasEdit(self):
        return True
    
    def Edit(self):
        import ToolDlg
        dlg = ToolDlg.ToolDlg(self)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            dlg.GetData()
        return res
        
    def ReadXml(self):
        self.tool_number = cad.GetXmlInt('tool_number')
        self.title = cad.GetXmlValue('title')
        
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'params':
                self.diameter = cad.GetXmlFloat('diameter', self.diameter)
                self.tool_length_offset = cad.GetXmlFloat('tool_length_offset', self.tool_length_offset)
                self.automatically_generate_title = cad.GetXmlBool('automatically_generate_title', self.automatically_generate_title)
                self.material = cad.GetXmlInt('material', self.material)
                type_str = GetToolTypeXMLString(self.type)
                xml_value = cad.GetXmlValue('type', type_str)
                self.type = GetToolTypeFromString(xml_value)
                self.corner_radius = cad.GetXmlFloat('corner_radius', self.corner_radius)
                self.flat_radius = cad.GetXmlFloat('flat_radius', self.flat_radius)
                self.cutting_edge_angle = cad.GetXmlFloat('cutting_edge_angle', self.cutting_edge_angle)
                self.cutting_edge_height = cad.GetXmlFloat('cutting_edge_height', self.cutting_edge_height)
            child_element = cad.GetNextXmlChild()
            
        CamObject.ReadXml(self)
            
        self.ResetTitle()
        
    def WriteXml(self):
        cad.SetXmlValue('title', self.title)
        cad.SetXmlValue('tool_number', self.tool_number)
        cad.BeginXmlChild('params')
        cad.SetXmlValue('diameter', self.diameter)
        cad.SetXmlValue('tool_length_offset', self.tool_length_offset)
        cad.SetXmlValue('automatically_generate_title', self.automatically_generate_title)
        cad.SetXmlValue('material', self.material)
        cad.SetXmlValue('type', GetToolTypeXMLString(self.type))
        cad.SetXmlValue('corner_radius', self.corner_radius)
        cad.SetXmlValue('flat_radius', self.flat_radius)
        cad.SetXmlValue('cutting_edge_angle', self.cutting_edge_angle)
        cad.SetXmlValue('cutting_edge_height', self.cutting_edge_height)
        cad.EndXmlChild()
        
        CamObject.WriteXml(self)
        
    def CallsObjListReadXml(self):
        return False
            
    def DoGCodeCalls(self):
        params = {
                  'corner_radius':self.corner_radius,
                  'cutting edge angle':self.cutting_edge_angle,
                  'cutting edge height':self.cutting_edge_height,
                  'diameter':self.diameter,
                  'flat radius':self.flat_radius,
                  'material':self.material,
                  'tool length offset':self.tool_length_offset,
                  'type':self.type,
                  'name':self.GenerateMeaningfulName(),
                  }
                  
        tool_defn(self.tool_number, self.GetTitle(), params)


#	The CuttingRadius is almost always the same as half the tool's diameter.
#	The exception to this is if it's a chamfering bit.  In this case we
#	want to use the flat_radius plus a little bit.  i.e. if we're chamfering the edge
#	then we want to use the part of the cutting surface just a little way from
#	the flat radius.  If it has a flat radius of zero (i.e. it has a pointed end)
#	then it will be a small number.  If it is a carbide tipped bit then the
#	flat radius will allow for the area below the bit that doesn't cut.  In this
#	case we want to cut around the middle of the carbide tip.  In this case
#	the carbide tip should represent the full cutting edge height.  We can
#	use this method to make all these adjustments based on the tool's
#	geometry and return a reasonable value.

#	If express_in_program_units is true then we need to divide by the program
#	units value.  We use metric (mm) internally and convert to inches only
#	if we need to and only as the last step in the process.  By default, return
#	the value in internal (metric) units.

#	If the depth value is passed in as a positive number then the radius is given
#	for the corresponding depth (from the bottom-most tip of the tool).  This is
#	only relevant for chamfering (angled) bits.

    def CuttingRadius( self, express_in_program_units = False, depth = -1 ):
        if self.type == TOOL_TYPE_CHAMFER:
            if depth < 0.0:
#                We want to decide where, along the cutting edge, we want
#                to machine.  Let's start with 1/3 of the way from the inside
#                cutting edge so that, as we plunge it into the material, it
#                cuts towards the outside.  We don't want to run right on
#                the edge because we don't want to break the top off.

                # one third from the centre-most point.
                proportion_near_centre = 0.3
                radius = (((self.diameter/2) - self.flat_radius) * proportion_near_centre) + self.flat_radius
            else:
                radius = self.flat_radius + (depth * math.tan((self.cutting_edge_angle / 360.0 * 2 * math.pi)))
                if radius > (self.diameter / 2.0):
                    # The angle and depth would have us cutting larger than our largest diameter.
                    radius = self.diameter / 2.0
        else:
            radius = self.diameter/2

        if express_in_program_units:
            return radius / wx.GetApp().program.units
        else:
            return radius

def GetToolTypeNames():
    choices = []
    for type in tool_types_for_choices:
        choices.append(type[1])
    return choices
        
def GetToolTypeValues():
    choices = []
    for type in tool_types_for_choices:
        choices.append(type[0])
    return choices

def GetToolTypeIndex(type):
    i = 0
    for t in GetToolTypeValues():
        if type == t:
            return i
        i += 1
    return -1    
        
XML_STRING_DRILL = 'drill'
XML_STRING_CENTRE_DRILL = 'centre_drill'
XML_STRING_END_MILL = 'end_mill'
XML_STRING_SLOT_CUTTER = 'slot_cutter'
XML_STRING_BALL_END_MILL = 'ball_end_mill'
XML_STRING_CHAMFER = 'chamfer'
XML_STRING_ENGRAVER = 'engraver'
XML_STRING_UNDEFINED = 'undefined'

def GetToolTypeFromString(s):
    s = s.lower()
    if s == XML_STRING_DRILL: return TOOL_TYPE_DRILL
    elif s == XML_STRING_CENTRE_DRILL: return TOOL_TYPE_CENTREDRILL
    elif s == XML_STRING_END_MILL: return TOOL_TYPE_ENDMILL
    elif s == XML_STRING_SLOT_CUTTER: return TOOL_TYPE_SLOTCUTTER
    elif s == XML_STRING_BALL_END_MILL: return TOOL_TYPE_BALLENDMILL
    elif s == XML_STRING_CHAMFER: return TOOL_TYPE_CHAMFER
    elif s == XML_STRING_ENGRAVER: return TOOL_TYPE_ENGRAVER
    return TOOL_TYPE_UNDEFINED

def GetToolTypeXMLString(type):
    if type == TOOL_TYPE_DRILL: return XML_STRING_DRILL
    elif type == TOOL_TYPE_CENTREDRILL: return XML_STRING_CENTRE_DRILL
    elif type == TOOL_TYPE_ENDMILL: return XML_STRING_END_MILL
    elif type == TOOL_TYPE_SLOTCUTTER: return XML_STRING_SLOT_CUTTER
    elif type == TOOL_TYPE_BALLENDMILL: return XML_STRING_BALL_END_MILL
    elif type == TOOL_TYPE_CHAMFER: return XML_STRING_CHAMFER
    elif type == TOOL_TYPE_ENGRAVER: return XML_STRING_ENGRAVER
    return XML_STRING_UNDEFINED

def FindToolType(tool_number):
    tool = FindTool(tool_number)
    if tool: return tool.type
    return TOOL_TYPE_UNDEFINED

def FindTool(tool_number):
    for tool in wx.GetApp().program.tools.GetChildren():
        if tool.tool_number == tool_number:
            return tool
    return None
