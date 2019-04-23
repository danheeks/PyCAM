from CamObject import CamObject
import geom
import cad
from HeeksConfig import HeeksConfig
import math
import wx

type = 0
s_arc_interpolation_count = 20

ColorDefaultType = 0
ColorBlockType = 1
ColorMiscType = 2
ColorProgramType = 3
ColorToolType = 4
ColorCommentType = 5
ColorVariableType = 6
ColorPrepType = 7
ColorAxisType = 8
ColorRapidType = 9
ColorFeedType = 10
MaxColorTypes = 11

PathObjectTypeLine = 0
PathObjectTypeArc = 1

PathObjectPrevPoint = geom.Point3D(0,0,0)

NcCode_pos = 0
NcCode_prev_po = None
colors_s_i = {}
colors_i_s = {}
colors = []
            
NcCodeBlock_multiplier = 1.0
NcCodeBlock_type = 0

def ClearColors():
    colors_s_i = {}
    colors_i_s = {}
    colors = []

def AddColor(name, col):
    i = ColorCount()
    colors_s_i[name] = i
    colors_i_s[i] = name
    colors.append(col)

def GetColor(name, default = ColorDefaultType):
    if name == None: return default
    if name in colors_s_i:
        return colors_s_i[name]
    return default

def GetColorName(i, default = "default"):
    if i in colors_i_s:
        return colors_i_s[i]
    return default

def ColorCount():
    return len(colors)
    
def Color(i):
    return colors[i]
    
def ReadColorsFromConfig():
    config = HeeksConfig()
    ClearColors()
    AddColor('default', cad.Color(int(config.Read('ColorDefaultType', str(cad.Color(0,0,0).ref())))))
    AddColor('blocknum', cad.Color(int(config.Read('ColorBlockType', str(cad.Color(0,0,222).ref())))))
    AddColor('misc', cad.Color(int(config.Read('ColorMiscType', str(cad.Color(0,200,0).ref())))))
    AddColor('program', cad.Color(int(config.Read('ColorProgramType', str(cad.Color(255,128,0).ref())))))
    AddColor('tool', cad.Color(int(config.Read('ColorToolType', str(cad.Color(200,200,0).ref())))))
    AddColor('comment', cad.Color(int(config.Read('ColorCommentType', str(cad.Color(0,200,200).ref())))))
    AddColor('variable', cad.Color(int(config.Read('ColorVariableType', str(cad.Color(164,88,188).ref())))))
    AddColor('prep', cad.Color(int(config.Read('ColorPrepType', str(cad.Color(255,0,175).ref())))))
    AddColor('axis', cad.Color(int(config.Read('ColorAxisType', str(cad.Color(128,0,255).ref())))))
    AddColor('rapid', cad.Color(int(config.Read('ColorRapidType', str(cad.Color(222,0,0).ref())))))
    AddColor('feed', cad.Color(int(config.Read('ColorFeedType', str(cad.Color(0,179,0).ref())))))

class ColouredText:
    def __init__(self):
        self.str = ''
        self.color_type = ColorDefaultType

    def WriteXML(self):
        pass # to do
    
    def ReadXml(self):
        self.color_type = GetColor(cad.GetXmlValue('col'), ColorRapidType)
        # get the text
        self.str = cad.GetXmlText()
        
    
class PathObject:
    def __init__(self):
        self.point = geom.Point3D(0,0,0)
        self.tool_number = 0
        
    def GetBox(self, box):
        box.InsertPoint(self.point.x, self.point.y, self.point.z)
        
    def WriteBaseXML(self):
        pass # to do
    
    def CopyFrom(self, object):
        self.point = object.point
        self.tool_number = object.tool_number
    
    def ReadXml(self):
        global PathObjectPrevPoint
        global NcCodeBlock_multiplier

        self.point.x = cad.GetXmlFloat('x', PathObjectPrevPoint.x) * NcCodeBlock_multiplier
        self.point.y = cad.GetXmlFloat('y', PathObjectPrevPoint.y) * NcCodeBlock_multiplier
        self.point.z = cad.GetXmlFloat('z', PathObjectPrevPoint.z) * NcCodeBlock_multiplier
        self.tool_number = cad.GetXmlInt('tool_number')
        
        PathObjectPrevPoint = self.point
        
class PathLine(PathObject):
    def __init__(self):
        PathObject.__init__(self)
        
    def GetType():
        return PathObjectTypeLine

    def WriteXML(self):
        pass # to do
    
    def MakeACopy(self):
        object = PathLine()
        object.CopyFrom(self)
        return object
    
    def glVertices(self):
        global NcCode_prev_po
        if NcCode_prev_po: cad.GlVertex(NcCode_prev_po.point)
        cad.GlVertex(self.point)
        
