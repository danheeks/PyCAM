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

type = 0

import math
import re
import copy

class Line:
    def __init__(self, p0, p1, rapid, tool_number):
        self.p0 = p0
        self.p1 = p1
        self.rapid = rapid
        self.tool_number = tool_number
        
    def Length(self):
        return self.p0.dist(self.p1)
        
x_for_cut = 0
y_for_cut = 0
z_for_cut = 0
        
class VoxelCyl:
    def __init__(self, radius, z, color):
        self.radius = int(radius)
        self.z_bottom = int(z)
        self.z_top = int(z) + 1
        self.color = color

    def cut(self, rapid):
        if rapid == True: voxelcut.set_current_color(0x600000)
        else: voxelcut.set_current_color(self.color)
        voxelcut.remove_cylinder(int(x_for_cut), int(y_for_cut), z_for_cut + int(self.z_bottom), int(x_for_cut), int(y_for_cut), z_for_cut + int(self.z_top), int(self.radius))
        
    def draw(self, rapid):

        color = self.color
        if rapid: color = 0x600000
        
        for i in range(0, 21):
            a = 0.31415926 * i
            x = float(x_for_cut) + self.radius * math.cos(a)
            y = float(y_for_cut) + self.radius * math.sin(a)
            z_bottom = float(z_for_cut) + self.z_bottom
            z_top = float(z_for_cut) + self.z_top

            voxelcut.drawline3d(x, y, z_bottom, x, y, z_top, color)
            
            if i > 0:
                voxelcut.drawline3d(prevx, prevy, prevz_bottom, x, y, z_bottom, color)
                voxelcut.drawline3d(prevx, prevy, prevz_top, x, y, z_top, color)
            prevx = x
            prevy = y
            prevz_bottom = z_bottom
            prevz_top = z_top
        
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
                radius = intersections[0].x * toolpath.coords.voxels_per_mm
                self.cylinders.append(VoxelCyl(radius, z * toolpath.coords.voxels_per_mm, color))
            z += 1/toolpath.coords.voxels_per_mm
            
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
            
    def cut(self, x, y, z, rapid):
        global x_for_cut
        global y_for_cut
        global z_for_cut
        x_for_cut = x
        y_for_cut = y
        z_for_cut = z
        
        for cylinder in self.cylinders:
            cylinder.cut(rapid)
            
    def draw(self, x, y, z, rapid):
        global x_for_cut
        global y_for_cut
        global z_for_cut
        x_for_cut = x
        y_for_cut = y
        z_for_cut = z

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
        self.simulation.iso_algo.updateGL()

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
        
        self.x = 0
        self.y = 0
        self.z = 50
        
        self.t = None
        
        self.gldata = None

