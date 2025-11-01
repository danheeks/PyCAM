import os
import sys
cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../PyCAD')
sys.path.append(pycad_dir)
import wx
from nc.nc import *
import cad
import cam

cam.SetResPath(cam_dir)
cam.SetApp(cad.GetApp())

from SolidApp import SolidApp # from CAD
import Program
import Tool
import Tools
import Operations
import Patterns
import Surface
import Surfaces
import Stock
import Stocks
import NcCode
import Profile
import Pocket
import Drilling
import ScriptOp
import Tags
import Tag
import Pattern
import SerialNums
import CamContextTool
from HeeksConfig import HeeksConfig
from OutputWindow import OutputWindow
import math
import geom
from Ribbon import RB
from Ribbon import Ribbon

programs = []

def CreateProgram(): return Program.Program()
def CreateTool(): return Tool.Tool()
def CreateTools(): return Tools.Tools()
def CreateOperations(): return Operations.Operations()
def CreatePatterns(): return Patterns.Patterns()
def CreateSurface(): return Surface.Surface()
def CreateSurfaces(): return Surfaces.Surfaces()
def CreateStock(): return Stock.Stock()
def CreateStocks(): return Stocks.Stocks()
def CreateNcCode(): return NcCode.NcCode()
def CreateNcCodeBlock(): return cam.NcCodeBlock()
def CreateProfile(): return Profile.Profile()
def CreatePocket(): return Pocket.Pocket()
def CreateDrilling(): return Drilling.Drilling()
def CreateSerialNums(): return SerialNums.SerialNums()
def CreateTags(): return Tags.Tags()
def CreateTag(): return Tag.Tag()
def CreateScriptOp(): return ScriptOp.ScriptOp()
def CreatePattern(): return Pattern.Pattern()

def ImportTooltable():
    cad.OpenXmlFile(cad.GetFilePathForImportExport())

class CamApp(SolidApp):
    def __init__(self):
        self.cam_dir = cam_dir
        self.program = None
        SolidApp.__init__(self)
        
    def GetAppTitle(self):
        return 'Heeks2 ( Computer Aided Manufacturing )'
       
    def GetAppConfigName(self):
        return 'Heeks2'
 
    def RegisterObjectTypes(self):
        SolidApp.RegisterObjectTypes(self)
        Program.type = cad.RegisterObjectType("Program", CreateProgram)
        Tools.type = cad.RegisterObjectType("Tools", CreateTools)
        Tool.type = cad.RegisterObjectType("Tool", CreateTool)
        Operations.type = cad.RegisterObjectType("Operations", CreateOperations)
        Pattern.type = cad.RegisterObjectType("Pattern", CreatePattern)
        Patterns.type = cad.RegisterObjectType("Patterns", CreatePatterns)
        Surface.type = cad.RegisterObjectType("Surface", CreateSurface)
        Surfaces.type = cad.RegisterObjectType("Surfaces", CreateSurfaces)
        Stock.type = cad.RegisterObjectType("Stock", CreateStock)
        Stocks.type = cad.RegisterObjectType("Stocks", CreateStocks)
        NcCode.type = cad.RegisterObjectType("nccode", CreateNcCode)
        cam.SetNcCodeBlockType(cad.RegisterObjectType("ncblock", CreateNcCodeBlock))
        Profile.type = cad.RegisterObjectType("Profile", CreateProfile)
        Pocket.type = cad.RegisterObjectType("Pocket", CreatePocket)
        Drilling.type = cad.RegisterObjectType("Drilling", CreateDrilling)
        Tags.type = cad.RegisterObjectType("Tags", CreateTags)
        Tag.type = cad.RegisterObjectType("Tag", CreateTag)
        ScriptOp.type = cad.RegisterObjectType("ScriptOp", CreateScriptOp)
        SerialNums.type = cad.RegisterObjectType("SerialNums", CreateSerialNums)
        
        self.RegisterImportFileTypes(['tooltable'], 'Tooltable Files', ImportTooltable)
        
        ReadNCCodeColorsFromConfig()

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
        SolidApp.OnNewOrOpen(self, open)

        self.AddProgramIfThereIsntOne()
        
        # link the output window to program's nc code obect
        self.output_window.SetNcCodeObject(self.program.nccode.nc_code)