class PathArc(PathObject):
    def __init__(self):
        PathObject.__init__(self)
        self.centre = geom.Point3D(0,0,0)
        self.radius = 0.0
        self.dir = 1
        
    def GetType():
        return PathObjectTypeArc
        
    def GetBox(self, box):
        PathObject.GetBox(self, box)
        
        global NcCode_prev_po
        
        if self.IsIncluded(geom.Point3D(0,1,0)):
            box.InsertPoint(NcCode_prev_po.point.x + self.centre.x, NcCode_prev_po.point.y + self.centre.y + self.radius, 0)
        if self.IsIncluded(geom.Point3D(0,-1,0)):
            box.InsertPoint(NcCode_prev_po.point.x + self.centre.x, NcCode_prev_po.point.y + self.centre.y - self.radius, 0)
        if self.IsIncluded(geom.Point3D(1,0,0)):
            box.InsertPoint(NcCode_prev_po.point.x + self.centre.x + self.radius, NcCode_prev_po.point.y + self.centre.y, 0)
        if self.IsIncluded(geom.Point3D(-1,0,0)):
            box.InsertPoint(NcCode_prev_po.point.x + self.centre.x - self.radius, NcCode_prev_po.point.y + self.centre.y, 0)
            
    def IsIncluded(self, point):
        global NcCode_prev_po
        sx = -self.centre.x
        sy = -self.centre.y
        ex = -self.centre.x + self.point.x - NcCode_prev_po.point.x
        ey = -self.centre.y + self.point.y - NcCode_prev_po.point.y
        rs = math.sqrt(sx * sx + sy * sy)
        self.radius = rs  # really! to do, remove this once it's working
        
        start_angle = math.atan2(sy, sx)
        end_angle = math.atan2(ey, ex)
        
        if self.dir == 1:
            if end_angle < start_angle: end_angle += 6.283185307179
        else:
            if start_angle < end_angle: start_angle += 6.283185307179
            
        if start_angle == end_angle:
            return True # It's a full circle.
        
        the_angle = math.atan2(point.y, point.x)
        the_angle2 = the_angle + 2 * math.pi
        
        return ((the_angle >= start_angle) and (the_angle <= end_angle)) or ((the_angle2 >= start_angle) and (the_angle2 <= end_angle))
        
    def WriteXML(self):
        pass # to do
    
    def ReadXml(self):
        self.radius = cad.GetXmlValue('r')
        if self.radius != '':
            self.radius = float(self.radius)
            PathObject.ReadXml(self)
            self.SetFromRadius()
        else:
            self.centre.x = cad.GetXmlFloat('i') * NcCodeBlock_multiplier
            self.centre.y = cad.GetXmlFloat('j') * NcCodeBlock_multiplier
            self.centre.z = cad.GetXmlFloat('k') * NcCodeBlock_multiplier
            self.dir = cad.GetXmlInt('d')
            PathObject.ReadXml(self)
    
    def CopyFrom(self, object):
        self.centre = object.centre
        self.radius = object.radius
        self.dir = object.dir
        PathObject.CopyFrom(self, object)
    
    def MakeACopy(self):
        object = PathArc()
        object.CopyFrom(self)
        return object
    
    def glVertices(self):
        global NcCode_prev_po

        if NcCode_prev_po == None:
            return
        
        vertices = self.Interpolate( s_arc_interpolation_count )
        cad.GlVertex(NcCode_prev_po.point)
        
        for vertex in vertices:
            cad.GlVertex(vertex)
            
    def Interpolate(self, number_of_points):
        points = []
        
        global NcCode_prev_po

        sx = -self.centre.x
        sy = -self.centre.y
        ex = -self.centre.x + self.point.x - NcCode_prev_po.point.x
        ey = -self.centre.y + self.point.y - NcCode_prev_po.point.y
        rs = math.sqrt(sx * sx + sy * sy)
        re = math.sqrt(ex * ex + ey * ey)
        self.radius = rs  # really! to do, remove this once it's working
        
        start_angle = math.atan2(sy, sx)
        end_angle = math.atan2(ey, ex)
        
        if self.dir == 1:
            if end_angle < start_angle: end_angle += 6.283185307179
        else:
            if start_angle < end_angle: start_angle += 6.283185307179
            
        angle_step = 0
            
        if start_angle == end_angle:
            # It's a full circle.
            angle_step = ( 2 * math.pi ) / number_of_points
            if self.dir == -1:
                angle_step = -angle_step # fix preview of full cw arcs
        else:
            # It's an arc
            angle_step = (end_angle - start_angle) / number_of_points
            
        points.append( geom.Point3D(NcCode_prev_po.point.x, NcCode_prev_po.point.y, NcCode_prev_po.point.z) )
        
        for i in range(0, number_of_points):
            angle = start_angle + angle_step * ( i + 1 )
            r = rs + ((re - rs) * (i + 1)) /number_of_points
            x = NcCode_prev_po.point.x + self.centre.x + r * math.cos(angle)
            y = NcCode_prev_po.point.y + self.centre.y + r * math.sin(angle)
            z = NcCode_prev_po.point.z + ((self.point.z - NcCode_prev_po.point.z) * (i+1))/number_of_points
            
            points.append( geom.Point3D( x, y, z ) )
            
        return points
    
    def MakeCircleCurveAtPoint(self, centre, radius):
        p0 = centre + geom.Point(radius, 0)
        p1 = centre + geom.Point(-radius, 0)
        curve = geom.Curve()
        curve.Append(p0)
        curve.Append(geom.Vertex(1, p1, centre))
        curve.Append(geom.Vertex(1, p0, centre))
        return curve
    
    def SetFromRadius(self):
        ps = PathObjectPrevPoint
        pe = self.point
        r = math.fabs(self.radius)
        c1 = self.MakeCircleCurveAtPoint(geom.Point(PathObjectPrevPoint.x, PathObjectPrevPoint.y), r)
        c2 = self.MakeCircleCurveAtPoint(geom.Point(self.point.x, self.point.y), r)
        plist = c1.Intersections(c2)
        if len(plist) == 2:
            p1 = geom.Point3D(plist[0].x, plist[0].y, ps.z)
            p2 = geom.Point3D(plist[0].x, plist[0].y, ps.z)
            along = pe - ps
            right = geom.Point3D(0,0,1) ^ along
            vc = p2 - p1
            left = vc * right < 0.0
            if (self.radius < 0.0) == left:
                self.centre = p1 - ps
                self.dir = 1
            else:
                self.centre = p2 - ps
                self.dir = -1
            self.radius = r

