import wx
import os
import sys
import cad

cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../../PyCAD/trunk')
sys.path.append(pycad_dir)

from App import App # from CAD
from CamFrame import CamFrame
from Program import Program
from Operations import AddOperationMenuItems

programs = []

class CamApp(App):
    def __init__(self):
        self.cam_dir = cam_dir
        App.__init__(self)
        self.program = None
        
    def NewFrame(self):
        return CamFrame(None)

    def OnNewOrOpen(self, open):
        App.OnNewOrOpen(self, open)

        # to do, check for existing program
        
        # add a program
        #print('add prgram')
        self.program = Program()
        programs.append(self.program)
        cad.AddUndoably(self.program)

    
