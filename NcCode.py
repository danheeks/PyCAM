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

    def icon(self):
        return "nccode"
    
    def TypeName(self):
        return "nccode"
    
    def GetTitle(self):
        return 'NC Code'
    
    def GetType(self):
        return type
    
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
        
    def GetBox(self):
        box = geom.Box3D()
        self.nc_code.GetBox(box)
        return box
        
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
        self.SetTextCtrl(wx.GetApp().frame.output_window.textCtrl)
        
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
            self.FormatBlockText(highlighted_block, wx.GetApp().frame.output_window.textCtrl, False, True)
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
    
    