#        self.gldata = sim.GLData()
#        self.tree = sim.Octree(70.0, 9, centre_point, self.gldata)
#        self.iso_algo = sim.MarchingCubes(self.gldata, self.tree)
#        stock0 = sim.RectVolume()
#        stock0.corner = sim.GLVertex(-50, -30, -10)
#        stock0.v1 = sim.GLVertex(100, 0, 0)
#        stock0.v2 = sim.GLVertex(0, 60, 0)
#        stock0.v3 = sim.GLVertex(0, 0, 10)
#        stock0.calcBB()
#        stock0.setColor(0,1,1)
#        self.tree.sum(stock0)
        
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
        voxelcut.drawclear()
        
        index = self.current_line_index
        if index < 0: index = 0
        if index >= len(self.lines):
            return
        
        tool_number = self.lines[index].tool_number
        rapid = self.lines[index].rapid
        
        if tool_number in self.tools:
            x, y, z = self.coords.mm_to_voxels(self.current_point.x, self.current_point.y, self.current_point.z)
            self.tools[tool_number].draw(x, y, z, rapid)
        
    def cut_point(self, p):
        x, y, z = self.coords.mm_to_voxels(p.x, p.y, p.z)
        index = self.current_line_index
        if index < 0: index = 0
        tool_number = self.lines[index].tool_number
        rapid = self.lines[index].rapid
        
        if tool_number in self.tools:
            self.tools[tool_number].cut(x, y, z, rapid)
         
    def cut_line(self, line):
        length = line.Length()
        num_segments = int(1 + length * self.coords.voxels_per_mm * 0.2)
        step = length/num_segments
        dv = (line.p1 - line.p0) * (1.0/num_segments)
        for i in range (0, num_segments + 1):
            p = line.p0 + (dv * i)
            self.cut_point(p)
            
    def cut_to_position(self, pos):
        if self.current_line_index >= len(self.lines):
            return
        
        if self.cut_to_position == True:
            import wx
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
        self.add_line(Point(self.x, self.y, self.z), Point(x, y, z))
        self.x = x
        self.y = y
        self.z = z
        
    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.rapid_flag = False
        if x == None: x = self.x
        if y == None: y = self.y
        if z == None: z = self.z
        self.add_line(Point(self.x, self.y, self.z), Point(x, y, z))
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
        curve.append(geom.Point(self.x, self.y))
        curve.append(geom.Vertex(dir, geom.Point(x, y), geom.Point(i, j)))
        curve.UnFitArcs()
        for span in curve.GetSpans():
            self.add_line(Point(span.p.x, span.p.y, z), Point(span.v.p.x, span.v.p.y, z))
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
        # get the box of all the solids
        #box = wx.GetApp().program.stocks.GetBox()
        box = geom.Box3D()
        cad.GetApp().GetBox(box) # use world box for now
        cp = box.Center()
        scale = box.Width()
        if box.Height() > scale: scale = box.Height()
        if box.Depth() > scale: scale = box.Depth()
        #self.center_point = sim.GLVertex(cp.x, cp.y, cp.z)
        self.center_point = sim.GLVertex(0.0, 0.0, 0.0)
        
        self.gldata = sim.GLData()
        self.tree = sim.Octree(3.0, 9, self.center_point, self.gldata) # to do, use cad's box
        self.tree.init(4)
        
        self.iso_algo = sim.MarchingCubes(self.gldata, self.tree)
        
        # to do, add each stock
        
        # for now add a stock the size of the world box
        maxz = box.MaxZ()
        if maxz < box.MinZ() + 1.0: maxz = box.MinZ() + 1.0
        #stock0 = sim.RectVolume(box.MinX(), box.MinY(), box.MinZ() + 0.2, box.MaxX(), box.MaxY(), maxz)
        #stock0 = sim.RectVolume(2, 2, 0, 10, 10, 1) can't see it
        self.stock0 = sim.RectVolume(0,0,0,1,1,1)
        self.stock0.calcBB()
        self.stock0.setColor(0,1,1)
        self.tree.sum(self.stock0)

        self.rect = sim.RectVolume(-1,-1,-0.9,2,2,0.1)
        self.rect.calcBB()
        self.rect.setColor(0,1,1)
        self.tree.sum(self.rect)

        self.rect = sim.RectVolume(-1,-1,-2,0.1,2,2)
        self.rect.calcBB()
        self.rect.setColor(0,1,1)
        self.tree.sum(self.rect)

        self.rect = sim.RectVolume(0.9,-1,-2,2,2,2)
        self.rect.calcBB()
        self.rect.setColor(0,1,1)
        self.tree.sum(self.rect)

        self.rect = sim.RectVolume(-1,-1,-2,2,0.1,2)
        self.rect.calcBB()
        self.rect.setColor(0,1,1)
        self.tree.sum(self.rect)
        
        self.rect = sim.RectVolume(-1,0.9,-2,2,2,2)
        self.rect.calcBB()
        self.rect.setColor(0,1,1)
        self.tree.sum(self.rect)

        cyl = sim.CylinderVolume()
        cyl.setRadius(0.3)
        cyl.setLength(50)
        cyl.setCenter(sim.GLVertex(1,1,-2))
        self.tree.diff(cyl)
        cyl.setCenter(sim.GLVertex(0.9,1,-2))
        self.tree.diff(cyl)
        cyl.setCenter(sim.GLVertex(0.8,1,-2))
        self.tree.diff(cyl)

        self.iso_algo.updateGL()

        self.threadLock.acquire()
        self.gldata.swap()
        self.threadLock.release()
        
        wx.GetApp().frame.graphics_canvas.Refresh()
        
#		WriteCoords(ofs);
#		WriteSolids(ofs);
#		WriteTools(ofs);

#		ofs<<_T("parser = nc.") << theApp.m_program->m_machine.reader.c_str() << _T(".Parser(toolpath)\n");

#		ofs<<_T("parser.Parse('")<<GetOutputFileNameForPython(theApp.m_program->GetOutputFileName().c_str())<<_T("')\n");
#		ofs<<_T("toolpath.rewind()\n");
        
        