class ColouredPath:
    def __init__(self):
        self.color_type = ColorRapidType
        self.points = []
        
    def glCommands(self):
        global NcCode_prev_po
        col = Color(self.color_type)
        cad.DrawColor(col)
        cad.BeginLines()
        for path_object in self.points:
            path_object.glVertices()
            NcCode_prev_po = path_object
        cad.EndLinesOrTriangles()
        
    def GetBox(self, box):
        global NcCode_prev_po
        for point in self.points:
            point.GetBox(box)
            NcCode_prev_po = point
        
    def WriteXML(self):
        pass # to do
    
    def ReadXml(self):
        self.color_type = GetColor(cad.GetXmlValue('col'), ColorRapidType)

        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'line':
                new_object = PathLine()
                new_object.ReadXml()
                self.points.append(new_object)
            elif child_element == 'arc':
                new_object = PathArc()
                new_object.ReadXml()
                self.points.append(new_object)

            child_element = cad.GetNextXmlChild()

class NcCodeBlock(CamObject):
    def __init__(self):
        self.text = []
        self.line_strips = []
        self.from_pos = -1
        self.to_pos = -1
        self.formatted = False
        
    def GetType(self):
        return NcCodeBlock_type
    
    def MakeACopy(self):
        new_object = NcCodeBlock()
        for text in self.text:
            new_text = ColouredText()
            new_text.str = text.str
            new_text.color_type = text.color_type
            new_object.text.append(new_text)
        for line_strip in self.line_strips:
            new_path = ColouredPath()
            new_path.color_type = line_strip.color_type
            for point in line_strip.points:
                new_path.points.append(point.MakeACopy())
            new_object.line_strips.append(new_path)
        new_object.from_pos = self.from_pos
        new_object.to_pos = self.to_pos
        new_object.formatted = self.formatted
        return new_object

    def GetBox(self, box):
        for line_strip in self.line_strips:
            line_strip.GetBox(box)
    
    def Text(self):
        if len(self.text) == 0:
            return ''
        
        str = ''
        
        for text in self.text:
            str += text.str
        str += '\n'
        
        return str
        
    def glCommands(self, marked):
        if marked: cad.GlLineWidth(3)
        for line_strip in self.line_strips:
            line_strip.glCommands()
        if marked: cad.GlLineWidth(1)
        
    def WriteXML(self):
        pass # to do
    
    def ReadXml(self):
        global NcCode_pos
        self.from_pos = NcCode_pos
        print('NcCode_pos = ' + str(NcCode_pos))
        
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'text':
                t = ColouredText()
                t.ReadXml()
                self.text.append(t)
                NcCode_pos += len(t.str)
            elif child_element == 'path':
                p = ColouredPath()
                p.ReadXml()
                self.line_strips.append(p)
            elif child_element == 'mode':
                global NcCodeBlock_multiplier
                NcCodeBlock_multiplier = cad.GetXmlFloat('units', NcCodeBlock_multiplier)

            child_element = cad.GetNextXmlChild()
            
        if len(self.text) > 0: NcCode_pos += 1
        self.to_pos = NcCode_pos
        
    def FormatText(self, textCtrl, highlighted, force_format):
        if self.formatted and not force_format:
            return
        i = self.from_pos
        for text in self.text:
            col = Color(text.color_type)
            c = wx.Colour(col.red, col.green, col.blue)
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Lucida Console', wx.FONTENCODING_SYSTEM)
            ta = wx.TextAttr(c)
            ta.SetFont(font)
            if highlighted: ta.SetBackgroundColour(wx.Colour(218, 242, 142))
            else: ta.SetBackgroundColour(wx.Colour(255, 255, 255))
            length = len(text.str)
            textCtrl.SetStyle(i, i + length, ta)
            i += length
        self.formatted = True
    
