from AutoProgramDlg import AutoProgramDlg

class AutoProgram:
    def __init__(self):
        self.ReadFromConfig()
    
    def ReadFromConfig(self):
        pass
        
    def WriteToConfig(self):
        pass
    
    def Edit(self):
        dlg = AutoProgramDlg()
        dlg.SetFromData(self)
        if dlg.ShowModal():
            dlg.GetData(self)
            self.WriteToConfig()
            return True
        return False
    
    def Run(self):
        # automatically create stocks, tools, operations, g-code
        pass