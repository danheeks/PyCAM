from DepthOpDlg import DepthOpDlg
from HDialog import HTypeObjectDropDown
import wx
import cad
from HDialog import ComboBoxBinded

class SketchOpDlg(DepthOpDlg):
    def __init__(self, object, title = 'Sketch Operation'):
        DepthOpDlg.__init__(self, object, False, title)

    def AddLeftControls(self):
        self.cmbSketch = HTypeObjectDropDown(self, cad.OBJECT_TYPE_SKETCH, cad.GetApp())
        self.btnSketchPick = wx.Button(self, wx.ID_ANY, 'Pick')
        self.MakeLabelAndControl('Sketches', self.cmbSketch, self.btnSketchPick).AddToSizer(self.sizerLeft)
                
        DepthOpDlg.AddLeftControls(self)
        
    def SetDefaultFocus(self):
        self.cmbSketch.SetFocus()
            
    def GetDataRaw(self):
        self.object.sketch = self.cmbSketch.GetSelectedId()
        DepthOpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.cmbSketch.SelectById(self.object.sketch)
        DepthOpDlg.SetFromDataRaw(self)
        
    def OnSketchPick(self, event):
        self.EndModal(self.btnSketchPick.GetId())
        
    def PickSketch(self):
        cad.ClearSelection()
        cad.PickObjects('Pick a sketch', cad.MARKING_FILTER_SKETCH_GROUP, True)
        
        self.cmbSketch.Recreate()
        self.Fit()
        
        id = 0
        if cad.GetNumSelected() > 0: id = cad.GetSelectedObjects()[0].GetID()
        self.cmbSketch.SelectById(id)
