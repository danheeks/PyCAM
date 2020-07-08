from CamObject import CamObject
import geom
import cad
from HeeksConfig import HeeksConfig
import math
import wx
from Object import PyProperty
import cam

type = 0
    
class NcCode(CamObject):
    def __init__(self):
        self.nc_code = cam.NcCode()
        CamObject.__init__(self)
        self.nc_code.SetOwner(self)
        self.box = None

    def icon(self):
        return "nccode"
    
    def TypeName(self):
        return "nccode"
    
    def GetTitle(self):
        return 'NC Code'
    
    def GetType(self):
        return type
    
#     def GetBox(self):
#         box = geom.Box3D()
#         self.nc_code.GetBox(box)
#         return box
    
    def CanBeDeleted(self):
        return False
    
    def Clear(self):
        self.nc_code.Clear()
        
    def OneOfAKind(self):
        return True
    
    def OnAdd(self):
        self.GetOwner().nccode = self        
    
    def OnGlCommands(self, select, marked, no_color):
        self.nc_code.OnGlCommands(select, marked, no_color)
        
    def KillGLLists(self):
        self.nc_code.KillGLLists()
        
#    def GetBox(self):
#        if self.box == None:
#            self.box = geom.Box3D()
#            self.nc_code.GetBox(self.box)
#            print('self.box = ' + str(self.box))
#        return None
#        return self.box
        
    def MakeACopy(self):
        object = NcCode()
        object.CopyFrom(self)
        return object
    
    def CopyFrom(self, object):
        pass
        #self.nc_code.CopyFrom(object)
    
    def CallsObjListReadXml(self):
        return False

    def ReadXml(self):
        self.nc_code.ReadXml()
        wx.GetApp().output_window.SetNcCodeObject(self.nc_code)
        
    def WriteXml(self):
        self.nc_code.WriteXml()
        
    def SetClickMarkPoint(self, marked_object, ray_start, ray_direction):
        self.nc_code.SetClickMarkPoint(marked_object, ray_start, ray_direction)

    def SetTextCtrl(self, textCtrl):
        textCtrl.Clear()
        textCtrl.Freeze()

        import wx
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Lucida Console", wx.FONTENCODING_SYSTEM)
        ta = wx.TextAttr()
        ta.SetFont(font)
        textCtrl.SetDefaultStyle(ta)

        s = ''
        
        for block in self.nc_code.GetBlocks():
            s += block.Text()
            s += '\n'
        
        textCtrl.SetValue(s)
        textCtrl.SetStyle(0, 100, ta)

#        '''
#        import platform
#        if platform.system() != "Windows":
#        # for Windows, this is done in OutputTextCtrl.OnPaint
#        for block in self.blocks:
#            block.FormatText(textCtrl, block == self.highlighted_block, False)
#        '''
        
        textCtrl.Thaw()
    
    def FormatBlockText(self, block, textCtrl, highlighted, force_format):
        if block.formatted and not force_format:
            return
        i = block.from_pos
        for text in block.GetTexts():
            col = cam.CncColor(text.color_type)
            c = wx.Colour(col.red, col.green, col.blue)
            length = len(text.str)
            
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Lucida Console', wx.FONTENCODING_SYSTEM)
            ta = wx.TextAttr(c)
            ta.SetFont(font)
            if highlighted:
                ta.SetBackgroundColour(wx.Colour(218, 242, 142))
            else:
                ta.SetBackgroundColour(wx.Colour(255, 255, 255))
            textCtrl.SetStyle(i, i + length, ta)
            i += length
        block.formatted = True

    def FormatBlocks(self, textCtrl, i0, i1):
        textCtrl.Freeze()
        
        highlighted_block = self.nc_code.GetHighlightedBlock()
        for block in self.nc_code.GetBlocks():
            if i0 <= block.from_pos and block.from_pos <= i1:
                self.FormatBlockText(block, textCtrl, block == highlighted_block, False)
        textCtrl.Thaw()
        
    def GetHighlightedBlock(self):
        return self.nc_code.GetHighlightedBlock()
        
    def SetHighlightedBlock(self, block):
        highlighted_block = self.nc_code.GetHighlightedBlock()
        if highlighted_block != None:
            self.FormatBlockText(highlighted_block, wx.GetApp().output_window.textCtrl, False, True)
        self.nc_code.SetHighlightedBlock(block)
        if block != None:
            self.FormatBlockText(block, wx.GetApp().output_window.textCtrl, True, True)
    
    def HighlightBlock(self, pos):
        self.SetHighlightedBlock(None)

        for block in self.nc_code.GetBlocks():
            if pos < block.to_pos:
                self.nc_code.SetHighlightedBlock(block)
                break
        self.nc_code.DestroyGLLists()
    
class NcCodeWriter:
    # this fills out an NcCode object with path, used in backplotting, instead of the old hxml_writer
    def __init__(self, nccode):
        self.nccode = nccode
        self.t = None
        self.oldp = geom.Point3D(0,0,50)
        self.current_block = None
        self.current_path = None

    def begin_ncblock(self):
        self.current_block = cam.NewNcCodeBlock()

    def end_ncblock(self):
        self.nccode.nc_code.AddBlock(self.current_block)
        self.current_block = None

    def add_text(self, s, col, cdata):
        text = cam.NewColouredText()
        text.str = s
        text.color_type = cam.GetTextColor(s)
        self.current_block.AddText(text)

    def set_mode(self, units):
        cam.SetMultiplier(float(units))
        
    def metric(self):
        self.set_mode(units = 1.0)
        
    def imperial(self):
        self.set_mode(units = 25.4)

    def begin_path(self, col):
        self.current_path = cam.NewColouredPath()
        self.current_path.color_type = cam.GetTextColor(col)

    def end_path(self):
        self.current_block.AddPath(self.current_path)
        self.current_path = None
        
    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.begin_path("rapid")
        self.add_line(x, y, z, a, b, c)
        self.end_path()
        
    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        self.begin_path("feed")
        self.add_line(x, y, z, a, b, c)
        self.end_path()

    def arc_cw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.begin_path("feed")
        self.add_arc(x, y, z, i, j, k, r, -1)
        self.end_path()

    def arc_ccw(self, x=None, y=None, z=None, i=None, j=None, k=None, r=None):
        self.begin_path("feed")
        self.add_arc(x, y, z, i, j, k, r, 1)
        self.end_path()
        
    def tool_change(self, id):
        self.t = id
            
    def current_tool(self):
        return self.t
            
    def spindle(self, s, clockwise):
        pass
    
    def feedrate(self, f):
        pass

    def add_line(self, x, y, z, a = None, b = None, c = None):
        line = cam.NewPathLine()
        if x != None: self.oldp.x = float(x)
        if y != None: self.oldp.y = float(y)
        if z != None: self.oldp.z = float(z)
        line.point = geom.Point3D(self.oldp)
        self.current_path.AddPathObject(line)
        
    def add_arc(self, x, y, z, i, j, k, r = None, d = None):
        arc = cam.NewPathArc()
        arc.c = geom.Point3D(self.oldp)
        if i != None: arc.c.x = float(i) - self.oldp.x
        if j != None: arc.c.y = float(j) - self.oldp.y
        if k != None: arc.c.z = float(k) - self.oldp.z
        if x != None: self.oldp.x = float(x)
        if y != None: self.oldp.y = float(y)
        if z != None: self.oldp.z = float(z)
        arc.point = geom.Point3D(self.oldp)
        if r != None: arc.radius = float(r)
        if d != None: arc.dir = int(d)
        self.current_path.AddPathObject(arc)
        
    