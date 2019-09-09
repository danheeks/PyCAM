import wx
import os
import sys
from nc.nc import *

cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../../PyCAD/trunk')
sys.path.append(pycad_dir)
import cad
import cam

cam.SetResPath(cam_dir)
cam.SetApp(cad.GetApp())

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
import Pocket
import Drilling
import ScriptOp
import Tags
import Tag
import CamContextTool
from HeeksConfig import HeeksConfig

programs = []

def CreateProgram(): return Program.Program()
def CreateTool(): return Tool.Tool()
def CreateTools(): return Tools.Tools()
def CreateOperations(): return Operations.Operations()
def CreatePatterns(): return Patterns.Patterns()
def CreateSurfaces(): return Surfaces.Surfaces()
def CreateStocks(): return Stocks.Stocks()
def CreateNcCode(): return NcCode.NcCode()
def CreateNcCodeBlock(): return cam.NcCodeBlock()
def CreateProfile(): return Profile.Profile()
def CreatePocket(): return Pocket.Pocket()
def CreateDrilling(): return Drilling.Drilling()
def CreateTags(): return Tags.Tags()
def CreateTag(): return Tag.Tag()
def CreateScriptOp(): return ScriptOp.ScriptOp()

#class CamObserver(cad.Observer):
#    def __init__(self):
#        cad.Observer.__init__(self)
#        print('CamObserver __init__')
        
#    def OnRemoved(self, removed):
#        for object in removed:
#            if object.GetType() == cam.GetNcCodeType():
#                wx.GetApp().frame.output_window.Clear()

#    def OnAdded(self, added):
#        for object in added:
#            print('object added')
#            if object.GetType() == cam.GetNcCodeType():
#                wx.GetApp().program.nccode = object
#                print('nccode added')
#                wx.GetApp().frame.output_window.textCtrl.SetText()
   

class CamApp(App):
    def __init__(self):
        self.cam_dir = cam_dir
        self.program = None
        App.__init__(self)

    def GetAppName(self):
        return 'CAM ( Computer Aided Manufacturing )'

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
        cam.SetNcCodeBlockType(cad.RegisterObjectType("ncblock", CreateNcCodeBlock))
        Profile.type = cad.RegisterObjectType("Profile", CreateProfile)
        Pocket.type = cad.RegisterObjectType("Pocket", CreatePocket)
        Drilling.type = cad.RegisterObjectType("Drilling", CreateDrilling)
        Tags.type = cad.RegisterObjectType("Tags", CreateTags)
        Tag.type = cad.RegisterObjectType("Tag", CreateTag)
        ScriptOp.type = cad.RegisterObjectType("ScriptOp", CreateScriptOp)
        
#        self.cam_observer = CamObserver()
#        cad.RegisterObserver(self.cam_observer)
        
        ReadNCCodeColorsFromConfig()

    
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
#         if open == False:
#             self.frame.OnOpenFilepath('c:/users/dan heeks/downloads/two points.heeks', False)
            
    def SetTool(self, tool_number):
        tool = Tool.FindTool(tool_number)
        if tool != None:
            if self.tool_number != tool_number:
                tool_change( id = tool_number)
                
            if self.attached_to_surface:
                nc.creator.set_ocl_cutter(tool.OCLDefinition(self.attached_to_surface))

        self.tool_number = tool_number
        
    def AddTags(self, object):
        Profile.tag_drawing.profile = object
        cad.SetInputMode(Profile.tag_drawing)
        
    def GetObjectTools(self, object, from_tree_canvas = False):
        tools = App.GetObjectTools(self, object, from_tree_canvas)
        if object.GetType() == Profile.type:
            tools.append(CamContextTool.CamObjectContextTool(object, "Add Tags", "addtag", self.AddTags))
        return tools
        
def ReadNCCodeColorsFromConfig():
    config = HeeksConfig()
    cam.ClearNcCodeColors()
    cam.AddNcCodeColor('default', cad.Color(int(config.Read('ColorDefaultType', str(cad.Color(0,0,0).ref())))))
    cam.AddNcCodeColor('blocknum', cad.Color(int(config.Read('ColorBlockType', str(cad.Color(0,0,222).ref())))))
    cam.AddNcCodeColor('misc', cad.Color(int(config.Read('ColorMiscType', str(cad.Color(0,200,0).ref())))))
    cam.AddNcCodeColor('program', cad.Color(int(config.Read('ColorProgramType', str(cad.Color(255,128,0).ref())))))
    cam.AddNcCodeColor('tool', cad.Color(int(config.Read('ColorToolType', str(cad.Color(200,200,0).ref())))))
    cam.AddNcCodeColor('comment', cad.Color(int(config.Read('ColorCommentType', str(cad.Color(0,200,200).ref())))))
    cam.AddNcCodeColor('variable', cad.Color(int(config.Read('ColorVariableType', str(cad.Color(164,88,188).ref())))))
    cam.AddNcCodeColor('prep', cad.Color(int(config.Read('ColorPrepType', str(cad.Color(255,0,175).ref())))))
    cam.AddNcCodeColor('axis', cad.Color(int(config.Read('ColorAxisType', str(cad.Color(128,0,255).ref())))))
    cam.AddNcCodeColor('rapid', cad.Color(int(config.Read('ColorRapidType', str(cad.Color(222,0,0).ref())))))
    cam.AddNcCodeColor('feed', cad.Color(int(config.Read('ColorFeedType', str(cad.Color(0,179,0).ref())))))
