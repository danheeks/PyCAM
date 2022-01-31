from HeeksObjDlg import HeeksObjDlg
from HDialog import HTypeObjectDropDown
from HDialog import HControl
import wx
import Tool
import Pattern
import Surface

def GetToolNumber(object):
    return object.tool_number

class OpDlg(HeeksObjDlg):
    def __init__(self, op, title = "", want_tool_control = True, picture = True):
        self.want_tool_control = want_tool_control
        HeeksObjDlg.__init__(self, op, title, picture)
            
    def AddLeftControls(self):
        self.cmbTool = None
        if self.want_tool_control:
            self.cmbTool = HTypeObjectDropDown(self, Tool.type, wx.GetApp().program.tools, self.OnComboOrCheck, GetToolNumber)
            self.MakeLabelAndControl('Tool', self.cmbTool).AddToSizer(self.sizerLeft)
            
        self.cmbPattern = HTypeObjectDropDown(self, Pattern.type, wx.GetApp().program.patterns, self.OnComboOrCheck)
        self.MakeLabelAndControl('Pattern', self.cmbPattern).AddToSizer(self.sizerLeft)
        self.cmbSurface = HTypeObjectDropDown(self, Surface.type, wx.GetApp().program.surfaces, self.OnComboOrCheck)
        self.MakeLabelAndControl('Surface', self.cmbSurface).AddToSizer(self.sizerLeft)
        
        HeeksObjDlg.AddLeftControls(self)

    def AddRightControls(self):            
        self.txtComment = wx.TextCtrl(self, wx.ID_ANY)
        self.MakeLabelAndControl('Comment', self.txtComment).AddToSizer(self.sizerRight)
        self.chkActive = wx.CheckBox(self, wx.ID_ANY, 'Active')
        HControl(wx.ALL, self.chkActive).AddToSizer(self.sizerRight)
        self.txtTitle = wx.TextCtrl(self, wx.ID_ANY)
        self.MakeLabelAndControl('Title', self.txtTitle).AddToSizer(self.sizerRight)
        
        HeeksObjDlg.AddRightControls(self)

    def SetDefaultFocus(self):
        if self.cmbTool: self.cmbTool.SetFocus()
        else: self.cmbPattern.SetFocus()
            
    def GetDataRaw(self):
        self.object.comment = self.txtComment.GetValue()
        self.object.active = self.chkActive.GetValue()
        self.object.title = self.txtTitle.GetValue()
        if self.object.title != self.object.GetTitle():
            self.object.title_made_from_id = False
        if self.cmbTool:
            self.object.tool_number = self.cmbTool.GetSelectedId()
        else:
            self.object.tool_number = 0
        self.object.pattern = self.cmbPattern.GetSelectedId()
        self.object.surface = self.cmbSurface.GetSelectedId()
        HeeksObjDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.txtComment.SetValue(self.object.comment)
        self.chkActive.SetValue(self.object.active)
        self.txtTitle.SetValue(self.object.GetTitle())
        if self.cmbTool:
            self.cmbTool.SelectById(self.object.tool_number)
        self.cmbPattern.SelectById(self.object.pattern)
        self.cmbSurface.SelectById(self.object.surface)
        HeeksObjDlg.SetFromDataRaw(self)
    
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder(name, "op")
        
    def SetPictureByNameAndFolder(self, name, folder):
        if self.picture:
            self.picture.SetPicture(wx.GetApp().cam_dir + '/bitmaps/' + folder + '/' + name + '.png')
        
    def SetPictureByWindow(self, w):
        if w == self.cmbPattern:
            pattern_id = self.cmbPattern.GetSelectedId()
            if pattern_id != 0:
#                PatternDlg.RedrawBitmap(self.picture.bitmap, cad.GetIDObject(PatternType, pattern_id)))
                self.picture.Refresh()
            else:
                self.SetPictureByName('general')
        elif w == self.cmbSurface:self.SetPictureByNameAndFolder('general', 'surface')
        else:
            self.SetPictureByName('general')