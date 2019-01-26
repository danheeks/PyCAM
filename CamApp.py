import wx
import os
import sys

cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../../PyCAD/trunk')
sys.path.append(pycad_dir)
import cad

from App import App # from CAD
from CamFrame import CamFrame
import Program
from Operations import AddOperationMenuItems

programs = []

class CamApp(App):
    def __init__(self):
        self.cam_dir = cam_dir
        App.__init__(self)
        self.program = None
        
    def OnInit(self):
        result = super().OnInit()
        cad.RegisterXMLRead("Program", Program.XMLRead)
        return result
    
    def NewFrame(self):
        return CamFrame(None)
        
    def AddProgramIfThereIsntOne(self):
        # check if there is already a program in the document
        doc = cad.GetApp()
        object = doc.GetFirstChild()
        while object != None:
            if object.GetType() == cad.OBJECT_TYPE_PYTHON:
                if object.GetTypeString() == "Program":
                    print("Program found")
                    return
            object = doc.GetNextChild()
        
        # add a program
        self.program = Program.Program()
        programs.append(self.program)
        self.program.add_initial_children()        
        cad.AddUndoably(self.program)

    def OnNewOrOpen(self, open):
        App.OnNewOrOpen(self, open)
        self.AddProgramIfThereIsntOne()
        

