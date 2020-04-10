from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import ObjectIdsCtrl
import wx
import cad

class SolidsDlg(HeeksObjDlg):
    def __init__(self, object, title, add_picture = True):
        HeeksObjDlg.__init__(self, object, title, add_picture)

    def AddLeftControls(self):
        self.idsSolids = ObjectIdsCtrl(self)
        self.btnSolidsPick = wx.Button(self, wx.ID_ANY, 'Pick')
        self.MakeLabelAndControl('Solids', self.idsSolids, self.btnSolidsPick).AddToSizer(self.sizerLeft)
        self.Bind(wx.EVT_BUTTON, self.OnSolidsPick, self.btnSolidsPick)
                
        HeeksObjDlg.AddLeftControls(self)
        
    def SetDefaultFocus(self):
        self.idsSolids.SetFocus()
            
    def GetDataRaw(self):
        self.object.solids = self.idsSolids.GetIdList()
        HeeksObjDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.idsSolids.SetFromIdList(self.object.solids)
        HeeksObjDlg.SetFromDataRaw(self)
        
    def OnSolidsPick(self, event):
        self.EndModal(self.btnSolidsPick.GetId())
        
    def PickSolids(self):
        cad.ClearSelection(True)
        wx.GetApp().PickObjects('Pick solids', cad.MARKING_FILTER_STL_SOLID, False)
        
        solids = []
        for object in cad.GetSelectedObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_STL_SOLID:
                solids.append(object.GetID())
                
        self.idsSolids.SetFromIdList(solids)
        self.Fit()
