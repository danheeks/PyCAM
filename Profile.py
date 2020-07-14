from SketchOp import SketchOp
import geom
import cad
import Tool
from Object import PyChoiceProperty
from Object import PyProperty
from Object import PyPropertyLength
from SpeedOp import SpeedOp
import wx
from nc.nc import *
import kurve_funcs
from HeeksConfig import HeeksConfig
import Tags
import Tag
import math

PROFILE_RIGHT_OR_INSIDE = -1
PROFILE_ON = 0
PROFILE_LEFT_OR_OUTSIDE = 1

PROFILE_CONVENTIONAL = 0
PROFILE_CLIMB = 1

type = 0

class Profile(SketchOp):
    def __init__(self, sketch = 0):
        SketchOp.__init__(self, sketch)
        self.tool_on_side = PROFILE_LEFT_OR_OUTSIDE
        self.cut_mode = PROFILE_CLIMB
        self.auto_roll_radius = 2.0
        self.auto_roll_on = True
        self.auto_roll_off = True
        self.roll_on_point = geom.Point3D(0,0,0)
        self.roll_off_point = geom.Point3D(0,0,0)
        self.start_given = False
        self.end_given = False
        self.start = geom.Point3D(0,0,0)
        self.end = geom.Point3D(0,0,0)
        self.sort_sketches = True
        self.tags = None
        self.offset_extra = 0.0
        self.do_finishing_pass = False
        self.only_finishing_pass = False
        self.finishing_h_feed_rate = 100.0
        self.finishing_cut_mode = PROFILE_CONVENTIONAL
        self.finishing_step_down = 1.0
        self.end_beyond_full_profile = False
        self.extend_at_start = 0.0
        self.extend_at_end = 0.0
        self.lead_in_line_len = 0.0
        self.lead_out_line_len = 0.0
        
    def TypeName(self):
        return "Profile"

    def GetType(self):
        return type
    
    def op_icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "profile"
    
    def HasEdit(self):
        return True

    def Edit(self):
        import ProfileDlg
        res =  ProfileDlg.Do(self)
        return res
        
    def MakeACopy(self):
        copy = Profile(self.sketch)
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        SketchOp.CopyFrom(self, object)
        self.tool_on_side = object.tool_on_side
        self.cut_mode = object.cut_mode
        self.auto_roll_radius = object.auto_roll_radius
        self.auto_roll_on = object.auto_roll_on
        self.auto_roll_off = object.auto_roll_off
        self.roll_on_point = object.roll_on_point
        self.roll_off_point = object.roll_off_point
        self.start_given = object.start_given
        self.end_given = object.end_given
        self.start = object.start
        self.end = object.end
        self.extend_at_start = object.extend_at_start
        self.extend_at_end = object.extend_at_end
        self.lead_in_line_len = object.lead_in_line_len
        self.lead_out_line_len = object.lead_out_line_len
        self.end_beyond_full_profile = object.end_beyond_full_profile
        self.sort_sketches = object.sort_sketches
        self.offset_extra = object.offset_extra
        self.do_finishing_pass = object.do_finishing_pass
        self.only_finishing_pass = object.only_finishing_pass
        self.finishing_h_feed_rate = object.finishing_h_feed_rate
        self.finishing_cut_mode = object.finishing_cut_mode
        self.finishing_step_down = object.finishing_step_down
        
    def WriteXml(self):
        cad.BeginXmlChild('params')
        cad.SetXmlValue('side', self.tool_on_side)
        cad.SetXmlValue('cut_mode', self.cut_mode)
        cad.SetXmlValue('auto_roll_on', self.auto_roll_on)
        if not self.auto_roll_on:
            cad.SetXmlValue('roll_onx', self.roll_on_point.x)
            cad.SetXmlValue('roll_ony', self.roll_on_point.y)
            cad.SetXmlValue('roll_onz', self.roll_on_point.z)
        cad.SetXmlValue('auto_roll_off', self.auto_roll_off)
        if not self.auto_roll_off:
            cad.SetXmlValue('roll_offx', self.roll_off_point.x)
            cad.SetXmlValue('roll_offy', self.roll_off_point.y)
            cad.SetXmlValue('roll_offz', self.roll_off_point.z)
        if self.auto_roll_on or self.auto_roll_off:
            cad.SetXmlValue('roll_radius', self.auto_roll_radius)
        cad.SetXmlValue('start_given', self.start_given)
        if self.start_given:
            cad.SetXmlValue('startx', self.start.x)
            cad.SetXmlValue('starty', self.start.y)
            cad.SetXmlValue('startz', self.start.z)
        cad.SetXmlValue('end_given', self.end_given)
        if self.end_given:
            cad.SetXmlValue('endx', self.end.x)
            cad.SetXmlValue('endy', self.end.y)
            cad.SetXmlValue('endz', self.end.z)
            cad.SetXmlValue('end_beyond_full_profile', self.end_beyond_full_profile)
        cad.SetXmlValue('sort_sketches', self.sort_sketches)
        cad.SetXmlValue('extend_at_start', self.extend_at_start)
        cad.SetXmlValue('extend_at_end', self.extend_at_end)
        cad.SetXmlValue('lead_in_line_len', self.lead_in_line_len)
        cad.SetXmlValue('lead_out_line_len', self.lead_out_line_len)
        cad.SetXmlValue('offset_extra', self.offset_extra)
        cad.SetXmlValue('do_finishing_pass', self.do_finishing_pass)
        cad.SetXmlValue('only_finishing_pass', self.only_finishing_pass)
        cad.SetXmlValue('finishing_feed_rate', self.finishing_h_feed_rate)
        cad.SetXmlValue('finish_cut_mode', self.finishing_cut_mode)
        cad.SetXmlValue('finishing_step_down', self.finishing_step_down)
        cad.EndXmlChild()
        SketchOp.WriteXml(self)
        
    def ReadXml(self):
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'params':
                self.tool_on_side = cad.GetXmlInt('side', self.tool_on_side)
                self.cut_mode = cad.GetXmlInt('cut_mode', self.cut_mode)
                self.auto_roll_on = cad.GetXmlBool('auto_roll_on', self.auto_roll_on)
                self.roll_on_point.x = cad.GetXmlFloat('roll_onx', self.roll_on_point.x)
                self.roll_on_point.y = cad.GetXmlFloat('roll_ony', self.roll_on_point.y)
                self.roll_on_point.z = cad.GetXmlFloat('roll_onz', self.roll_on_point.z)
                self.auto_roll_off = cad.GetXmlBool('auto_roll_off', self.auto_roll_off)
                self.roll_off_point.x = cad.GetXmlFloat('roll_offx', self.roll_off_point.x)
                self.roll_off_point.y = cad.GetXmlFloat('roll_offy', self.roll_off_point.y)
                self.roll_off_point.z = cad.GetXmlFloat('roll_offz', self.roll_off_point.z)
                self.auto_roll_radius = cad.GetXmlFloat('roll_radius', self.auto_roll_radius)
                self.start_given = cad.GetXmlBool('start_given', self.start_given)
                self.start.x = cad.GetXmlFloat('startx', self.start.x)
                self.start.y = cad.GetXmlFloat('starty', self.start.y)
                self.start.z = cad.GetXmlFloat('startz', self.start.z)
                self.end_given = cad.GetXmlBool('end_given', self.end_given)
                self.end.x = cad.GetXmlFloat('endx', self.end.x)
                self.end.y = cad.GetXmlFloat('endy', self.end.y)
                self.end.z = cad.GetXmlFloat('endz', self.end.z)
                self.end_beyond_full_profile = cad.GetXmlBool('end_beyond_full_profile', self.end_beyond_full_profile)
                self.sort_sketches = cad.GetXmlBool('sort_sketches', self.sort_sketches)
                self.offset_extra = cad.GetXmlFloat('offset_extra', self.offset_extra)
                self.do_finishing_pass = cad.GetXmlBool('do_finishing_pass', self.do_finishing_pass)
                self.only_finishing_pass = cad.GetXmlBool('only_finishing_pass', self.only_finishing_pass)
                self.finishing_h_feed_rate = cad.GetXmlFloat('finishing_feed_rate', self.finishing_h_feed_rate)
                self.finishing_cut_mode = cad.GetXmlInt('finish_cut_mode', self.finishing_cut_mode)
                self.finishing_step_down = cad.GetXmlFloat('finishing_step_down', self.finishing_step_down)
                self.extend_at_start = cad.GetXmlFloat('extend_at_start', self.extend_at_start)
                self.extend_at_end = cad.GetXmlFloat('extend_at_end', self.extend_at_end)
                self.lead_in_line_len = cad.GetXmlFloat('lead_in_line_len', self.lead_in_line_len)
                self.lead_out_line_len = cad.GetXmlFloat('lead_out_line_len', self.lead_out_line_len)
            if child_element == 'Tags':
                self.tags = cad.GetXmlObject()
                self.Add(self.tags)
                
            child_element = cad.GetNextXmlChild()

        SketchOp.ReadXml(self)
        
    def CallsObjListReadXml(self):
        return False
        
    def ReadDefaultValues(self):
        SketchOp.ReadDefaultValues(self)
        config = HeeksConfig()
        self.tool_on_side = config.ReadInt("ToolOnSide", PROFILE_LEFT_OR_OUTSIDE)
        self.cut_mode = config.ReadInt("CutMode", PROFILE_CLIMB)
        self.auto_roll_radius = config.ReadFloat("RollRadius", 2.0)
        self.offset_extra = config.ReadFloat("OffsetExtra", 0.0)
        self.do_finishing_pass = config.ReadBool("DoFinishPass", False)
        self.only_finishing_pass = config.ReadBool("OnlyFinishPass", False)
        self.finishing_h_feed_rate = config.ReadFloat("FinishFeedRate", 100.0)
        self.finishing_cut_mode = config.ReadInt("FinishCutMode", PROFILE_CONVENTIONAL)
        self.finishing_step_down = config.ReadFloat("FinishStepDown", 1.0)
        self.end_beyond_full_profile = config.ReadBool("EndBeyond", False)
        self.extend_at_start = config.ReadFloat("ExtendAtStart", 0.0)
        self.extend_at_end = config.ReadFloat("ExtendAtEnd", 0.0)
        self.lead_in_line_len = config.ReadFloat("LeadInLineLen", 0.0)
        self.lead_out_line_len = config.ReadFloat("LeadOutLineLen", 0.0)
        
    def WriteDefaultValues(self):
        SketchOp.WriteDefaultValues(self)
        config = HeeksConfig()
        config.WriteInt("ToolOnSide", self.tool_on_side)
        config.WriteInt("CutMode", self.cut_mode)
        config.WriteFloat("RollRadius", self.auto_roll_radius)
        config.WriteFloat("OffsetExtra", self.offset_extra)
        config.WriteBool("DoFinishPass", self.do_finishing_pass)
        config.WriteBool("OnlyFinishPass", self.only_finishing_pass)
        config.WriteFloat("FinishFeedRate", self.finishing_h_feed_rate)
        config.WriteInt("FinishCutMode", self.finishing_cut_mode)
        config.WriteFloat("FinishStepDown", self.finishing_step_down)
        config.WriteBool("EndBeyond", self.end_beyond_full_profile)
        config.WriteFloat("ExtendAtStart", self.extend_at_start)
        config.WriteFloat("ExtendAtEnd", self.extend_at_end)
        config.WriteFloat("LeadInLineLen", self.lead_in_line_len)
        config.WriteFloat("LeadOutLineLen", self.lead_out_line_len)
            
    def GetProperties(self):
        properties = []

        sketch_order = cad.SketchOrderType.SketchOrderTypeUnknown
        sketch_object = cad.GetObjectFromId(cad.OBJECT_TYPE_SKETCH, self.sketch)
        if sketch_object != None:
            sketch_order = sketch_object.GetSketchOrder()
        choices = []
        if sketch_order == cad.SketchOrderType.SketchOrderTypeOpen:
            choices.append('Left')
            choices.append('Right')
        elif sketch_order == cad.SketchOrderType.SketchOrderTypeCloseCW or sketch_order == cad.SketchOrderType.SketchOrderTypeCloseCCW:
            choices.append('Outside')
            choices.append('Inside')
        else:
            choices.append('Outside or Left')
            choices.append('Inside or Right')
        choices.append('On')
        choice = 0
        if self.tool_on_side == PROFILE_RIGHT_OR_INSIDE:
            choice = 1
        elif self.tool_on_side == PROFILE_LEFT_OR_OUTSIDE:
            choice = 2
        properties.append(PyChoiceProperty("Tool On Side", 'tool_on_side', choices, self, alternative_values = [PROFILE_LEFT_OR_OUTSIDE, PROFILE_RIGHT_OR_INSIDE, PROFILE_ON]))

        properties.append(PyChoiceProperty("Cut Mode", 'cut_mode', ['Conventional', 'Climb'], self))
        properties.append(PyProperty("Auto Roll On", 'auto_roll_on', self))
        properties.append(PyProperty("Roll On Point", 'roll_on_point', self))
        properties.append(PyProperty("Auto Roll Off", 'auto_roll_off', self))
        properties.append(PyProperty("Roll Off Point", 'roll_off_point', self))
        properties.append(PyPropertyLength("Roll Radius", 'auto_roll_radius', self))
        properties.append(PyProperty("Use Start Point", 'start_given', self))
        properties.append(PyProperty("Start Point", 'start', self))
        properties.append(PyProperty("Use End Point", 'end_given', self))
        properties.append(PyProperty("End Point", 'end', self))
        properties.append(PyProperty("End Beyond Full Profile", 'end_beyond_full_profile', self))
        properties.append(PyPropertyLength("Extend Before Start", 'extend_at_start', self))
        properties.append(PyPropertyLength("Extend Past End", 'extend_at_end', self))
        properties.append(PyPropertyLength("Lead In Line Length", 'lead_in_line_len', self))
        properties.append(PyPropertyLength("Lead Out Line Length", 'lead_out_line_len', self))
        properties.append(PyPropertyLength("Offset Extra", 'offset_extra', self))
        properties.append(PyProperty("Do Finishing Pass", 'do_finishing_pass', self))
        properties.append(PyProperty("Only Finishing Pass", 'only_finishing_pass', self))
        properties.append(PyProperty("Finishing Feed Rate", 'finishing_h_feed_rate', self))
        properties.append(PyChoiceProperty("Finish Cut Mode", 'finishing_cut_mode', ['Conventional', 'Climb'], self))
        properties.append(PyPropertyLength("Finishing Step Down", 'finishing_step_down', self))
        
        properties += SketchOp.GetProperties(self)

        return properties
    
    def DoGCodeCallsForSketch(self, object, data):
        cut_mode, depth_params, tool_diameter, roll_radius, offset_extra, cutting_edge_angle = data
        
        # decide if we need to reverse the kurve
        reversed = False
        initially_ccw = False
        if self.tool_on_side != PROFILE_ON:
            if object.GetType() == cad.OBJECT_TYPE_CIRCLE:
                initially_ccw = True
            if object.GetType() == cad.OBJECT_TYPE_SKETCH:
                order = object.GetSketchOrder()
                if order == cad.SketchOrderType.SketchOrderTypeCloseCCW:
                    initially_ccw = True
            if self.spindle_speed<0:reversed = not reversed
            if cut_mode == PROFILE_CONVENTIONAL: reversed = not reversed
            if self.tool_on_side == PROFILE_RIGHT_OR_INSIDE: reversed = not reversed
            
        curve = object.GetCurve()
        
        if self.start_given or self.end_given:
            start = None
            if self.start_given:
                start = geom.Point(self.start.x, self.start.y)
            end = None
            end_beyond = False
            if self.end_given:
                end = geom.Point(self.end.x, self.end.y)
                end_beyond = self.end_beyond_full_profile
            kurve_funcs.make_smaller(curve, start, end, end_beyond)

        if curve.NumVertices() <= 1:
            raise NameError("sketch has no spans! object = " + object.GetTitle() + ' curve = ' + str(curve))

        if initially_ccw != reversed:
            curve.Reverse()
            
        if ( not self.start_given ) and ( not self.end_given ):
            kurve_funcs.set_good_start_point(curve, reversed)
            
        # start - assume we are at a suitable clearance height
        
        # get offset side string
        side_string = 'on'
        if self.tool_on_side == PROFILE_LEFT_OR_OUTSIDE:
            side_string = 'right' if reversed else 'left'
        elif self.tool_on_side == PROFILE_RIGHT_OR_INSIDE:
            side_string = 'left' if reversed else 'right'
            
        # roll on
        if self.tool_on_side == PROFILE_LEFT_OR_OUTSIDE or self.tool_on_side == PROFILE_RIGHT_OR_INSIDE:
            if self.auto_roll_on:
                roll_on = 'auto'
            else:
                roll_on = geom.Point(self.roll_on_point.x/wx.GetApp().program.units, self.roll_on_point.ywx.GetApp().program.units)
        else:
            roll_on = None
            
        # roll off
        if self.tool_on_side == PROFILE_LEFT_OR_OUTSIDE or self.tool_on_side == PROFILE_RIGHT_OR_INSIDE:
            if self.auto_roll_off:
                roll_off = 'auto'
            else:
                roll_off = geom.Point(self.roll_off_point.x/wx.GetApp().program.units, self.roll_off_point.ywx.GetApp().program.units)
        else:
            roll_off = None
            
        tags_cleared = False
        for tag in self.GetTags():
            if not tags_cleared:
                kurve_funcs.clear_tags()
            tags_cleared = True
            kurve_funcs.add_tag(geom.Point(tag.pos.x / wx.GetApp().program.units, tag.pos.y / wx.GetApp().program.units), tag.width / wx.GetApp().program.units, tag.angle * math.pi / 180.0, tag.height / wx.GetApp().program.units)
        
        # extend_at_start, extend_at_end
        extend_at_start = self.extend_at_start / wx.GetApp().program.units
        extend_at_end = self.extend_at_end / wx.GetApp().program.units
        
        # lead in lead out line length
        lead_in_line_len = self.lead_in_line_len / wx.GetApp().program.units
        lead_out_line_len = self.lead_out_line_len / wx.GetApp().program.units
        
        # profile the kurve
        kurve_funcs.profile(curve, side_string, tool_diameter / 2, offset_extra, roll_radius, roll_on, roll_off, depth_params, extend_at_start,extend_at_end,lead_in_line_len,lead_out_line_len)
        
        # do we need this here
        absolute()

    def DoGCodeCallsForPass(self, finishing_pass):
        tool = Tool.FindTool(self.tool_number)
        if tool == None:
            wx.MessageBox('Cannot generate G-Code for profile without a tool assigned')
            return
        
        depthparams = self.GetDepthParams()
        if not finishing_pass or self.only_finishing_pass:
            SpeedOp.DoGCodeCalls(self)
        
        if self.auto_roll_on or self.auto_roll_off:
            roll_radius = self.auto_roll_radius / wx.GetApp().program.units
        else:
            roll_radius = None
                
        depth_params = self.GetDepthParams()
        tool_diameter = tool.CuttingRadius(True) * 2.0
        cutting_edge_angle = tool.cutting_edge_angle
            
        if finishing_pass:
            feedrate_hv(self.finishing_h_feed_rate / wx.GetApp().program.units, self.vertical_feed_rate / wx.GetApp().program.units)
            flush_nc()
            offset_extra = 0.0
            depth_params.step_down = self.finishing_step_down
            depth_params.z_finish_depth = 0.0
        else:
            offset_extra = self.offset_extra /  wx.GetApp().program.units
            
        cut_mode = self.finishing_cut_mode if finishing_pass else self.cut_mode
        
        self.DoEachSketch(self.DoGCodeCallsForSketch, (cut_mode, depth_params, tool_diameter, roll_radius, offset_extra, cutting_edge_angle))
                    
    def GetTags(self):
        if self.tags == None:
            return []
        else:
            return self.tags.GetChildren()
            
    def DoGCodeCalls(self):
        # roughing pass
        if not self.do_finishing_pass or not self.only_finishing_pass:
            self.DoGCodeCallsForPass(False)

        # finishing pass
        if self.do_finishing_pass:
            self.DoGCodeCallsForPass(True)
            
    def AddMissingChildren(self):
        # add tags
        self.tags = Tags.Tags()
        self.Add(self.tags)
        
    def OnGlCommands(self, select, marked, no_color):
        if self.tags:
            object = self.tags.GetFirstChild()
            while object:
                object.OnGlCommands(select, marked, no_color)
                object = self.tags.GetNextChild()

class TagDrawing(cad.Drawing):
    def __init__(self):
        cad.Drawing.__init__(self)
        self.profile = None
        
    # cad.InputMode's overridden method
    def GetTitle(self):
        return "Tag Drawing"
    
    def IsAnAddLevel(self, level):
        return True
    
    def NumberOfSteps(self):
        return 1
        
    def CalculateItem(self, end):
        if end.type == cad.DigitizeType.DIGITIZE_NO_ITEM_TYPE:
            return False

        if (self.TempObject() != None) and (self.TempObject().GetType() != Tag.type):
            self.ClearObjectsMade()

        if self.TempObject() == None:
            tag = Tag.Tag()
            self.AddToTempObjects(tag)
        else:
            self.TempObject().pos.x = end.point.x
            self.TempObject().pos.y = end.point.y
        return True
            
    def GetOwnerForDrawingObjects(self):
        return self.profile.tags
        
tag_drawing = TagDrawing()        
            