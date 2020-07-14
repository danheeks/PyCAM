from AutoProgramDlg import AutoProgramDlg
from HeeksConfig import HeeksConfig
import wx
import cad
import geom
import math
import step
import Program
import NcCode
import Stock
import Profile
import Tag
import Tags
import Tool
from consts import *

MOVE_START_NOT = 0
MOVE_START_TO_MIDDLE_LEFT = 1

BOTTOM_NONE = 0
BOTTOM_THROUGH = 1
BOTTOM_POCKET = 2

class DefaultTool:
    def __init__(self, diam, type, hfeed, finish_hfeed, spin, vfeed, rough_step_down, finish_step_down):
        self.diam = diam
        self.type = type
        self.hfeed = hfeed
        self.finish_hfeed = finish_hfeed
        self.spin = spin
        self.vfeed = vfeed
        self.rough_step_down = rough_step_down
        self.finish_step_down = finish_step_down
        
    def GetName(self):
        if self.type == TOOL_TYPE_SLOTCUTTER:
            return str(self.diam) + ' mm Slot Cutter'
        elif self.type == TOOL_TYPE_DRILL:
            return str(self.diam) + ' mm Drill'
        else:
            return 'Unknown Tool Type'
        
    def AddTool(self, tool_number):
        tool = Tool.Tool(self.diam, title = self.GetName(), tool_number = tool_number, type = self.type)
        cad.PyIncref(tool)
        cad.AddUndoably(tool, wx.GetApp().program.tools)

default_tools = {
                 1:DefaultTool(16.0, TOOL_TYPE_SLOTCUTTER, 200.0, 100.0, 1800.0, 50.0, 5.0, 10.0),
                 2:DefaultTool(2.5, TOOL_TYPE_DRILL, None, None, 3000.0, 150.0, 1.0, None),
                 3:DefaultTool(6.0, TOOL_TYPE_SLOTCUTTER, 200.0, 100.0, 3000.0, 100.0, 3.0, 6.0),
                 4:DefaultTool(2.0, TOOL_TYPE_SLOTCUTTER, 150.0, 75.0, 3000.0, 50.0, 1.0, 2.0),
                 5:DefaultTool(5.0, TOOL_TYPE_SLOTCUTTER, 200.0, 100.0, 3000.0, 100.0, 2.5, 5.0),
                 6:DefaultTool(3.0, TOOL_TYPE_SLOTCUTTER, 150.0, 75.0, 3000.0, 50.0, 1.5, 3.0),
                 }

stock_thicknesses = {
                 'Acetal':[5.0, 6.0, 10.0, 20.0, 30.0, 40.0],
                 'Alu Alloy':[2.0, 3.0, 4.0, 5.0, 6.0, 10.0, 16.0, 20.0, 30.0, 40.0],
                 'Mild Steel':[2.0, 3.0, 4.0, 5.0, 6.0],
                 }

default_options = {
                   "machine":"emc2b",
                   "outer_tool_diameter":6.0,
                   "tools":default_tools,
                   }

