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
import Pocket
import Drilling
import Tag
import Tags
import Tool
from consts import *

MOVE_START_NOT = 0
MOVE_START_TO_MIDDLE_LEFT = 1

BOTTOM_NORMAL = 0
BOTTOM_THROUGH = 1
BOTTOM_POCKET = 2


class DefaultTool:
    def __init__(self, diam, type, cutting_length, hfeed, finish_hfeed, spin, vfeed, rough_step_down, finish_step_down = None):
        self.diam = diam
        self.type = type
        self.cutting_length = cutting_length
        self.hfeed = hfeed
        if hfeed == None:
            self.hfeed = 200.0
        self.finish_hfeed = finish_hfeed
        self.spin = spin
        self.vfeed = vfeed
        self.rough_step_down = rough_step_down
        self.finish_step_down = finish_step_down
        self.added_tool_id = None
        
    def GetName(self):
        if self.type == TOOL_TYPE_SLOTCUTTER:
            return str(self.diam) + ' mm Slot Cutter'
        elif self.type == TOOL_TYPE_DRILL:
            return str(self.diam) + ' mm Drill'
        else:
            return 'Unknown Tool Type'
        
    def NewTool(self, tool_number):
        tool = Tool.Tool(self.diam, title = self.GetName(), tool_number = tool_number, type = self.type)
        cad.PyIncref(tool)
        self.added_tool_id = tool_number
        return tool

slot_cutter_positions = [3,4,5,6]
drill_positions = [1,2,7,8,9]

BIG_CUTTER_DIAMETER = 6.0 # maximum cutter diameter allowed when big_rigid_part is not ticked, otherwise allow any size tool
        
class DefaultTools:
    def __init__(self, auto_program, name, tools, tool_numbers):
        self.auto_program = auto_program
        self.name = name
        self.tools = tools
        self.tool_numbers = tool_numbers
        self.next_index = 0
        
    def AddIfNotAdded(self, tool_index):
        tool = self.tools[tool_index]
        if tool.added_tool_id != None:
            return tool.added_tool_id, tool
        if self.next_index >= len(self.tool_numbers):
            self.failure = 'no more ' + self.name + ' available!\ntrying to add: ' + self.tools[tool_index].GetName()
            tool_id = 0
        else:
            tool_id = self.tool_numbers[self.next_index]
            self.next_index += 1
            self.auto_program.tools_to_add_at_end[tool_id] = tool.NewTool(tool_id)        
        return tool_id, tool
    
    def GetBiggestToolLessThanOrEqual(self, d, cut_depth):
        if d == None:
            return None
        max_d = None
        max_d_tool = None
        for index in range(0, len(self.tools)):
            if self.tools[index].cutting_length < cut_depth:
                continue
            tool_diameter = self.tools[index].diam
            if tool_diameter == d:
                return index
            if tool_diameter < d:
                if max_d == None or tool_diameter > max_d:
                    max_d = tool_diameter
                    max_d_tool = index
        return max_d_tool
    
    def GetToolOfDiameter(self, d, cut_depth, precision):
        for index in range(0, len(self.tools)):
            if self.tools[index].cutting_length < cut_depth:
                continue
            tool_diameter = self.tools[index].diam
            if math.fabs(tool_diameter - d) < precision:
                return index
        return None
    
    def GetDiamMapShortest(self, cut_depth, max_cutter_diameter):
        # map of diameter to found index for checking smallest cutter length
        index = 0
        diam_map = {} # map of diameter to found index for checking smallest cutter length
        for tool in self.tools:
            if max_cutter_diameter == None or max_cutter_diameter >= tool.diam:
                if tool.cutting_length >= cut_depth:
                    if tool.diam in diam_map:
                        # tool diameter already in map
                        existing_tool = self.tools[diam_map[tool.diam]]
                        if tool.cutting_length < existing_tool.cutting_length:
                            # replace map enty with shorter tool
                            diam_map[tool_diam] = index
                    else:
                        diam_map[tool.diam] = index
            index += 1
        return diam_map
    
    def BiggestShortest(self, cut_depth, max_cutter_diameter):
        diam_map = self.GetDiamMapShortest(cut_depth, max_cutter_diameter)
        # return first
        for d in sorted(diam_map.keys(), reverse = True):
            return diam_map[d]
        return None        
            
    def GetPatchCutters(self, cut_depth, max_cutter_diameter):
        diam_map = self.GetDiamMapShortest(cut_depth, max_cutter_diameter)
            
        # make the list from the map
        cutters = []
        for d in sorted(diam_map.keys(), reverse = True):
            cutters.append(diam_map[d])
        return cutters

