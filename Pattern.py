from CamObject import CamObject
import geom
import cad

type = 0

class Pattern(CamObject):
    def __init__(self):
        CamObject.__init__(self, id_named = True)
        self.copies1 = 1
        self.x_shift1 = 10.0
        self.y_shift1 = 0.0
        self.copies2 = 1
        self.x_shift2 = 10.0
        self.y_shift2 = 0.0
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Pattern"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "pattern"
    
    def HasEdit(self):
        return True
    
    def Edit(self):
        from PatternDlg import PatternDlg
        import wx
        dlg = PatternDlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetData()
            return True
        return False
        
    def MakeACopy(self):
        copy = Pattern()
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        CamObject.CopyFrom(self, object)
        self.copies1 = object.copies1
        self.x_shift1 = object.x_shift1
        self.y_shift1 = object.y_shift1
        self.copies2 = object.copies2
        self.x_shift2 = object.x_shift2
        self.y_shift2 = object.y_shift2
        
    def WriteXml(self):
        cad.SetXmlValue('copies1', self.copies1)
        cad.SetXmlValue('x_shift1', self.x_shift1)
        cad.SetXmlValue('y_shift1', self.y_shift1)
        cad.SetXmlValue('copies2', self.copies2)
        cad.SetXmlValue('x_shift2', self.x_shift2)
        cad.SetXmlValue('y_shift2', self.y_shift2)
        CamObject.WriteXml(self)
        
    def ReadXml(self):
        self.copies1 = cad.GetXmlInt('copies1', self.copies1)
        self.x_shift1 = cad.GetXmlFloat('x_shift1', self.x_shift1)
        self.y_shift1 = cad.GetXmlFloat('y_shift1', self.y_shift1)
        self.copies2 = cad.GetXmlInt('copies2', self.copies2)
        self.x_shift2 = cad.GetXmlFloat('x_shift2', self.x_shift2)
        self.y_shift2 = cad.GetXmlFloat('y_shift2', self.y_shift2)
        CamObject.ReadXml(self)
