from HeeksObjDlg import HeeksObjDlg
from HDialog import HTypeObjectDropDown
from HDialog import HControl
import wx

class OpDlg(HeeksObjDlg):
    def __init__(self, parent, op, title = "", top_level = True, want_tool_control = True, picture = True):
        HeeksObjDlg.__init__(self, op, title, top_level, picture)
        self.cmbTool = None
        if want_tool_control:
            # to think about
            ToolType = 0

            self.cmbTool = HTypeObjectDropDown(self, ToolType, wx.GetApp().program.tools, self.OnComboOrCheck)
            self.leftControls.append(self.MakeLabelAndControl('Tool', self.cmbTool))
            
        #temporary code
        PatternType = 0
        SurfaceType = 0
            
        self.cmbPattern = HTypeObjectDropDown(self, PatternType, wx.GetApp().program.patterns, self.OnComboOrCheck)
        self.leftControls.append(self.MakeLabelAndControl('Pattern', self.cmbPattern))
        self.cmbSurface = HTypeObjectDropDown(self, SurfaceType, wx.GetApp().program.surfaces, self.OnComboOrCheck)
        self.leftControls.append(self.MakeLabelAndControl('Surface', self.cmbSurface))

        self.txtComment = wx.TextCtrl(self, wx.ID_ANY)
        self.rightControls.append(self.MakeLabelAndControl('Comment', self.txtComment))
        self.chkActive = wx.CheckBox(self, wx.ID_ANY, 'Active')
        self.rightControls.append(HControl(wx.ALL, self.chkActive))
        self.txtTitle = wx.TextCtrl(self, wx.ID_ANY)
        self.rightControls.append(self.MakeLabelAndControl('Title', self.txtTitle))

        if top_level:
            self.AddControlsAndCreate()
            if self.cmbTool: self.cmbTool.SetFocus()
            else: self.cmbPattern.SetFocus
            
    def GetDataRaw(self, object):
        object.comment = self.txtComment.GetValue()
        object.active = self.chkActive.GetValue()
        object.title = self.txtTitle.GetValue()
        if object.title != object.GetTitle():
            object.title_made_from_id = False
        if self.cmbTool:
            object.tool_number = self.cmbTool.GetSelectedId()
        else:
            object.tool_number = 0
        object.pattern = self.cmbPattern.GetSelectedId()
        object.surface = self.cmbSurface.GetSelectedId()
        HeeksObjDlg.GetDataRaw(self, object)
        
    def SetFromDataRaw(self, object):
        self.txtComment.SetValue(object.comment)
        self.chkActive.SetValue(object.active)
        self.txtTitle.SetValue(object.GetTitle())
        if self.cmbTool:
            self.cmbTool.SelectById(object.tool_number)
        self.cmbPattern.SelectById(object.pattern)
        self.cmbSurface.SelectById(object.surface)
        HeeksObjDlg.SetFromDataRaw(self, object)
    
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