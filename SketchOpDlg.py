from DepthOpDlg import DepthOpDlg
from HDialog import HTypeObjectDropDown
import wx
import cad

class SketchOpDlg(DepthOpDlg):
    def __init__(self, parent, object, title = 'Sketch Operation', top_level = True):
        DepthOpDlg.__init__(self, parent, object, False, title, False)
        self.cmbSketch = HTypeObjectDropDown(self, cad.OBJECT_TYPE_SKETCH, cad.GetApp())
        self.btnSketchPick = wx.Button(self, wx.ID_ANY, 'Pick')
        self.leftControls.append(self.MakeLabelAndControl('Sketches', self.cmbSketch, self.btnSketchPick))
        
        if top_level:
            HeeksObjDlg.AddControlsAndCreate(self)
            self.cmbSketch.SetFocus()
            
    def GetDataRaw(self, object):
        object.sketch = self.cmbSketch.GetSelectedId()
        DepthOpDlg.GetDataRaw(self, object)
        
    def SetFromDataRaw(self, object):
        self.cmbSketch.SelectById(object.sketch)
        DepthOpDlg.SetFromDataRaw(self, object)
        
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
