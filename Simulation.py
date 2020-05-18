from CamObject import CamObject
import geom
import cad
from HeeksConfig import HeeksConfig
import math
import wx
from Object import PyProperty
import sim
import threading
import time
from consts import *

type = 0

import math
import re
import copy

simulation = None  # global simulation object when one exists

def OnTimer(event):
    if simulation.running:
        new_pos = simulation.current_pos + simulation.mm_per_sec/30
        simulation.cut_to_position(new_pos)
        wx.GetApp().frame.graphics_canvas.Refresh()

class Line:
    def __init__(self, p0, p1, rapid, tool_number):
        self.p0 = p0
        self.p1 = p1
        self.rapid = rapid
        self.tool_number = tool_number
        
    def Length(self):
        return self.p0.Dist(self.p1)
        
p_for_cut = None
        
class SimCyl(sim.CylinderVolume):
    def __init__(self, radius, z, color):
        sim.CylinderVolume.__init__(self)
        self.radius = radius
        self.z_bottom = z
        self.z_top = z + wx.GetApp().program.simulation.leaf_scale
        self.color = color

    def cut(self, rapid):
        if rapid == True: self.setColor(0.6, 0.0, 0.0)
        else: self.setColor(self.color[0], self.color[1], self.color[2])
        self.setCenter(sim.GLVertex(p_for_cut.x, p_for_cut.y, p_for_cut.z + self.z_bottom))
        simulation.tree.diff(self)
        
    def draw(self, rapid):
        self.setCenter(sim.GLVertex(p_for_cut.x, p_for_cut.y, p_for_cut.z + self.z_bottom))
        self.Render()
        # to do
#        color = self.color
#        if rapid: color = 0x600000
        
#        for i in range(0, 21):
#            a = 0.31415926 * i
#            x = float(x_for_cut) + self.radius * math.cos(a)
#            y = float(y_for_cut) + self.radius * math.sin(a)
#            z_bottom = float(z_for_cut) + self.z_bottom
#            z_top = float(z_for_cut) + self.z_top

#            voxelcut.drawline3d(x, y, z_bottom, x, y, z_top, color)
            
#            if i > 0:
#                voxelcut.drawline3d(prevx, prevy, prevz_bottom, x, y, z_bottom, color)
#                voxelcut.drawline3d(prevx, prevy, prevz_top, x, y, z_top, color)
#            prevx = x
#            prevy = y
#            prevz_bottom = z_bottom
#            prevz_top = z_top
        
class Tool:
    def __init__(self, span_list):
        # this is made from a list of (geom.Span, colour_ref)
        # the spans should be defined with the y-axis representing the centre of the tool, with the tip of the tool being defined at y = 0
        self.span_list = span_list
        self.cylinders = []
        self.cylinders_calculated = False
        self.calculate_cylinders()
        
    def calculate_span_cylinders(self, span, color):
        sz = span.p.y
        ez = span.v.p.y
        
        z = sz
        while z < ez:
            # make a line at this z
            intersection_line = geom.Span(geom.Point(0, z), geom.Vertex(0, geom.Point(300, z), geom.Point(0, 0)), False)
            intersections = span.Intersect(intersection_line)
            if len(intersections):
                radius = intersections[0].x
                self.cylinders.append(SimCyl(radius, z, color))
            z += wx.GetApp().program.simulation.leaf_scale
            
    def refine_cylinders(self):
        cur_cylinder = None
        old_cylinders = self.cylinders
        
        self.cylinders = []
        for cylinder in old_cylinders:
            if cur_cylinder == None:
                cur_cylinder = cylinder
            else:
                if (cur_cylinder.radius == cylinder.radius) and (cur_cylinder.color == cylinder.color):
                    cur_cylinder.z_top = cylinder.z_top
                    cur_cylinder.setLength(cur_cylinder.z_top - cur_cylinder.z_bottom)
                else:
                    self.cylinders.append(cur_cylinder)
                    cur_cylinder = cylinder
        if cur_cylinder != None:
            self.cylinders.append(cur_cylinder)       
        
    def calculate_cylinders(self):
        self.cylinders = []
        for span_and_color in self.span_list:
            self.calculate_span_cylinders(span_and_color[0], span_and_color[1])
            
        self.refine_cylinders()
                                  
        self.cylinders_calculated = True
            
    def cut(self, p, rapid):
        global p_for_cut
        p_for_cut = p
        
        for cylinder in self.cylinders:
            cylinder.cut(rapid)
            
    def draw(self, p, rapid):
        global p_for_cut
        p_for_cut = p
        
        for cylinder in self.cylinders:
            cylinder.draw(rapid)

