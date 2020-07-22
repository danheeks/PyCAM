from HDialog import HDialog
from HDialog import HControl
from HDialog import control_border
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl
import wx
import AutoProgram

class AutoProgramDlg(HDialog):
    def __init__(self, auto_program):
        HDialog.__init__(self, "Auto Program")
        
        sizerMain = wx.BoxSizer(wx.HORIZONTAL)
        
        # add left sizer
        self.sizerLeft = wx.BoxSizer(wx.VERTICAL)
        sizerMain.Add(self.sizerLeft, 0, wx.ALL, control_border)
            
        # add right sizer
        self.sizerRight = wx.BoxSizer(wx.VERTICAL)
        sizerMain.Add(self.sizerRight, 0, wx.ALL, control_border)
        
        self.ignore_event_functions = True
        
        # add left controls
        self.lgthYMargin = LengthCtrl(self)
        self.MakeLabelAndControl('Y Margin', self.lgthYMargin).AddToSizer(self.sizerLeft)
        self.lgthXMargin = LengthCtrl(self)
        self.MakeLabelAndControl('X Margin', self.lgthXMargin).AddToSizer(self.sizerLeft)
        self.chkCreateGCode = wx.CheckBox(self, wx.ID_ANY, 'Create G-Code')
        HControl(wx.ALL, self.chkCreateGCode).AddToSizer(self.sizerLeft)
        self.chkBigRigidPart = wx.CheckBox(self, wx.ID_ANY, 'Big Rigid Part')
        HControl(wx.ALL, self.chkBigRigidPart).AddToSizer(self.sizerLeft)

        # add right controls
        cut_mode_choices = []
        for material in AutoProgram.stock_thicknesses:
            cut_mode_choices.append(material)
        self.cmbMaterial = wx.ComboBox(self, choices = cut_mode_choices)
        self.MakeLabelAndControl("Material", self.cmbMaterial).AddToSizer(self.sizerRight)
        self.lgthTagWidth = LengthCtrl(self)
        self.MakeLabelAndControl('Tag Width', self.lgthTagWidth).AddToSizer(self.sizerRight)
        self.lgthTagHeight = LengthCtrl(self)
        self.MakeLabelAndControl('Tag Height', self.lgthTagHeight).AddToSizer(self.sizerRight)
        self.dblTagAngle = DoubleCtrl(self)
        self.MakeLabelAndControl('Tag Angle', self.dblTagAngle).AddToSizer(self.sizerRight)
        self.lgthTagYMargin = LengthCtrl(self)
        self.MakeLabelAndControl('Tag Y Margin', self.lgthTagYMargin).AddToSizer(self.sizerRight)
        
        
        self.MakeOkAndCancel(wx.HORIZONTAL).AddToSizer(self.sizerRight)
            
        self.SetFromData(auto_program)
        
        self.SetSizer( sizerMain )
        sizerMain.SetSizeHints( self )
        sizerMain.Fit( self )
        
        self.ignore_event_functions = False

        self.SetDefaultFocus()
        
    def SetDefaultFocus(self):
        self.lgthYMargin.SetFocus()
        
    def SetFromData(self, auto_program):
        self.lgthXMargin.SetValue(auto_program.x_margin)
        self.lgthYMargin.SetValue(auto_program.y_margin)
        self.cmbMaterial.SetValue(auto_program.material)
        self.chkCreateGCode.SetValue(auto_program.create_gcode)
        self.lgthTagWidth.SetValue(auto_program.tag_width)
        self.lgthTagHeight.SetValue(auto_program.tag_height)
        self.dblTagAngle.SetValue(auto_program.tag_angle)
        self.lgthTagYMargin.SetValue(auto_program.tag_y_margin)
        self.chkBigRigidPart.SetValue(auto_program.big_rigid_part)
        
    def GetData(self, auto_program):
        auto_program.x_margin = self.lgthXMargin.GetValue()
        auto_program.y_margin = self.lgthYMargin.GetValue()
        auto_program.material = self.cmbMaterial.GetValue()
        auto_program.create_gcode = self.chkCreateGCode.GetValue()
        auto_program.tag_width = self.lgthTagWidth.GetValue()
        auto_program.tag_height = self.lgthTagHeight.GetValue()
        auto_program.tag_angle = self.dblTagAngle.GetValue()
        auto_program.tag_y_margin = self.lgthTagYMargin.GetValue()
        auto_program.big_rigid_part = self.chkBigRigidPart.GetValue()
        