class Hole:
    # used to group found features
    def __init__(self, circle, top_z, bottom_z):
        self.diameter = circle.radius * 2
        self.top_z = top_z
        self.bottom_z = bottom_z
        self.pts = [circle.c]
        
    def AddHole(self, hole, precision):
        # returns True if it added the hole's position to this hole
        if math.fabs(self.diameter - hole.diameter) > precision:
            return False
        if math.fabs(self.top_z - hole.top_z) > precision:
            return False
        if math.fabs(self.bottom_z - hole.bottom_z) > precision:
            return False
        self.pts += hole.pts
        return True
    
    def __str__(self):
        return 'Hole - diameter = ' + str(self.diameter) + ' at pts: ' + str(self.pts)

class AutoProgram:
    def __init__(self):
        self.ReadFromConfig()
        self.next_slot_cutter = 0
        self.next_drill = 0
        self.tools_to_add_at_end = {} # dictionary of tool id and Tool
        self.slot_cutters = DefaultTools(self, 'slot cutters', [
    DefaultTool(16.0, TOOL_TYPE_SLOTCUTTER, 30.0, 200.0, 100.0, 1800.0, 50.0, 5.0, 10.0), # short
    DefaultTool(16.0, TOOL_TYPE_SLOTCUTTER, 60.0, 200.0, 100.0, 1800.0, 50.0, 5.0, 10.0), # long
    DefaultTool(6.0, TOOL_TYPE_SLOTCUTTER, 15.0, 200.0, 100.0, 3000.0, 100.0, 3.0, 6.0), # short
    DefaultTool(6.0, TOOL_TYPE_SLOTCUTTER, 40.0, 200.0, 100.0, 3000.0, 100.0, 3.0, 6.0), # long
    DefaultTool(5.0, TOOL_TYPE_SLOTCUTTER, 25.0, 200.0, 100.0, 3000.0, 100.0, 2.5, 5.0),
    DefaultTool(4.0, TOOL_TYPE_SLOTCUTTER, 12.0, 200.0, 100.0, 3000.0, 50.0, 1.5, 3.0),
    DefaultTool(3.0, TOOL_TYPE_SLOTCUTTER, 15.0, 150.0, 75.0, 3000.0, 50.0, 1.5, 3.0),
    DefaultTool(2.0, TOOL_TYPE_SLOTCUTTER, 10.0, 150.0, 75.0, 3000.0, 50.0, 1.0, 2.0),
], slot_cutter_positions)
        self.drills = DefaultTools(self, 'drills', [
    # to do change 12.0 to actual cutting lengths
    DefaultTool(1.6, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(1.8, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(1.9, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(2.0, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(2.1, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(2.5, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(3.0, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(3.2, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(3.3, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(3.5, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(3.6, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(4.0, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
    DefaultTool(4.2, TOOL_TYPE_DRILL, 12.0, None, None, 3000.0, 150.0, 1.0),
], drill_positions)
        self.part = None
        self.failure = None
        self.warnings = []
        self.stock_thicknesses = {
                 'Acetal':[5.0, 6.0, 10.0, 20.0, 30.0, 40.0],
                 'Alu Alloy':[2.0, 3.0, 4.0, 5.0, 6.0, 10.0, 16.0, 20.0, 30.0, 40.0],
                 'Mild Steel':[2.0, 3.0, 4.0, 5.0, 6.0],
                 }

    
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
        self.big_rigid_part = config.ReadBool('BigRigidPart', False) # tick this to use the big cutter
        self.precision = config.ReadFloat('Precision', 0.1)
        
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
        config.WriteBool('BigRigidPart', self.big_rigid_part)
        config.WriteFloat('Precision', self.precision)
    
    def Edit(self):
        dlg = AutoProgramDlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetData(self)
            self.WriteToConfig()
            return True
        return False
    
    def Run(self):
        # automatically create stocks, tools, operations, g-code
        self.GetPart()
        
        # clear existing program
        self.ClearProgram()
        
        # add a cube and stock referencing it
        self.AddStock()
        
        # move the part, so stock is at origin
        self.MovePart()
        
        self.MakeShadow()
        self.CutShadowInners()
        self.CutPatches()
        self.CutOutside()
        
        self.AddToolsAtEnd()

        if self.failure:
            wx.MessageBox(self.failure, "ERROR!")
            return
        
        if len(self.warnings) > 0:
            s = ''
            for warning in self.warnings:
                if s:
                    s.append('\n')
                s.append(warning)
            wx.MessageBox(s, 'warnings only:')

        if self.create_gcode:
            wx.GetApp().program.MakeGCode()
            wx.GetApp().program.BackPlot()
            
        wx.GetApp().frame.graphics_canvas.viewport.OnMagExtents(True, 6)
        wx.GetApp().frame.graphics_canvas.Refresh()
        
    def AddToolsAtEnd(self):
        if self.failure: return
        for tool_id in self.tools_to_add_at_end:
            cad.AddUndoably(self.tools_to_add_at_end[tool_id], wx.GetApp().program.tools)
            
    def CutShadowInners(self):
        if self.failure: return
        curves_to_profile = []
        holes_to_profile = []
        holes_to_drill = []
        
        shadow_curves = self.shadow.GetCurves()
        for curve in shadow_curves:
            if curve.IsClockwise():
                circle = curve.IsACircle(self.precision)
                if circle == None:
                    curves_to_profile.append(curve)
                else:
                    hole = Hole(circle, 0.0, -self.thickness)
                    # add to existing holes
                    for h in holes_to_drill:
                        if h.AddHole(hole, self.precision):
                            hole = None
                            break
                    if hole != None:
                        holes_to_drill.append(hole)
                        
        for hole in holes_to_drill:
            cut_depth = hole.top_z - hole.bottom_z
            tool_index = self.drills.GetToolOfDiameter(hole.diameter, cut_depth, self.precision)
            if tool_index == None:
                # no drill of this size
                holes_to_profile.append(hole)
                continue
            tool_id, default_tool = self.drills.AddIfNotAdded(tool_index)
            drilling = Drilling.Drilling()
            drilling.tool_number = tool_id
            for p in hole.pts:
                new_point = cad.NewPoint(geom.Point3D(p.x, p.y, 0.0))
                cad.AddUndoably(new_point)
                drilling.points.append(new_point.GetID())
            drilling.start_depth = hole.top_z
            drilling.final_depth = hole.bottom_z
            drilling.horizontal_feed_rate = default_tool.hfeed
            drilling.vertical_feed_rate = default_tool.vfeed
            drilling.spindle_speed = default_tool.spin
            drilling.step_down = default_tool.rough_step_down
            cad.PyIncref(drilling)
            cad.AddUndoably(drilling, wx.GetApp().program.operations)
            
        for hole in holes_to_profile:
            self.ProfileHole(hole)
                        
        for curve in curves_to_profile:
            self.ProfileCurve(curve, inside = True)            

    def CutPatches(self):
        if self.failure: return
        
        for ma in self.part_stl.GetMachiningAreas():
            if ma.face_type == geom.FaceFlatType.Flat:
                if ma.bottom < -0.001:
                    # pocket area
                    
                    print('accuracy = ' + str(geom.get_accuracy()))
                    
                    # get a list of cutters ordered by biggest diameter first
                    cut_depth = ma.top - ma.bottom
                    patch_cutters = self.GetPatchCutters(cut_depth)
                    
                    # store area remaining to be cut, starting with the machining area's area
                    area_remaining = geom.Area(ma.area)
                    
                    for cutter_index in patch_cutters:
                        # start with the remaining area
                        a = geom.Area(area_remaining)
                        
                        # offset it outwards
                        cutter_radius = self.slot_cutters.tools[cutter_index].diam * 0.5
                        offset = cutter_radius + 0.1
                        a.Offset(-offset)
                        
                        print('accuracy = ' + str(geom.get_accuracy()))
                    
                        # subtract area already done ( areas above this one )
                        a.Subtract(self.area_done)

                        if self.PocketCanBeDoneWithProfileOp(a, cutter_index):
                            self.ProfileCurve(a.GetCurves()[0], cutter_index = cutter_index, z_bottom = ma.bottom, inside = True)
                        else:
                            self.PocketArea(a, cutter_index, z_bottom = ma.bottom)
                            
                        # calculate the remaining area
                        a.Offset(cutter_radius) # offset inwards
                        
                        # output sketch just for debugging
                        s = cad.NewSketchFromArea(a)
                        s.SetTitle('area cut by ' + str(cutter_radius * 2) + 'mm cutter, offset inwards')
                        cad.AddUndoably(s)

                        
                        a.Offset(-cutter_radius)# offset outwards ( rounds off the corners )

                        print('accuracy = ' + str(geom.get_accuracy()))
                    
                        # output sketch just for debugging
                        s = cad.NewSketchFromArea(a)
                        s.SetTitle('area cut by  ' + str(cutter_radius * 2) + 'mm cutter, offset back outwards')
                        cad.AddUndoably(s)
                        
                        # output sketch just for debugging
                        s = cad.NewSketchFromArea(area_remaining)
                        s.SetTitle('area_remaining before subtraction')
                        cad.AddUndoably(s)
                        
                        
                        area_remaining.Subtract(a)

                        # output sketch just for debugging
                        s = cad.NewSketchFromArea(area_remaining)
                        s.SetTitle('area_remaining after subtraction')
                        cad.AddUndoably(s)
                        
                        if area_remaining.NumCurves() == 0:
                            # nothing left to cut
                            break                    
            else:
                # handle 3d surfaces
                pass
            
            self.area_done.Union(ma.area)
        
    def MakeShadow(self):
        if self.failure: return
        self.part_stl = self.part.GetTris(self.precision)
        self.part_box = self.part_stl.GetBox()
        self.clearance_height = self.part_box.MaxZ() + 5.0
        mat = geom.Matrix()
        geom.set_fitarcs(False) # make sure FitArcs only happens when making the g-code
        self.shadow = self.part_stl.Shadow(mat, False)
        sketch = cad.NewSketchFromArea(self.shadow)
        cad.AddUndoably(sketch)
        self.shadow.Reorder()
        self.stock_area = self.MakeStockArea(self.shadow, self.x_margin, self.y_margin, self.x_margin, self.y_margin)
        self.area_done = geom.Area() # area_done starts empty, then is the area at the top ( top face ), then gets added to by each descending area until it should end up the same as the shadow of the part
        self.solid_area = None
        self.current_top_height = None
        
    def CutOutside(self):
        if self.failure: return
        for curve in self.shadow.GetCurves():
            if not curve.IsClockwise():
                self.ProfileCurve(curve, move_start_type = MOVE_START_TO_MIDDLE_LEFT, add_tags = True)         
                
    def ProfileHole(self, hole):
        radius = hole.diameter * 0.5
        for p in hole.pts:
            curve = geom.Curve()
            curve.Append(geom.Point(p.x - radius, p.y))
            curve.Append(geom.Vertex(1, geom.Point(p.x + radius, p.y), geom.Point(p.x, p.y)))
            curve.Append(geom.Vertex(1, geom.Point(p.x - radius, p.y), geom.Point(p.x, p.y)))
            self.ProfileCurve(curve, z_top = hole.top_z, z_bottom = hole.bottom_z, inside = True)
        
    def ProfileCurve(self, curve, cutter_index = None, z_top = 0.0, z_bottom = None, move_start_type = MOVE_START_NOT, bottom_style = BOTTOM_THROUGH, do_finish_pass = True, only_finishing = False, add_tags = False, inside = False):
        
        #check for thin artifact curves
        if math.fabs(curve.GetArea()) < 0.1:
            return
        
        # create a sketch for the curve
        sketch = cad.NewSketchFromCurve(curve)
        cad.AddUndoably(sketch)
        
        if z_bottom == None:
            cut_depth = self.thickness
        else:
            cut_depth = z_top - z_bottom
        
        if cutter_index == None:
            tool_id, default_tool = self.GetToolForCurve(curve, not inside, cut_depth)
        else:
            tool_id, default_tool = self.slot_cutters.AddIfNotAdded(cutter_index)
        if self.failure:
            return
        profile = Profile.Profile(sketch.GetID())
        profile.tool_number = tool_id
        profile.start_depth = z_top
        if z_bottom == None:
            profile.final_depth = -self.thickness
        else:
            profile.final_depth = z_bottom
            
        if inside == True:
            profile.tool_on_side = Profile.PROFILE_RIGHT_OR_INSIDE

        if move_start_type == MOVE_START_TO_MIDDLE_LEFT:
            profile.start_given = True
            box = curve.GetBox()
            profile.start = geom.Point3D(box.MinX(), (box.MinY() + box.MaxY())*0.5, 0.0)
            
        self.SetDepthOpBottomFromStyle(profile, bottom_style)

        # set operation from chosen tool info
        profile.horizontal_feed_rate = default_tool.hfeed
        profile.vertical_feed_rate = default_tool.vfeed
        profile.spindle_speed = default_tool.spin
        profile.step_down = default_tool.rough_step_down
            
        if do_finish_pass:
            profile.do_finishing_pass = True
            profile.only_finishing_pass = only_finishing
            profile.offset_extra = 0.1
            profile.finishing_h_feed_rate = default_tool.finish_hfeed
            profile.finishing_step_down = default_tool.finish_step_down
        profile.auto_roll_radius = 0.1
            
        if add_tags:
            offset_curve = geom.Curve(curve)
            radius = default_tool.diam * 0.5
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
        
    def PocketArea(self, a, cutter_index, z_top = 0.0, z_bottom = None, bottom_style = BOTTOM_NORMAL, do_finish_pass = True):
        # add the sketch to pocket or profile
        sketch = cad.NewSketchFromArea(a)
        cad.AddUndoably(sketch)
        
        # add the tool
        tool_id, default_tool = self.slot_cutters.AddIfNotAdded(cutter_index)
        
        pocket = Pocket.Pocket(sketch.GetID())
        pocket.tool_number = tool_id
        pocket.step_over = self.slot_cutters.tools[cutter_index].diam * 0.5
        pocket.start_depth = z_top
        pocket.final_depth = z_bottom
        pocket.horizontal_feed_rate = default_tool.hfeed
        pocket.vertical_feed_rate = default_tool.vfeed
        pocket.spindle_speed = default_tool.spin
        pocket.step_down = default_tool.rough_step_down
        
        self.SetDepthOpBottomFromStyle(pocket, bottom_style)

        cad.AddUndoably(pocket, wx.GetApp().program.operations)

    def SetDepthOpBottomFromStyle(self, depthop, bottom_style):
        if bottom_style == BOTTOM_THROUGH:
            depthop.z_thru_depth = 1.0 # to do, use more of the tool?
        elif bottom_style == BOTTOM_POCKET:
            depthop.z_finish_depth = 0.1

    def ClearProgram(self):
        if self.failure:
            return
        
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
        blank_nc = NcCode.NcCode()
        cad.PyIncref(blank_nc)
        wx.GetApp().CopyUndoably(wx.GetApp().program.nccode, blank_nc)
        cad.EndHistory()
        
    def AddStock(self):
        if self.failure: return
        
        self.part_box = self.part.GetBox()
        if not self.material in self.stock_thicknesses:
            self.failure = 'material not found in stock: ' + self.material
            return
            
        thicknesses = self.stock_thicknesses[self.material]
        if len(thicknesses) == 0:
            self.failure = 'no stock available for material, material: ' + self.material
            return
            
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
            
        self.failure = 'part too thick to make: material: ' + self.material + ', part thickness: ' + str(self.part_box.Depth()) + ', thickest stock available: ' + thicknesses[-1]
                
    def MovePart(self):
        if self.failure: return
        part_box = self.part.GetBox()
        mat = geom.Matrix()
        # move down with bottom left corner at x_margin, y_margin and z top at z0
        mat.Translate(geom.Point3D(self.x_margin - part_box.MinX(), self.y_margin - part_box.MinY(), -part_box.MinZ() - self.thickness))
        cad.TransformUndoably(self.part, mat)
            
    def GetPart(self):
        for object in cad.GetObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_STL_SOLID:
                self.part = object
                break
        if self.part == None:
            self.failure = 'No Solid Found!'
       
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

    def GetToolForCurve(self, curve, outside, cut_depth):
        r = curve.GetMaxCutterRadius(outside, self.precision)
        
        preferred_cutter = self.ChoosePreferredCutter(cut_depth)
        if self.failure:
            return 0, None
        if r == None:
            cutter_index = preferred_cutter
        else:
            if self.slot_cutters.tools[preferred_cutter].diam <= r*2:
                cutter_index = preferred_cutter
            else:
                cutter_index = self.slot_cutters.GetBiggestToolLessThanOrEqual(r*2, cut_depth)
                if cutter_index == None:
                    sketch = cad.NewSketchFromCurve(curve)
                    cad.AddUndoably(sketch)
                    cad.Select(sketch)
                    self.failure = 'GetToolForCurve couldnt find tool of diameter ' + str(r*2) + ' or less with cut depth of ' + str(cut_depth) + '\nsee sketch ' + str(sketch.GetID())
                    return 0, None

        return self.slot_cutters.AddIfNotAdded(cutter_index)

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
    
    def GetMaxPocketCutterRadius(self, area):
        max_diam = None
        for curve in area.GetCurves():
            outer = curve.IsClockwise()
            diam = curve.GetMaxCutterRadius(outer, self.precision)
            if (diam != None) and (max_diam == None or diam < max_diam):
                max_diam = diam
        if max_diam != None:
            max_diam -= 0.11 # make sure there is room to offset the area inwards without it disappearing, also with room for a roughing pass
        return max_diam
    
    def PocketCanBeDoneWithProfileOp(self, a, cutter_index):
        # if the area is a simple single curve and disappears when offset inwards by the cutter diameter, then it's fine to just profile the area
        if a.NumCurves() == 1:
            a_copy = geom.Area(a)
            a_copy.Offset(self.slot_cutters[cutter_index].diam * 0.95)
            if a_copy.NumCurves() == 0:
                return True
        
        return False
    
    def ChoosePreferredCutter(self, cut_depth):
        # return the cutter_index of the biggest tool allowed, with the smallest cutting length, where there are multiple same diameter cutters
        cutter_found = None
        index = self.slot_cutters.BiggestShortest(cut_depth = cut_depth, max_cutter_diameter = None if self.big_rigid_part else BIG_CUTTER_DIAMETER)
        
        if index != None:
            return index
        
        self.failure = 'no cutter long enough for cut depth - ' + str(cut_depth)
        
    def GetPatchCutters(self, cut_depth):
        return self.slot_cutters.GetPatchCutters(cut_depth, max_cutter_diameter = None if self.big_rigid_part else BIG_CUTTER_DIAMETER)

def FindTagPoint(curve, line):
    # line defined by two lists of two coordinates
    c2 = geom.Curve()
    c2.Append(geom.Point(line[0][0], line[0][1]))
    c2.Append(geom.Point(line[1][0], line[1][1]))
    pts = curve.Intersections(c2)
    if len(pts) == 0:
        return None
    return pts[0]