from DepthOpDlg import DepthOpDlg
from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl
from NiceTextCtrl import ObjectIdsCtrl
import wx
import cad
from HDialog import HControl
from HDialog import ComboBoxBinded
import Drilling

class DrillingDlg(DepthOpDlg):
    def __init__(self, object, title = 'Pocket Operation'):
        DepthOpDlg.__init__(self, object, True, title)

    def AddLeftControls(self):
        # add all the controls to the left side
        self.idsPoints = ObjectIdsCtrl(self)
        self.btnPointsPick = wx.Button(self, wx.ID_ANY, 'Pick')
        self.MakeLabelAndControl("Points", self.idsPoints, self.btnPointsPick).AddToSizer(self.sizerLeft)
        self.dblDwell = DoubleCtrl(self)
        self.MakeLabelAndControl("Dwell", self.dblDwell).AddToSizer(self.sizerLeft)
        self.chkFeedRetract = wx.CheckBox(self, wx.ID_ANY, 'Feed Retract')
        HControl(wx.ALL, self.chkFeedRetract).AddToSizer(self.sizerLeft)
        self.chkRapidToClearance = wx.CheckBox(self, wx.ID_ANY, 'Rapid to Clearance')
        HControl(wx.ALL, self.chkRapidToClearance).AddToSizer(self.sizerLeft)
        self.chkStopSpindleAtBottom = wx.CheckBox(self, wx.ID_ANY, 'Stop Spindle at Bottom')
        HControl(wx.ALL, self.chkStopSpindleAtBottom).AddToSizer(self.sizerLeft)
        self.chkInternalCoolantOn = wx.CheckBox(self, wx.ID_ANY, 'Interal Coolant On')
        HControl(wx.ALL, self.chkInternalCoolantOn).AddToSizer(self.sizerLeft)
        
        DepthOpDlg.AddLeftControls(self)        
            
    def GetDataRaw(self):
        self.object.points = self.idsPoints.GetIdList()
        self.object.dwell = self.dblDwell.GetValue()
        self.object.retract_mode = 1 if self.chkFeedRetract.GetValue() else 0
        self.object.spindle_mode = 1 if self.chkStopSpindleAtBottom.GetValue() else 0
        self.object.internal_coolant_on = self.chkInternalCoolantOn.GetValue()
        self.object.rapid_to_clearance = self.chkRapidToClearance.GetValue()
        DepthOpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.idsPoints.SetFromIdList(self.object.points)
        self.dblDwell.SetValue(self.object.dwell)
        self.chkFeedRetract.SetValue(self.object.retract_mode != 0)
        self.chkStopSpindleAtBottom.SetValue(self.object.spindle_mode != 0)
        self.chkInternalCoolantOn.SetValue(self.object.internal_coolant_on)
        self.chkRapidToClearance.SetValue(self.object.rapid_to_clearance)
        
        self.EnableControls()
        
        DepthOpDlg.SetFromDataRaw(self)
        
    def EnableControls(self):
        pass

    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder( name, 'drilling')

    def SetPictureByWindow(self, w):
        if w == self.dblDwell: DrillingDlg.SetPictureByName(self, 'dwell')
        elif w == self.chkFeedRetract:
            if self.chkFeedRetract.GetSelection() == 1:
                DrillingDlg.SetPictureByName(self, 'feed retract')
            else:
                DrillingDlg.SetPictureByName(self, 'rapid retract')
        elif w == self.chkStopSpindleAtBottom:
            if self.chkStopSpindleAtBottom.GetSelection() == 1:
                DrillingDlg.SetPictureByName(self, 'stop spindle at bottom')
            else:
                DrillingDlg.SetPictureByName(self, 'dont stop spindle')
        elif w == self.chkInternalCoolantOn:
            if self.chkInternalCoolantOn.GetValue():
                DrillingDlg.SetPictureByName(self, 'internal coolant on')
            else:
                DrillingDlg.SetPictureByName(self, 'internal coolant off')
        elif w == self.chkRapidToClearance:
            if self.chkRapidToClearance.GetValue():
                DrillingDlg.SetPictureByName(self, 'rapid to clearance')
            else:
                DrillingDlg.SetPictureByName(self, 'rapid to standoff')
        else:
            DepthOpDlg.SetPictureByWindow(self, w)
        
    def PickPoints(self):
        cad.ClearSelection()
        cad.PickObjects('Pick a sketch', cad.MARKING_FILTER_SKETCH_GROUP, False)
        
        self.cmbSketch.Recreate()
        self.Fit()
        
        id = 0
        if cad.GetNumSelected() > 0: id = cad.GetSelectedObjects()[0].GetID()
        self.cmbSketch.SelectById(id)
        
def Do(object):
    dlg = DrillingDlg(object)
    
    while(True):
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            dlg.GetData()
            return True
        elif result == dlg.btnPointsPick.GetId():
            dlg.PickSketch()
        else:
            return False

            
            
            
            
            
            
            
