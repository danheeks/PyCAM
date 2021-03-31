from HeeksObjDlg import HeeksObjDlg
from HDialog import HTypeObjectDropDown
from HDialog import HControl
import wx
import Tool
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl
from consts import *

class ToolDlg(HeeksObjDlg):
    def __init__(self, object, title = "Tool Definition"):
        HeeksObjDlg.__init__(self, object, title, True)
            
    def AddLeftControls(self):
        self.txtToolNumber = wx.TextCtrl(self)
        self.MakeLabelAndControl("Tool Number", self.txtToolNumber).AddToSizer(self.sizerLeft)
        
        self.cmbMaterial = wx.ComboBox(self, choices = ["High Speed Steel", "Carbide"])
        self.Bind(wx.EVT_COMBOBOX, self.OnComboMaterial, self.cmbMaterial)
        self.MakeLabelAndControl("Tool Material", self.cmbMaterial).AddToSizer(self.sizerLeft)
        
        self.cmbToolType = wx.ComboBox(self, choices = Tool.GetToolTypeNames())
        self.Bind(wx.EVT_COMBOBOX, self.OnComboToolType, self.cmbToolType)
        self.MakeLabelAndControl("Tool Type", self.cmbToolType).AddToSizer(self.sizerLeft)
        
        self.lgthDiameter = LengthCtrl(self)
        self.MakeLabelAndControl("Diameter", self.lgthDiameter).AddToSizer(self.sizerLeft)
        self.Bind(wx.EVT_TEXT, self.OnDiamChange, self.lgthDiameter)
        
        self.lgthToolLengthOffset = LengthCtrl(self)
        self.MakeLabelAndControl("Tool Length Offset", self.lgthToolLengthOffset).AddToSizer(self.sizerLeft)
        
        self.lgthFlatRadius = LengthCtrl(self)
        self.MakeLabelAndControl("Flat Radius", self.lgthFlatRadius).AddToSizer(self.sizerLeft)
        
        self.lgthCornerRadius = LengthCtrl(self)
        self.MakeLabelAndControl("Corner Radius", self.lgthCornerRadius).AddToSizer(self.sizerLeft)
        
        self.lgthCuttingEdgeAngle = DoubleCtrl(self)
        self.MakeLabelAndControl("Cutting Edge Angle", self.lgthCuttingEdgeAngle).AddToSizer(self.sizerLeft)
        
        self.lgthCuttingEdgeHeight = LengthCtrl(self)
        self.MakeLabelAndControl("Cutting Edge Height", self.lgthCuttingEdgeHeight).AddToSizer(self.sizerLeft)
        
        HeeksObjDlg.AddLeftControls(self)

    def AddRightControls(self):            
        self.txtTitle = wx.TextCtrl(self, wx.ID_ANY)
        self.MakeLabelAndControl('Title', self.txtTitle).AddToSizer(self.sizerRight)
        self.cmbTitleType = wx.ComboBox(self, choices = ["Leave manually assigned title", "Automatically Generate Title"])
        self.MakeLabelAndControl("Title Type", self.cmbTitleType).AddToSizer(self.sizerRight)
        
        HeeksObjDlg.AddRightControls(self)
            
    def GetDataRaw(self):
        self.object.tool_number = int(self.txtToolNumber.GetValue())
        self.object.material = self.cmbMaterial.GetSelection()
        self.object.type = Tool.GetToolTypeValues()[self.cmbToolType.GetSelection()]
        self.object.diameter = self.lgthDiameter.GetValue()
        self.object.tool_length_offset = self.lgthToolLengthOffset.GetValue()
        self.object.flat_radius = self.lgthFlatRadius.GetValue()
        self.object.corner_radius = self.lgthCornerRadius.GetValue()
        self.object.cutting_edge_angle = self.lgthCuttingEdgeAngle.GetValue()
        self.object.cutting_edge_height = self.lgthCuttingEdgeHeight.GetValue()
        self.object.title = self.txtTitle.GetValue()
        self.object.automatically_generate_title = (self.cmbTitleType.GetSelection() != 0)

        HeeksObjDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.txtToolNumber.SetValue(str(self.object.tool_number))
        self.cmbMaterial.SetSelection(self.object.material)
        self.cmbToolType.SetSelection(Tool.GetToolTypeIndex(self.object.type))
        self.lgthDiameter.SetValue(self.object.diameter)
        self.lgthToolLengthOffset.SetValue(self.object.tool_length_offset)
        self.lgthFlatRadius.SetValue(self.object.flat_radius)
        self.lgthCornerRadius.SetValue(self.object.corner_radius)
        self.lgthCuttingEdgeAngle.SetValue(self.object.cutting_edge_angle)
        self.lgthCuttingEdgeHeight.SetValue(self.object.cutting_edge_height)
        self.txtTitle.SetValue(self.object.title)
        self.cmbTitleType.SetSelection(1 if self.object.automatically_generate_title else 0)
        
        self.EnableAndSetCornerFlatAndAngle()

        HeeksObjDlg.SetFromDataRaw(self)
    
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder(name, "tool")
        
    def SetPictureByNameAndFolder(self, name, folder):
        if self.picture:
            self.picture.SetPicture(wx.GetApp().cam_dir + '/bitmaps/' + folder + '/' + name + '.png')
        
    def SetPictureByWindow(self, w):
        type = Tool.GetToolTypeValues()[self.cmbToolType.GetSelection()]
        if type == TOOL_TYPE_DRILL:
            if w == self.lgthDiameter:self.SetPictureByName('drill_diameter')
            elif w == self.lgthToolLengthOffset:self.SetPictureByName('drill_offset')
            elif w == self.lgthFlatRadius:self.SetPictureByName('drill_flat')
            elif w == self.lgthCornerRadius:self.SetPictureByName('drill_corner')
            elif w == self.lgthCuttingEdgeAngle:self.SetPictureByName('drill_angle')
            elif w == self.lgthCuttingEdgeHeight:self.SetPictureByName('drill_height')
            else: self.SetPictureByName('drill')
        elif type == TOOL_TYPE_CENTREDRILL:
            if w == self.lgthDiameter:self.SetPictureByName('centre_drill_diameter')
            elif w == self.lgthToolLengthOffset:self.SetPictureByName('centre_drill_offset')
            elif w == self.lgthFlatRadius:self.SetPictureByName('centre_drill_flat')
            elif w == self.lgthCornerRadius:self.SetPictureByName('centre_drill_corner')
            elif w == self.lgthCuttingEdgeAngle:self.SetPictureByName('centre_drill_angle')
            elif w == self.lgthCuttingEdgeHeight:self.SetPictureByName('centre_drill_height')
            else: self.SetPictureByName('centre_drill')
        elif type == TOOL_TYPE_ENDMILL or type == TOOL_TYPE_SLOTCUTTER:
            if w == self.lgthDiameter:self.SetPictureByName('end_mill_diameter')
            elif w == self.lgthToolLengthOffset:self.SetPictureByName('end_mill_offset')
            elif w == self.lgthFlatRadius:self.SetPictureByName('end_mill_flat')
            elif w == self.lgthCornerRadius:self.SetPictureByName('end_mill_corner')
            elif w == self.lgthCuttingEdgeAngle:self.SetPictureByName('end_mill_angle')
            elif w == self.lgthCuttingEdgeHeight:self.SetPictureByName('end_mill_height')
            else: self.SetPictureByName('end_mill')
        elif type == TOOL_TYPE_BALLENDMILL:
            if w == self.lgthDiameter:self.SetPictureByName('ball_mill_diameter')
            elif w == self.lgthToolLengthOffset:self.SetPictureByName('ball_mill_offset')
            elif w == self.lgthFlatRadius:self.SetPictureByName('ball_mill_flat')
            elif w == self.lgthCornerRadius:self.SetPictureByName('ball_mill_corner')
            elif w == self.lgthCuttingEdgeAngle:self.SetPictureByName('ball_mill_angle')
            elif w == self.lgthCuttingEdgeHeight:self.SetPictureByName('ball_mill_height')
            else: self.SetPictureByName('ball_mill')
        elif type == TOOL_TYPE_CHAMFER:
            if w == self.lgthDiameter:self.SetPictureByName('chamfer_diameter')
            elif w == self.lgthToolLengthOffset:self.SetPictureByName('chamfer_offset')
            elif w == self.lgthFlatRadius:self.SetPictureByName('chamfer_flat')
            elif w == self.lgthCornerRadius:self.SetPictureByName('chamfer_corner')
            elif w == self.lgthCuttingEdgeAngle:self.SetPictureByName('chamfer_angle')
            elif w == self.lgthCuttingEdgeHeight:self.SetPictureByName('chamfer_height')
            else: self.SetPictureByName('chamfer')
        elif type == TOOL_TYPE_ENGRAVER:
            if w == self.lgthDiameter:self.SetPictureByName('engraver_diameter')
            elif w == self.lgthToolLengthOffset:self.SetPictureByName('engraver_offset')
            elif w == self.lgthFlatRadius:self.SetPictureByName('engraver_flat')
            elif w == self.lgthCornerRadius:self.SetPictureByName('engraver_corner')
            elif w == self.lgthCuttingEdgeAngle:self.SetPictureByName('engraver_angle')
            elif w == self.lgthCuttingEdgeHeight:self.SetPictureByName('engraver_height')
            else: self.SetPictureByName('engraver')

    def OnComboToolType(self, e):
        self.EnableAndSetCornerFlatAndAngle()
        self.SetTitleFromControls()
        HeeksObjDlg.SetPicture(self)
        
    def OnComboMaterial(self, e):
        self.SetTitleFromControls()
        HeeksObjDlg.SetPicture(self)
        
    def EnableAndSetCornerFlatAndAngle(self):
        type = Tool.GetToolTypeValues()[self.cmbToolType.GetSelection()]
        if type == TOOL_TYPE_DRILL or type == TOOL_TYPE_CENTREDRILL:
            self.lgthCornerRadius.Enable(False)
            self.lgthCornerRadius.SetLabel("")
            self.lgthFlatRadius.Enable(False)
            self.lgthFlatRadius.SetLabel("")
            self.lgthCuttingEdgeAngle.Enable()
            self.lgthCuttingEdgeAngle.SetValue(self.object.cutting_edge_angle)
        elif type == TOOL_TYPE_ENDMILL or type == TOOL_TYPE_SLOTCUTTER:
            self.lgthCornerRadius.Enable()
            self.lgthCornerRadius.SetValue(self.object.corner_radius)
            self.lgthFlatRadius.Enable(False)
            self.lgthFlatRadius.SetLabel("")
            self.lgthCuttingEdgeAngle.Enable(False)
            self.lgthCuttingEdgeAngle.SetLabel("")
        elif type == TOOL_TYPE_BALLENDMILL:
            self.lgthCornerRadius.Enable(False)
            self.lgthCornerRadius.SetLabel("")
            self.lgthFlatRadius.Enable(False)
            self.lgthFlatRadius.SetLabel("")
            self.lgthCuttingEdgeAngle.Enable(False)
            self.lgthCuttingEdgeAngle.SetLabel("")
        elif type == TOOL_TYPE_CHAMFER or type == TOOL_TYPE_ENGRAVER:
            self.lgthCornerRadius.Enable(False)
            self.lgthCornerRadius.SetLabel("")
            self.lgthFlatRadius.Enable()
            self.lgthFlatRadius.SetValue(self.object.flat_radius)
            self.lgthCuttingEdgeAngle.Enable()
            self.lgthCuttingEdgeAngle.SetValue(self.object.cutting_edge_angle)
            
    def SetTitleFromControls(self):
        if self.ignore_event_functions:
            return
        save_object = self.object
        self.object = self.object.MakeACopy()
        self.GetData()
        self.ignore_event_functions = True
        self.object.ResetTitle()
        self.txtTitle.SetValue(self.object.title)
        self.object = save_object
        self.ignore_event_functions = False
            
    def OnDiamChange(self, e):
        self.SetTitleFromControls()