class RemovalThread(threading.Thread):
    def __init__(self, simulation):
        threading.Thread.__init__(self)
        self.simulation = simulation

    def run(self):
        for i in range(0,2000):
            r = 20.0 + 0.01*i
            z = -1.0 - 0.005 * i
            a = 0.017453 * i
            x = r * math.cos(a)
            y = r * math.sin(a)
            self.removeCylinder(sim.GLVertex(x,y,z))
        if self.simulation.iso_algo:
            self.simulation.iso_algo.updateGL()

        if self.simulation.iso_algo:
            self.simulation.threadLock.acquire()
            self.simulation.gldata.swap()
            self.simulation.threadLock.release()
        
        wx.GetApp().frame.graphics_canvas.Refresh()

    def removeCylinder(self, center):
        cyl = sim.CylinderVolume()
        cyl.setRadius(3)
        cyl.setLength(50)
        cyl.setCenter(center)
        self.simulation.tree.diff(cyl)

    
class Simulation(CamObject):
    def __init__(self):
        self.length = 0.0
        self.lines = []
        self.current_pos = 0.0
        self.from_position = geom.Point3D(0, 0, 0)
        self.current_point = self.from_position
        self.current_line_index = 0
        self.tools = {} # dictionary, tool id to Tool object
        self.rapid_flag = True
        self.mm_per_sec = 50.0
        self.running = False
        self.in_cut_to_position = False
        self.leaf_scale = None
        
        self.x = 0
        self.y = 0
        self.z = 50
        
        self.t = None
        
        self.gldata = None
        
        self.threadLock = threading.Lock()
        
        #self.removal_thread = RemovalThread(self)
        #self.removal_thread.start()
        
        CamObject.__init__(self)
        
    def add_line(self, p0, p1):
        self.lines.append(Line(p0, p1, self.rapid_flag, self.t))
        
    def rewind(self):
        self.current_point = geom.Point3D(0, 0, 0)
        if len(self.lines)>0:
            self.current_point = self.lines[0].p0
        self.current_pos = 0.0
        self.current_line_index = 0
        self.running = False
        
    def draw_tool(self):
        index = self.current_line_index
        if index < 0: index = 0
        if index >= len(self.lines):
            return
        
        tool_number = self.lines[index].tool_number
        rapid = self.lines[index].rapid

        if tool_number in self.tools:
            self.tools[tool_number].draw(self.current_point, rapid)
        
    def cut_point(self, p):
        index = self.current_line_index
        if index < 0: index = 0
        tool_number = self.lines[index].tool_number
        rapid = self.lines[index].rapid
        
        if tool_number in self.tools:
            self.tools[tool_number].cut(p, rapid)
         
    def cut_line(self, line):
        length = line.Length()
        num_segments = int(1 + length / self.leaf_scale * 0.2)
        step = length/num_segments
        dv = (line.p1 - line.p0) * (1.0/num_segments)
        for i in range (0, num_segments + 1):
            p = line.p0 + (dv * i)
            self.cut_point(p)
            
    def cut_to_position(self, pos):
        if self.current_line_index >= len(self.lines):
            return
        
        if self.cut_to_position == True:
            wx.MessageBox("in cut_to_position again!")
        
        self.in_cut_to_position = True
        start_pos = self.current_pos
        while self.current_line_index < len(self.lines):
            line = copy.copy(self.lines[self.current_line_index])
            line.p0 = self.current_point
            line_length = line.Length()
            if line_length > 0:
                end_pos = self.current_pos + line_length
                if pos < end_pos:
                    fraction = (pos - self.current_pos)/(end_pos - self.current_pos)
                    line.p1 = line.p0 + ((line.p1 - line.p0) * fraction)
                    self.cut_line(line)
                    self.current_pos = pos
                    self.current_point = line.p1
                    break
                self.cut_line(line)
                self.current_pos = end_pos
            self.current_point = line.p1
            self.current_line_index = self.current_line_index + 1
        
        if self.iso_algo:
            self.iso_algo.updateGL()

            self.threadLock.acquire()
            self.gldata.swap()
            self.threadLock.release()
        
        wx.GetApp().frame.graphics_canvas.Refresh()
            
        self.in_cut_to_position = False
        
    def begin_ncblock(self):
        pass

    def end_ncblock(self):
        pass

    def add_text(self, s, col, cdata):
        pass

    def set_mode(self, units):
        pass
        
    def metric(self):
        pass
        
    def imperial(self):
        pass

    def begin_path(self, col):
        pass

    def end_path(self):
        pass
        
    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.rapid_flag = True
        if x == None: x = self.x
        if y == None: y = self.y
        if z == None: z = self.z
        self.add_line(geom.Point3D(self.x, self.y, self.z), geom.Point3D(x, y, z))
        self.x = x
        self.y = y
        self.z = z
        
    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.rapid_flag = False
        if x == None: x = self.x
        if y == None: y = self.y
        if z == None: z = self.z
        self.add_line(geom.Point3D(self.x, self.y, self.z), geom.Point3D(x, y, z))
        self.x = x
        self.y = y
        self.z = z
        
    def arc(self, dir, x, y, z, i, j, k, r):
        self.rapid_flag = False
        if x == None: x = self.x
        if y == None: y = self.y
        if z == None: z = self.z
        geom.set_units(0.05)
        curve = geom.Curve()
        curve.Append(geom.Point(self.x, self.y))
        curve.Append(geom.Vertex(dir, geom.Point(x, y), geom.Point(i, j)))
        curve.UnFitArcs()
        for span in curve.GetSpans():
            self.add_line(geom.Point3D(span.p.x, span.p.y, z), geom.Point3D(span.v.p.x, span.v.p.y, z))
        self.x = x
        self.y = y
        self.z = z

    def arc_cw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.arc(-1, x, y, z, i, j, k, r)

    def arc_ccw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.arc(1, x, y, z, i, j, k, r)
        
    def tool_change(self, id):
        self.t = id
            
    def current_tool(self):
        return self.t
            
    def spindle(self, s, clockwise):
        pass
    
    def feedrate(self, f):
        pass

    def icon(self):
        return "sim"
    
    def TypeName(self):
        return "sim"
    
    def GetTitle(self):
        return 'Simulation'
    
    def GetType(self):
        return type
    
    def CanBeDeleted(self):
        return False
            
    def OneOfAKind(self):
        return True
    
    def OnGlCommands(self, select, marked, no_color):
        if self.gldata != None:
            self.threadLock.acquire()
            self.gldata.draw()
            self.threadLock.release()
        self.draw_tool()
        
    def KillGLLists(self):
        # to do
        pass
        #self.sim.KillGLLists()
        
    def MakeACopy(self):
        object = Simulation()
        object.CopyFrom(self)
        return object
    
    def CopyFrom(self, object):
        pass
        #self.sim.CopyFrom(object)
    
    def CallsObjListReadXml(self):
        return False

    def ReadXml(self):
        # to do
        pass
        #self.sim.ReadXml()
        
    def WriteXml(self):
        # to do
        pass
        #self.sim.WriteXml()
        
    def SetClickMarkPoint(self, marked_object, ray_start, ray_direction):
        # to do
        pass
        #self.sim.SetClickMarkPoint(marked_object, ray_start, ray_direction)

    def Reset(self):
        global simulation
        simulation = self
        
        # get the box of all the solids
        box = wx.GetApp().program.stocks.GetBox()
        cp = box.Center()
        scale = box.Width()
        if box.Height() > scale: scale = box.Height()
        if box.Depth() > scale: scale = box.Depth()
        self.center_point = sim.GLVertex(cp.x, cp.y, cp.z)
        #self.center_point = sim.GLVertex(0.0, 0.0, 0.0)
        
        self.gldata = sim.GLData()
        self.tree = sim.Octree(scale,11, self.center_point, self.gldata)
        self.tree.init(4)
        self.leaf_scale = self.tree.get_leaf_scale()
        
        self.iso_algo = sim.MarchingCubes(self.gldata, self.tree)
        #self.iso_algo = None
        
        # add each stock
        stocks = wx.GetApp().program.stocks.GetChildren()
        for stock in stocks:
            stock_box = stock.GetBox()
            stock = sim.RectVolume(stock_box.MinX(), stock_box.MinY(), stock_box.MinZ(), stock_box.MaxX(), stock_box.MaxY(), stock_box.MaxZ())
            stock.calcBB()
            stock.setColor(0,1,1)
            self.tree.sum(stock)
            
        tools = wx.GetApp().program.tools.GetChildren()
        for tool in tools:
            self.tools[tool.tool_number] = GetSimToolDefinition(tool)
            
        machine_module = __import__('nc.' + wx.GetApp().program.machine.reader, fromlist = ['dummy'])
        parser = machine_module.Parser(self)
        parser.Parse(wx.GetApp().program.GetOutputFileName())
        self.rewind()

        if self.iso_algo:
            self.iso_algo.updateGL()

        self.threadLock.acquire()
        self.gldata.swap()
        self.threadLock.release()
        
        
        
        self.timer = wx.Timer(wx.GetApp().frame, wx.ID_ANY)
        self.timer.Start(33)
        wx.GetApp().frame.Bind(wx.EVT_TIMER, OnTimer)

        
