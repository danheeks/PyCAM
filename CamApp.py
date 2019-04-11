import wx
import os
import sys
from nc.nc import *

cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../../PyCAD/trunk')
sys.path.append(pycad_dir)
import cad

from App import App # from CAD
from CamFrame import CamFrame
import Program
import Tool
import Tools
import Operations
import Patterns
import Surfaces
import Stocks
import NcCode
import Profile

programs = []

def CreateProgram(): return Program.Program()
def CreateTool(): return Tool.Tool()
def CreateTools(): return Tools.Tools()
def CreateOperations(): return Operations.Operations()
def CreatePatterns(): return Patterns.Patterns()
def CreateSurfaces(): return Surfaces.Surfaces()
def CreateStocks(): return Stocks.Stocks()
def CreateNcCode(): return NcCode.NcCode()
def CreateProfile(): return Profile.Profile()

class CamApp(App):
    def __init__(self):
        self.cam_dir = cam_dir
        self.program = None
        App.__init__(self)
        
    def RegisterObjectTypes(self):
        App.RegisterObjectTypes(self)
        Program.type = cad.RegisterObjectType("Program", CreateProgram)
        Tools.type = cad.RegisterObjectType("Tools", CreateTools)
        Tool.type = cad.RegisterObjectType("Tool", CreateTool)
        Operations.type = cad.RegisterObjectType("Operations", CreateOperations)
        Patterns.type = cad.RegisterObjectType("Patterns", CreatePatterns)
        Surfaces.type = cad.RegisterObjectType("Surfaces", CreateSurfaces)
        Stocks.type = cad.RegisterObjectType("Stocks", CreateStocks)
        NcCode.type = cad.RegisterObjectType("nccode", CreateNcCode)
        Profile.type = cad.RegisterObjectType("Profile", CreateProfile)
    
    def NewFrame(self, pos=wx.DefaultPosition, size=wx.DefaultSize):
        return CamFrame(None, pos = pos, size = size)
        
    def AddProgramIfThereIsntOne(self):
        # check if there is already a program in the document
        doc = cad.GetApp()
        object = doc.GetFirstChild()
        while object != None:
            if object.GetType() == Program.type:
                self.program = object
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
        
        if open == False:
            self.frame.OnOpenFilepath('c:/users/dan heeks/downloads/profile.heeks', False)
            
    def SetTool(self, tool_number):
        tool = Tool.FindTool(tool_number)
        if tool != None:
            if self.tool_number != tool_number:
                tool_change( id = tool_number)
                
            if self.attached_to_surface:
                nc.creator.set_ocl_cutter(tool.OCLDefinition(self.attached_to_surface))

        self.tool_number = tool_number
        
        