#         if open == False:
#             self.frame.OnOpenFilepath('c:/users/dan heeks/downloads/two points.heeks', False)

    def GetAboutText(self):
        return '''Open source CAM software ( Computer Aided Manufacturing ), source code here:
https://github.com/danheeks/PyCAM

built on wxPython based CAD Software:
''' + SolidApp.GetAboutText(self) 
            
    def SetTool(self, tool_number):
        tool = Tool.FindTool(tool_number)
        if tool != None:
            if self.tool_number != tool_number:
                tool_change( id = tool_number)
                
            if self.attached_to_surface:
                import nc.nc
                nc.nc.creator.set_ocl_cutter(tool.OCLDefinition(self.attached_to_surface))

        self.tool_number = tool_number
        
    def AddTags(self, object):
        Profile.tag_drawing.profile = object
        self.SetInputMode(Profile.tag_drawing)
        
    def RepositionTag(self, object):
        pos = self.PickPosition('Pick New Tag Position')
        object.pos.x = pos.x
        object.pos.y = pos.y
        cad.Repaint()
        
    def ClearUnusedTools(self, program):
        to_delete = []
        used_set = {}
        for op in program.operations.GetChildren():
            used_set[op.tool_number] = True
            
        for tool in program.tools.GetChildren():
            if tool.tool_number not in used_set:
                to_delete.append(tool)
                
        if len(to_delete)>0:
            cad.DeleteObjectsUndoably(to_delete)
            
    def ClearToolpath(self):
        cad.StartHistory('Clear Toolpath')
        blank_nc = NcCode.NcCode()
        cad.PyIncref(blank_nc)
        wx.GetApp().CopyUndoablyWithChildren(wx.GetApp().program.nccode, blank_nc)
        self.EndHistory()
        
    def GetObjectTools(self, object, control_pressed, from_tree_canvas = False):
        tools = SolidApp.GetObjectTools(self, object, control_pressed, from_tree_canvas)
        if object.GetType() == Profile.type:
            tools.append(CamContextTool.CamObjectContextTool(object, "Add Tags", "addtag", self.AddTags))
        if object.GetType() == Tag.type:
            tools.append(CamContextTool.CamObjectContextTool(object, "Pick new position", "tagpos", self.RepositionTag))
        if object.GetType() == Program.type or object.GetType() == Tools.type:
            tools.append(CamContextTool.CamObjectContextTool(self.program, "Clear Unused Tools", "optoolclear", self.ClearUnusedTools))
        if object.GetType() == NcCode.type:
            tools.append(CamContextTool.CamContextTool("Clear Toolpath", "toolpathclear", self.ClearToolpath))        
        if object.GetType() == Stocks.type:
            tools.append(CamContextTool.CamContextTool("New Stock", "stock", self.NewStock2))        
        if object.GetType() == Tools.type:
            tools.append(CamContextTool.CamContextTool("Import Tools", "imptools", self.ImportTools))        
        return tools
    
    def AddExtraMachiningPanels(self, ribbon, page):
        pass

    def AddExtraOtherOperations(self, toolbar):
        pass
        
    def AddExtraRibbonPages(self, ribbon):
        SolidApp.AddExtraRibbonPages(self, ribbon)
        
        save_bitmap_path = self.bitmap_path
        self.bitmap_path = cam_dir + '/bitmaps'

        page = RB.RibbonPage(ribbon, wx.ID_ANY, 'Machining', ribbon.Image('ops'))
        page.Bind(wx.EVT_KEY_DOWN, ribbon.OnKeyDown)

        panel = RB.RibbonPanel(page, wx.ID_ANY, 'Milling', ribbon.Image('ops'))
        toolbar = RB.RibbonButtonBar(panel)
        Ribbon.AddToolBarTool(toolbar, 'Profile', 'opprofile', 'Add a Profile Operation', self.NewProfileOp)
        Ribbon.AddToolBarTool(toolbar, 'Pocket', 'pocket', 'Add a Pocket Operation', self.NewPocketOp)
        Ribbon.AddToolBarTool(toolbar, 'Drilling', 'drilling', 'Add a Drilling Operation', self.NewDrillingOp)
        Ribbon.AddToolBarTool(toolbar, 'Serial Numbers', 'serialnums', 'Add a Serial Numbers Operation', self.NewSerialNums)
        
        self.AddExtraMachiningPanels(ribbon, page)

        panel = RB.RibbonPanel(page, wx.ID_ANY, 'Other Operations', ribbon.Image('ops'))
        toolbar = RB.RibbonButtonBar(panel)
        Ribbon.AddToolBarTool(toolbar, 'Script', 'scriptop', 'Add a Script Operation', self.NewScriptOp)
        Ribbon.AddToolBarTool(toolbar, 'Pattern', 'pattern', 'Add a Pattern', self.NewPattern)
        Ribbon.AddToolBarTool(toolbar, 'Surface', 'surface', 'Add a Surface', self.NewSurface)
        Ribbon.AddToolBarTool(toolbar, 'Stock', 'stock', 'Add a Stock', self.NewStock)
        
        self.AddExtraOtherOperations(toolbar)

        panel = RB.RibbonPanel(page, wx.ID_ANY, 'Tools', ribbon.Image('tools'))
        toolbar = RB.RibbonButtonBar(panel)
        Ribbon.AddToolBarTool(toolbar, 'Drill', 'drill', 'Add a Drill', self.NewDrill)
        Ribbon.AddToolBarTool(toolbar, 'Centre Drill', 'centredrill', 'Add a Centre Drill', self.NewCentreDrill)
        Ribbon.AddToolBarTool(toolbar, 'End Mill', 'endmill', 'Add an End Mill', self.NewEndMill)
        Ribbon.AddToolBarTool(toolbar, 'Slot Drill', 'slotdrill', 'Add a Slot Drill', self.NewSlotDrill)
        Ribbon.AddToolBarTool(toolbar, 'Ball End Mill', 'ballmill', 'Add a Ball Mill', self.NewBallMill)
        Ribbon.AddToolBarTool(toolbar, 'Chamfer Mill', 'chamfmill', 'Add a Chamfer Mill', self.NewChamferMill)

        panel = RB.RibbonPanel(page, wx.ID_ANY, 'G-Code', ribbon.Image('code'))
        toolbar = RB.RibbonButtonBar(panel)
        Ribbon.AddToolBarTool(toolbar, 'Auto Program', 'magic', 'Create Program Automatically', self.OnAutoProgram)
        Ribbon.AddToolBarTool(toolbar, 'Create G-Code', 'postprocess', 'Create G-Code Output File', self.OnCreateGCode)
        Ribbon.AddToolBarTool(toolbar, 'Setup Sheet', 'pdf', 'Create PDF Setup Sheet', self.OnSetupSheet)
        Ribbon.AddToolBarTool(toolbar, 'Open G-Code', 'opennc', 'Open a G-Code File ( to display its tool path )', self.OnOpenGCodeFile)

        page.Realize()

        self.bitmap_path = save_bitmap_path

    def AddExtraWindows(self, frame):
        self.output_window = OutputWindow(frame)
        frame.aui_manager.AddPane(self.output_window, wx.aui.AuiPaneInfo().Name('Output').Caption('Output').Left().Bottom().BestSize(wx.Size(600, 200)))
        self.RegisterHideableWindow(self.output_window, self.cam_dir + '/bitmaps')
        
    def GetSelectedSketches(self):
        sketches = []
        for object in cad.GetSelectedObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_SKETCH:
                sketches.append(object.GetID())
        return sketches
        
    def GetSelectedPoints(self):
        points = []
        for object in cad.GetSelectedObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_POINT:
                points.append(object.GetID())
        return points
    
    def EditAndAddSketchOp(self, new_object, sketches):
        if new_object.Edit():
            cad.StartHistory('Add ' + new_object.GetTitle())
            cad.AddUndoably(new_object, self.program.operations, None)
            
            first = True
            for sketch in sketches:
                if first:
                    first = False
                else:
                    copy = new_object.MakeACopy()
                    copy.sketch = sketch
                    cad.AddUndoably(copy, self.program.operations, None)
            
            self.EndHistory()
    
    def NewProfileOp(self, e):
        sketches = self.GetSelectedSketches()
        sketch = 0
        if len(sketches) > 0: sketch = sketches[0]
        new_object = Profile.Profile(sketch)
        new_object.ReadDefaultValues()
        new_object.SetID(cad.GetNextID(Profile.type))
        new_object.AddMissingChildren()  # add the tags container
        
        self.EditAndAddSketchOp(new_object, sketches)
            
    def NewPocketOp(self, e):
        sketches = self.GetSelectedSketches()
        sketch = 0
        if len(sketches) > 0: sketch = sketches[0]
        new_object = Pocket.Pocket(sketch)
        new_object.ReadDefaultValues()
        new_object.SetID(cad.GetNextID(Pocket.type))
        
        self.EditAndAddSketchOp(new_object, sketches)
        
    def NewSerialNums(self, e):
        new_object = SerialNums.SerialNums()
        new_object.ReadDefaultValues()
        new_object.SetID(cad.GetNextID(SerialNums.type))
        
        self.EditAndAddOp(new_object)
        
    def NewStock2(self):
        self.NewStock(None)
        
    def NewStock(self, e):
        solids = []
        for object in cad.GetSelectedObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_STL_SOLID:
                solids.append(object.GetID())

        new_object = Stock.Stock()
        new_object.solids += solids
        new_object.SetID(cad.GetNextID(Stock.type))
        if new_object.Edit():
            cad.AddUndoably(new_object, self.program.stocks, None)
            self.EndHistory()
            
    def ImportTools(self):
        config = HeeksConfig()
        dialog = wx.FileDialog(self.frame, 'Import Tools', config.Read('ImportToolsDirectory', self.GetDefaultDir()), 'default.tooltable', 'Tool Table files |*.tooltable;*.TOOLTABLE')
        dialog.CenterOnParent()
        
        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetPath()
            res = cad.Import(filepath)
            if res:
                config.Write('ImportToolsDirectory', dialog.GetDirectory())
                self.Repaint()
        
    def EditAndAddOp(self, op):
        if op.Edit():
            cad.StartHistory('Add ' + op.GetTitle())
            cad.AddUndoably(op, op.PreferredPasteTarget(), None)
            self.EndHistory()
            
    def NewDrillingOp(self, e):
        new_object = Drilling.Drilling()
        new_object.ReadDefaultValues()
        new_object.points += self.GetSelectedPoints()
        new_object.SetID(cad.GetNextID(Drilling.type))
        self.EditAndAddOp(new_object)
            
    def NewScriptOp(self, e):
        new_object = ScriptOp.ScriptOp()
        new_object.SetID(cad.GetNextID(ScriptOp.type))
        self.EditAndAddOp(new_object)

    def NewPattern(self, e):
        new_object = Pattern.Pattern()
        new_object.SetID(cad.GetNextID(Pattern.type))
        self.EditAndAddOp(new_object)

    def NewSurface(self, e):
        new_object = Surface.Surface()
        new_object.ReadDefaultValues()
        new_object.SetID(cad.GetNextID(Surface.type))
        self.EditAndAddOp(new_object)

    def EditAndAddTool(self, tool):
        if tool.Edit():
            cad.StartHistory('Add Tool')
            cad.AddUndoably(tool, self.program.tools, None)
            self.EndHistory()
        
    def AddNewTool(self, tool_type):
        # find next available tool number
        max_tool_number = 0
        for object in self.program.tools.GetChildren():
            if object.tool_number > max_tool_number:
                max_tool_number = object.tool_number

        # Add a new tool
        new_object = Tool.Tool(tool_number = max_tool_number + 1, type = tool_type)
        self.EditAndAddTool(new_object)
            
    def NewDrill(self, e):
        self.AddNewTool(Tool.TOOL_TYPE_DRILL)
            
    def NewCentreDrill(self, e):
        self.AddNewTool(Tool.TOOL_TYPE_CENTREDRILL)
            
    def NewEndMill(self, e):
        self.AddNewTool(Tool.TOOL_TYPE_ENDMILL)
            
    def NewSlotDrill(self, e):
        self.AddNewTool(Tool.TOOL_TYPE_SLOTCUTTER)
            
    def NewBallMill(self, e):
        self.AddNewTool(Tool.TOOL_TYPE_BALLENDMILL)
            
    def NewChamferMill(self, e):
        self.AddNewTool(Tool.TOOL_TYPE_CHAMFER)
        
    def OnAutoProgram(self, event):
        if not os.path.isfile('AutoProgram.py'):
            wx.MessageBox('This is a commercial feature. Download it from here. ( website URL to do... )')
            return

        from AutoProgram import AutoProgram
        a = AutoProgram()
        if a.Edit():
            a.Run()
        
    def OnCreateGCode(self, e):
        try:
            self.program.MakeGCode()
            self.program.BackPlot()
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            wx.MessageBox('error during Create G-Code: ' + str(e))
        
        
    def OnSetupSheet(self, e):
        temporary_filepath = str((wx.StandardPaths.Get().GetTempDir() + "/setup_sheet.pdf").replace('\\', '/'))
        self.program.MakeSetupSheet(temporary_filepath)
        import webbrowser
        webbrowser.open_new(temporary_filepath)

    def OnOpenGCodeFile(self, e):
        import wx
        dialog = wx.FileDialog(self.frame, "Open G-Code file", wildcard = "G-Code files" + " |*.*")
        dialog.CentreOnParent()
        
        if dialog.ShowModal() == wx.ID_OK:
            self.program.output_file_name_follows_data_file_name = False
            self.program.output_file = dialog.GetPath()
            self.program.BackPlot()

    def OnViewOutput(self, e):
        pane_info = self.aui_manager.GetPane(self.output_window)
        if pane_info.IsOk():
            pane_info.Show(e.IsChecked())
            self.aui_manager.Update()
        
    def OnUpdateViewOutput(self, e):
        e.Check(self.aui_manager.GetPane(self.output_window).IsShown())
    
    def OnLeftClick(self, event):
        if not event.controlDown:
            # check for nc code block clicked
            if self.select_mode.filter.IsTypeInFilter(cam.GetNcCodeBlockType()):
                mask = cad.Filter()
                mask.AddType(cam.GetNcCodeBlockType())
                objects = cad.ObjectsUnderWindow(cad.IRect(self.select_mode.button_down_point.x, self.select_mode.button_down_point.y), False, True, mask, False)
                if len(objects):
                    block = objects[0]
                    cad.ClearSelection()
                    cad.Select(block)
                    block.__class__ = cam.NcCodeBlock
                    self.output_window.viewport.SelectLine(block.line_number, True)
                    wx.GetApp().frame.graphics_canvas.Refresh()
                    self.output_window.Refresh()
                    return            
                
                program = wx.GetApp().program
                if program != None:
                    nccode = program.nccode
                    if nccode != None:
                        nccode.nc_code.SetHighlightedBlock(None)
        
        # do the default click behaviour
        SolidApp.OnLeftClick(self, event)

        
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
    
if __name__ == "__main__":
    app = CamApp()
    app.MainLoop()