#		WriteCoords(ofs);
#		WriteSolids(ofs);
#		WriteTools(ofs);

#		ofs<<_T("parser = nc.") << theApp.m_program->m_machine.reader.c_str() << _T(".Parser(toolpath)\n");

#		ofs<<_T("parser.Parse('")<<GetOutputFileNameForPython(theApp.m_program->GetOutputFileName().c_str())<<_T("')\n");
#		ofs<<_T("toolpath.rewind()\n");
        
def GetSimToolDefinition(tool):
    GRAY = (0.5, 0.5, 0.5)
    RED = (0.7, 0.0, 0.0)
    BLUE = (0.0, 0.0, 0.3)
        
    span_list = []
    height_above_cutting_edge = 30.0
    r = tool.diameter/2.0
    h = tool.cutting_edge_height
    cr = tool.corner_radius
    
    if tool.type == TOOL_TYPE_DRILL or tool.type == TOOL_TYPE_CENTREDRILL:
        max_cutting_height = 0.0
        radius_at_cutting_height = r
        edge_angle = tool.cutting_edge_angle
        flat_radius = tool.flat_radius
        if (edge_angle < 0.01) or (r < flat_radius):
            span_list.append([geom.Span(geom.Point(flat_radius, 0), geom.Vertex(geom.Point(flat_radius, h)), False), GRAY])
            span_list.append([geom.Span(geom.Point(flat_radius, h), geom.Vertex(geom.Point(flat_radius, h + height_above_cutting_edge)), False), RED])
        else:
            rad_diff = r - flat_radius
            max_cutting_height = rad_diff / math.tan(edge_angle * 0.0174532925199432)
            radius_at_cutting_height = (h/max_cutting_height) * rad_diff + flat_radius
            if max_cutting_height > h:
                span_list.append([geom.Span(geom.Point(flat_radius, 0), geom.Vertex(geom.Point(radius_at_cutting_height, h)), False), GRAY])
                span_list.append([geom.Span(geom.Point(radius_at_cutting_height, h), geom.Vertex(geom.Point(r, max_cutting_height)), False), GRAY])
                span_list.append([geom.Span(geom.Point(r, max_cutting_height), geom.Vertex(geom.Point(r, max_cutting_height + height_above_cutting_edge)), False), RED])
            else:
                span_list.append([geom.Span(geom.Point(flat_radius, 0), geom.Vertex(geom.Point(r, max_cutting_height)), False), GRAY])
                span_list.append([geom.Span(geom.Point(r, max_cutting_height), geom.Vertex(geom.Point(r, h)), False), GRAY])
                span_list.append([geom.Span(geom.Point(r, h), geom.Vertex(geom.Point(r, h + height_above_cutting_edge)), False), RED])
    elif tool.type == TOOL_TYPE_ENDMILL or tool.type == TOOL_TYPE_SLOTCUTTER:
        span_list.append([geom.Span(geom.Point(r, 0), geom.Vertex(geom.Point(r, h)), False), GRAY])
        span_list.append([geom.Span(geom.Point(r, h), geom.Vertex(geom.Point(r, h + height_above_cutting_edge)), False), RED])
    elif tool.type == TOOL_TYPE_BALLENDMILL:
        if h > r:
            span_list.append([geom.Span(geom.Point(0, 0), geom.Vertex(1, geom.Point(r, r), geom.Point(0, r)), False), GRAY])
            span_list.append([geom.Span(geom.Point(r, r), geom.Vertex(geom.Point(r, h)), False), GRAY])
            span_list.append([geom.Span(geom.Point(r, h), geom.Vertex(geom.Point(r, h + height_above_cutting_edge)), False), RED])
        else:
            x = math.sqrt(r*r - (r-h) * (r-h))
            span_list.append([geom.Span(geom.Point(0, 0), geom.Vertex(1, geom.Point(x, h), geom.Point(0, r)), False), GRAY])
            span_list.append([geom.Span(geom.Point(x, h), geom.Vertex(1, geom.Point(r, r), geom.Point(0, r)), False), RED])
            span_list.append([geom.Span(geom.Point(r, r), geom.Vertex(geom.Point(r, r + height_above_cutting_edge)), False), RED])
    else:
        if cr > r: cr = r
        if cr > 0.0001:
            if h >= cr:
                span_list.append([geom.Span(geom.Point(r-cr, 0), geom.Vertex(1, geom.Point(r, cr), geom.Point(r-cr, cr)), False), GRAY])
                span_list.append([geom.Span(geom.Point(r, r), geom.Vertex(geom.Point(r, h)), False), GRAY])
                span_list.append([geom.Span(geom.Point(r, h), geom.Vertex(geom.Point(r, h + height_above_cutting_edge)), False), RED])
            else:
                x = (r - cr) + math.sqrt(cr*cr - (cr-h) * (cr-h))
                span_list.append([geom.Span(geom.Point(r-cr, 0), geom.Vertex(1, geom.Point(x, h), geom.Point(0, cr)), False), GRAY])
                span_list.append([geom.Span(geom.Point(x, h), geom.Vertex(1, geom.Point(r, cr), geom.Point(0, cr)), False), RED])
                span_list.append([geom.Span(geom.Point(r, cr), geom.Vertex(geom.Point(r, cr + height_above_cutting_edge)), False), RED])
        else:
            span_list.append([geom.Span(geom.Point(r, 0), geom.Vertex(geom.Point(r, h)), False), GRAY])
            span_list.append([geom.Span(geom.Point(r, h), geom.Vertex(geom.Point(r, h + height_above_cutting_edge)), False), RED])
    
    return Tool(span_list)