class AutoProgram:
    def __init__(self):
        self.ReadFromConfig()
    
    def ReadFromConfig(self):
        config = HeeksConfig()
        self.x_margin = config.ReadFloat('XMargin', 20.0)
        self.y_margin = config.ReadFloat('YMargin', 3.0)
        self.material = config.Read('Material', 'Alu Alloy')
        self.create_gcode = config.ReadBool('CreateGCode', True)
        self.tag_width = config.ReadFloat('TagWidth', 5.0)
        self.tag_height = config.ReadFloat('TagHeight', 1.0)
        self.tag_angle = config.ReadFloat('TagAngle', 45.0)
        self.tag_y_margin = config.ReadFloat('TagYMargin', 4.0)
        
    def WriteToConfig(self):
        config = HeeksConfig()
        config.WriteFloat('XMargin', self.x_margin)
        config.WriteFloat('YMargin', self.y_margin)
        config.Write('Material', self.material)
        config.WriteBool('CreateGCode', self.create_gcode)
        config.WriteFloat('TagWidth', self.tag_width)
        config.WriteFloat('TagHeight', self.tag_height)
        config.WriteFloat('TagAngle', self.tag_angle)
        config.WriteFloat('TagYMargin', self.tag_y_margin)
    
    def Edit(self):
        dlg = AutoProgramDlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetData(self)
            self.WriteToConfig()
            return True
        return False
    
    def Run(self):
        # automatically create stocks, tools, operations, g-code
        self.part = self.GetPart()
        if self.part == None:
            wx.MessageBox('No Solid Found!')
            return
        
        # clear existing program
        self.ClearProgram()
        
        # add a cube and stock referencing it
        self.AddStock()
        
        # move the part, so stock is at origin
        self.MovePart()
        
        self.CutOutside()
        
        if self.create_gcode:
            wx.GetApp().program.MakeGCode()
            wx.GetApp().program.BackPlot()
        
    def CutOutside(self):
        self.part_stl = self.part.GetTris(0.01)
        self.part_box = self.part_stl.GetBox()
        self.clearance_height = self.part_box.MaxZ() + 5.0
        mat = geom.Matrix()
        self.shadow = self.part_stl.Shadow(mat, False)
        self.shadow.Reorder()
        self.stock_area = self.MakeStockArea(self.shadow, self.x_margin, self.y_margin, self.x_margin, self.y_margin)
        self.area_done = geom.Area()
        self.solid_area = None
        self.current_top_height = None
        self.tools_defined = {}

        for curve in self.shadow.GetCurves():
            if not curve.IsClockwise():
                self.ProfileCurve(curve, move_start_type = MOVE_START_TO_MIDDLE_LEFT, add_tags = True)         
        
    def DefineToolIfNotAlready(self, tool_id):
        if tool_id in self.tools_defined:
            return
        #(6 mm Slot Cutter)
        self.tools_defined[tool_id] = 1
        
        default_tools[tool_id].AddTool(tool_id)
                
    def ProfileCurve(self, curve, z_top = 0.0, z_bottom = None, move_start_type = MOVE_START_NOT, bottom_style = BOTTOM_THROUGH, do_finish_pass = True, add_tags = False):
        # create a sketch for the curve
        sketch = cad.NewSketchFromCurve(curve)
            
        cad.AddUndoably(sketch)
        
        tool_id = self.GetToolForCurve(curve)
                
        if tool_id == None:
            return # shouldn't happen

        self.DefineToolIfNotAlready(tool_id)

        profile = Profile.Profile(sketch.GetID())
        profile.tool_number = tool_id
        profile.start_depth = z_top
        if z_bottom == None:
            profile.final_depth = -self.thickness
        else:
            profile.final_depth = z_bottom

        if move_start_type == MOVE_START_TO_MIDDLE_LEFT:
            profile.start_given = True
            box = curve.GetBox()
            profile.start = geom.Point(box.MinX(), (box.MinY() + box.MaxY())*0.5)
            
        if bottom_style == BOTTOM_THROUGH:
            profile.z_thru_depth = 1.0 # to do, use more of the tool?
        elif bottom_style == BOTTOM_POCKET:
            profile.z_finish_depth = 0.1

        # set operation from chosen tool info
        profile.horizontal_feed_rate = default_tools[tool_id].hfeed
        profile.vertical_feed_rate = default_tools[tool_id].vfeed
        profile.spindle_speed = default_tools[tool_id].spin
        profile.step_down = default_tools[tool_id].rough_step_down
            
        if do_finish_pass:
            profile.do_finishing_pass = True
            profile.offset_extra = 0.1
            profile.roll_radius = 0.1
            profile.finishing_h_feed_rate = default_tools[tool_id].finish_hfeed
            profile.finishing_step_down = default_tools[tool_id].finish_step_down
            
        if add_tags:
            offset_curve = geom.Curve(curve)
            radius = default_tools[tool_id].diam * 0.5
            offset_curve.Offset(-radius)
            box = offset_curve.GetBox()
            left = box.MinX() - 1.0
            right = box.MaxX() + 1.0
            if box.Height() < (2 * self.tag_y_margin + self.tag_width):
                # 2 tags in the middle
                y_mid = (box.MinY() + box.MaxY()) * 0.5
                lines = [ [ [left, y_mid], [right, y_mid] ], [[right, y_mid], [left, y_mid]] ]
            else:
                # 4 tags
                y_upper = box.MaxY() - self.tag_y_margin
                y_lower = box.MinY() + self.tag_y_margin
                lines = [ [ [left, y_upper], [right, y_upper] ], [[right, y_upper], [left, y_upper]], [ [left, y_lower], [right, y_lower] ], [[right, y_lower], [left, y_lower]] ]
            for line in lines:
                p = FindTagPoint(offset_curve, line)
                if p != None:
                    tag = Tag.Tag()
                    tag.width = self.tag_width
                    tag.height = self.tag_height
                    tag.angle = self.tag_angle
                    tag.pos = p
                    cad.PyIncref(tag)
                    if profile.tags == None:
                        tags = Tags.Tags()
                        cad.PyIncref(tags)
                        profile.Add(tags)
                        profile.tags = tags
                    profile.tags.Add(tag)

        cad.PyIncref(profile)
        cad.AddUndoably(profile, wx.GetApp().program.operations)

    def ClearProgram(self):
        # check if there are any exisiting operations in the program
        if wx.GetApp().program.operations.GetNumChildren() > 0:
            if wx.MessageBox('The program already has operations. Do you want to continue and overwrite them?', style = wx.YES_NO) != wx.YES:
                return
        
        cad.StartHistory()
        for object in wx.GetApp().program.tools.GetChildren():
            cad.DeleteUndoably(object)
        for object in wx.GetApp().program.patterns.GetChildren():
            cad.DeleteUndoably(object)
        for object in wx.GetApp().program.surfaces.GetChildren():
            cad.DeleteUndoably(object)
        for object in wx.GetApp().program.stocks.GetChildren():
            cad.DeleteUndoably(object)
        for object in wx.GetApp().program.operations.GetChildren():
            cad.DeleteUndoably(object)
        cad.CopyUndoably(wx.GetApp().program.nccode, NcCode.NcCode())
        cad.EndHistory()
        
    def AddStock(self):
        self.part_box = self.part.GetBox()
        if not self.material in stock_thicknesses:
            raise NameError('material not found in stock: ' + self.material)
            
        thicknesses = stock_thicknesses[self.material]
        if len(thicknesses) == 0:
            raise NameError('no stock available for material, material: ' + self.material)
            
        for thickness in thicknesses:
            if thickness >= self.part_box.Depth():
                cuboid = step.NewCuboid()
                cuboid.width = self.part_box.Width() + 2 * self.x_margin
                cuboid.height = self.part_box.Height() + 2 * self.y_margin
                cuboid.depth = thickness
                mat = geom.Matrix()
                mat.Translate(geom.Point3D(0,0,-thickness))
                cuboid.Transform(mat)
                cuboid.SetVisible(False)
                cad.AddUndoably(cuboid)
                new_stock = Stock.Stock()
                new_stock.solids.append(cuboid.GetID())
                cad.AddUndoably(new_stock, wx.GetApp().program.stocks)
                self.thickness = thickness
                return
            
        raise NameError('part too thick to make: material: ' + self.material + ', part thickness: ' + str(self.part_box.Depth()) + ', thickest stock available: ' + thicknesses[-1])
                
    def MovePart(self):
        part_box = self.part.GetBox()
        mat = geom.Matrix()
        # move down with bottom left corner at x_margin, y_margin and z top at z0
        mat.Translate(geom.Point3D(self.x_margin - part_box.MinX(), self.y_margin - part_box.MinY(), -part_box.MinZ() - self.thickness))
        cad.TransformUndoably(self.part, mat)
            
    def GetPart(self):
        for object in cad.GetObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_STL_SOLID:
                return object
        return None
        
    def MakeStockArea(self, a, extra_xminus, extra_yminus, extra_xplus, extra_yplus):
        box = a.GetBox()
        stock_area = geom.Area()
        c = geom.Curve()
        x0 = box.MinX() - math.fabs(extra_xminus)
        x1 = box.MaxX() + math.fabs(extra_xplus)
        y0 = box.MinY() - math.fabs(extra_yminus)
        y1 = box.MaxY() + math.fabs(extra_yplus)
        c.Append(geom.Point(x0, y0))
        c.Append(geom.Point(x1, y0))
        c.Append(geom.Point(x1, y1))
        c.Append(geom.Point(x0, y1))
        c.Append(geom.Point(x0, y0))
        stock_area.Append(c)
        return stock_area        

    def GetToolForCurve(self, curve, outside = True):
        r = curve.GetMaxCutterRadius()
        if r == None:
            tool_id = self.ChoosePreferredTool()
        else:
            if self.tools[self.ChoosePreferredTool()].diam <= r*2:
                tool_id = self.ChoosePreferredTool()
            else:
                tool_id = self.GetFirstToolGreaterOrEqual(r*2)
        
        #d = self.GetMaxOutsideDiameter()
        #tool = self.GetFirstToolGreaterOrEqual(d)
        return tool_id
    
    def GetMaxOutsideDiameter(self):
        max_diameter = None
        for curve in self.shadow.GetCurves():
            if not curve.IsClockwise():
                r = curve.GetMaxCutterRadius()
                if r != None:
                    d = r * 2
                    if max_diameter == None or d < max_diameter:
                        max_diameter = d
        return max_diameter
    
    def GetFirstToolGreaterOrEqual(self, d):
        if d == None:
            return None
        min_d = None
        min_d_tool = None
        for tool in default_tools:
            tool_diameter = default_tools[tool].diam
            if tool_diameter == d:
                return tool
            if tool_diameter > d:
                if min_d == None or tool_diameter < min_d:
                    min_d = tool_diameter
                    min_d_tool = tool
        return min_d_tool

    def ChoosePreferredTool(self):
        return 3 # use the 6mm tool

def FindTagPoint(curve, line):
    # line defined by two lists of two coordinates
    c2 = geom.Curve()
    c2.Append(geom.Point(line[0][0], line[0][1]))
    c2.Append(geom.Point(line[1][0], line[1][1]))
    pts = curve.Intersections(c2)
    print('pts = ' + str(pts[0]) + ', ' + str(pts[1]))
    if len(pts) == 0:
        return None
    return pts[0]