class NcCode(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        self.blocks = [] # for now, just strings, but later to be NCCodeBlock objects
        self.highlighted_block = None
        self.box = geom.Box3D()
        self.SetUsesLights(False)
        self.SetUsesGLList(True)
        
    def icon(self):
        return "nccode"
    
    def TypeName(self):
        return "NC Code"
    
    def GetType(self):
        return type
    
    def CanBeDeleted(self):
        return False
    
    def Clear(self):
        self.blocks = []
        self.KillGLLists()
        self.box = geom.Box3D()
        self.highlighted_block = None
        
    def OneOfAKind(self):
        return True
    
    def OnAdd(self):
        self.GetOwner().nccode = self        
        
    def OnRenderTriangles(self):
        global NcCode_prev_po
        NcCode_prev_po = None
        
        for block in self.blocks:
            #glPushName(block->GetIndex())
            block.glCommands(block == self.highlighted_block)
            #glPopName()
        
    def GetBox(self):
        if not self.box.valid:
            for block in self.blocks:
                block.GetBox(self.box)
                
        if not self.box.valid:
            return 0,0,0,0,0,0
        return self.box.MinX(), self.box.MinY(), self.box.MinZ(), self.box.MaxX(), self.box.MaxY(), self.box.MaxZ()
        
    def MakeACopy(self):
        object = NcCode()
        object.CopyFrom(self)
        return object
    
    def CopyFrom(self, object):
        self.blocks = []
        self.highlighted_block = None
        for block in object.blocks:
            new_block = block.MakeACopy()
            if block == object.highlighted_block:
                self.highlighted_block = new_block
            self.blocks.append(new_block)
        cad.ObjList.CopyFrom(self, object)
        
    def WriteXML(self):
        pass # to do
    
    def CallsObjListReadXml(self):
        return False
    
    def ReadXml(self):
        global NcCode_pos
        global NcCodeBlock_multiplier
        NcCode_pos = 0
        NcCodeBlock_multiplier = 1.0

        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'ncblock':
                new_object = NcCodeBlock()
                new_object.ReadXml()
                self.blocks.append(new_object)
            child_element = cad.GetNextXmlChild()
            
        CamObject.ReadXml(self)
        
        self.SetTextCtrl(wx.GetApp().frame.output_window.textCtrl)

    def SetTextCtrl(self, textCtrl):
        textCtrl.Clear()
        textCtrl.Freeze()

        import wx
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Lucida Console", wx.FONTENCODING_SYSTEM)
        ta = wx.TextAttr()
        ta.SetFont(font)
        textCtrl.SetDefaultStyle(ta)

        str = ''
        for block in self.blocks:
            str += block.Text()
        
        textCtrl.SetValue(str)
        textCtrl.SetStyle(0, 100, ta)

#        '''
#        import platform
#        if platform.system() != "Windows":
#        # for Windows, this is done in OutputTextCtrl.OnPaint
#        for block in self.blocks:
#            block.FormatText(textCtrl, block == self.highlighted_block, False)
#        '''
        
        textCtrl.Thaw()
    
    def FormatBlocks(self, textCtrl, i0, i1):
        textCtrl.Freeze()
        
        for block in self.blocks:
            if i0 <= block.from_pos and block.from_pos <= i1:
                block.FormatText(textCtrl, block == self.highlighted_block, False)
        textCtrl.Thaw()
        
    def SetHighlightedBlock(self, block):
        if self.highlighted_block != None:
            self.highlighted_block.FormatText(wx.GetApp().frame.output_window.textCtrl, False, True)
        self.highlighted_block = block
        if self.highlighted_block != None:
            self.highlighted_block.FormatText(wx.GetApp().output_window.textCtrl, True, True)
    
    def HighlightBlock(self, pos):
        self.SetHighlightedBlock(None)

        for block in self.blocks:
            if pos < block.to_pos:
                self.highlighted_block = block
                break
        self.KillGLLists()

    def GetPaths(self):
        paths = []
        for block in self.blocks:
            for colored_path in block.line_strips:
                for path_object in colored_path.points:
                    tool = Tool.Find(path_object.tool_number)
                    if tool != None:
                        paths.append((path_object, tool))
        return paths
    
    