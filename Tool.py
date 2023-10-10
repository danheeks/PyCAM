from CamObject import CamObject
from consts import *
import wx
import cad
from Object import PyChoiceProperty
from Object import PyProperty
from Object import PyPropertyLength
from nc.nc import *
import Tools

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

class ToolPyPropertyLength(PyPropertyLength):
    def __init__(self, title, value_name, object):
        PyPropertyLength.__init__(self, title, value_name, object)

    def SetFloat(self, value):
        PyPropertyLength.SetFloat(self, value)
        self.pyobj.ResetTitle()

class Tool(CamObject):
    def __init__(self, diameter = 3.0, title = None, tool_number = 0, type = TOOL_TYPE_SLOTCUTTER):
        CamObject.__init__(self, type)
        self.tool_number = tool_number
        self.type = type
        self.diameter = diameter
        self.material = TOOL_MATERIAL_CARBIDE
        self.tool_length_offset = 0.0
        self.corner_radius = 0.0
        self.flat_radius = 0.0
        self.cutting_edge_angle = 0.0
        self.cutting_edge_height = 0.0    # How far, from the bottom of the cutter, do the flutes extend?
        self.automatically_generate_title = True    #// Set to true by default but reset to false when the user edits the title.
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
    
    def CanEditString(self):
        return not self.automatically_generate_title
    
    def OnEditString(self, new_title):
        self.title = str(new_title)

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
        self.corner_radius = object.corner_radius
        self.flat_radius = object.flat_radius
        self.cutting_edge_angle = object.cutting_edge_angle
        self.cutting_edge_height = object.cutting_edge_height
        self.automatically_generate_title = object.automatically_generate_title
        self.title = object.title
            
        CamObject.CopyFrom(self, object)
        
    def CanAddTo(self, owner):
        return owner.GetType() == Tools.type
    
    def PreferredPasteTarget(self):
        return wx.GetApp().program.tools
    
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
        properties.append(PyChoiceProperty("Material", 'material', ['High Speed Steel', 'Carbide'], self, recalculate = self.ResetTitle))
        properties.append(PyChoiceProperty("Type", 'type', GetToolTypeNames(), self, GetToolTypeValues(), recalculate = self.ResetTitle))
        properties.append(PyPropertyLength("Diameter", 'diameter', self, recalculate = self.ResetTitle))
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
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetData()
            return True
        return False
        
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
    
    def OCLDefinition(self, surface):
        import ocl
        if self.type == TOOL_TYPE_BALLENDMILL:
            return ocl.BallCutter(self.diameter + surface.material_allowance * 2, 1000)
        elif self.type == TOOL_TYPE_CHAMFER or self.type == TOOL_TYPE_ENGRAVER:
            return ocl.CylConeCutter(self.flat_radius * 2 + surface.material_allowance, self.diameter + surface.material_allowance * 2, self.cutting_edge_angle * math.pi/360)
        else:
            if self.corner_radius > 0.000000001:
                return ocl.BullCutter(self.diameter + surface.material_allowance * 2, self.corner_radius, 1000)
            else:
                return ocl.CylCutter(self.diameter + surface.material_allowance * 2, 1000)

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
