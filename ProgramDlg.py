import wx
from Program import Program
from HeeksObjDlg import HeeksObjDlg
from HDialog import HControl

class ProgramDlg(HeeksObjDlg):
    def __init__(self, object, title = "Program"):
        HeeksObjDlg.__init__(self, object, title, add_picture = False)
        
    def AddLeftControls(self):
        # add the controls in one column
        self.machines = self.object.GetMachines()
        choices = []
        for machine in self.machines:
            choices.append(machine.description)
        self.cmbMachine = wx.ComboBox(self, choices = choices)
        self.MakeLabelAndControl('Machine', self.cmbMachine).AddToSizer(self.sizerLeft)
        
        self.chkOutputSame = wx.CheckBox( self, label = "output file name follows data file name" )
        HControl(wx.ALL, self.chkOutputSame).AddToSizer(self.sizerLeft)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOutputSame, self.chkOutputSame)

        self.txtOutputFile = wx.TextCtrl(self)
        self.lblOutputFile, self.btnOutputFile = self.AddFileNameControl(self.sizerLeft, "output file", self.txtOutputFile)

        self.cmbUnits = wx.ComboBox(self, choices = ["mm", "inch"])
        self.MakeLabelAndControl('Units', self.cmbUnits).AddToSizer(self.sizerLeft)
        
        self.chkAddComments = wx.CheckBox(self, wx.ID_ANY, 'Add Comments')
        HControl(wx.ALL, self.chkAddComments).AddToSizer(self.sizerLeft)
 
        self.txtMaterial = wx.TextCtrl(self, wx.ID_ANY)
        self.MakeLabelAndControl('Material', self.txtMaterial).AddToSizer(self.sizerLeft)

    def SetDefaultFocus(self):
        self.cmbMachine.SetFocus()
        
    def EnableControls(self):
        output_same = self.chkOutputSame.GetValue()
        self.txtOutputFile.Enable(output_same == False)
        self.btnOutputFile.Enable(output_same == False)
        self.lblOutputFile.Enable(output_same == False)
        
    def OnCheckOutputSame(self, event):
        if self.ignore_event_functions: return
        self.EnableControls()

    def GetDataRaw(self):
        if self.cmbMachine.GetSelection() != wx.NOT_FOUND:
            self.object.machine = self.machines[self.cmbMachine.GetSelection()]
            
        self.object.output_file_name_follows_data_file_name = self.chkOutputSame.GetValue()
        self.object.output_file = self.txtOutputFile.GetValue()
            
        if self.cmbUnits.GetValue() == "inch":
            self.object.units = 25.4
        else:
            self.object.units = 1.0
            
        self.object.add_comments = self.chkAddComments.GetValue()
        self.object.material = self.txtMaterial.GetValue()

    def SetFromDataRaw(self):
        self.cmbMachine.SetValue(self.object.machine.description)
        
        self.chkOutputSame.SetValue(self.object.output_file_name_follows_data_file_name)

        self.txtOutputFile.SetValue(self.object.output_file)
            
        if self.object.units == 25.4:
            self.cmbUnits.SetValue("inch")
        else:
            self.cmbUnits.SetValue("mm")
            
        self.chkAddComments.SetValue(self.object.add_comments)
        self.txtMaterial.SetValue(self.object.material)
