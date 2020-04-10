import sys
import os
import wx
import cad
cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../../PyCAD/trunk')
sys.path.append(pycad_dir)

from Frame import Frame # from CAD
import Profile
import Pocket
import Drilling
import ScriptOp
import Stock
from OutputWindow import OutputWindow
from SimControls import SimControls

class CamFrame(Frame):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr):
        Frame.__init__(self, parent, id, pos, size, style, name)
        
    def AddExtraMenus(self):
        save_bitmap_path = self.bitmap_path
        self.bitmap_path = cam_dir + '/bitmaps'
        
        self.AddMenu('&Machining')
        self.AddMenu('Add New Milling Operation', 'ops')        
        self.AddMenuItem('Profile Operation...', self.NewProfileOp, None, 'opprofile')        
        self.AddMenuItem('Pocket Operation...', self.NewPocketOp, None, 'pocket')        
        self.AddMenuItem('Drilling Operation...', self.NewDrillingOp, None, 'drilling')  
        self.EndMenu()      
        self.AddMenu('Add Other Operation', 'ops')        
        self.AddMenuItem('Script Operation...', self.NewScriptOp, None, 'scriptop')        
        self.AddMenuItem('Pattern...', self.NewProfileOp, None, 'pattern')        
        self.AddMenuItem('Surface...', self.NewProfileOp, None, 'surface')        
        self.AddMenuItem('Stock...', self.NewStock, None, 'stock')        
        self.EndMenu()      
        self.AddMenu('Add New Tool', 'tools')        
        self.AddMenuItem('Drill...', self.NewProfileOp, None, 'drill')        
        self.AddMenuItem('Centre Drill...', self.NewProfileOp, None, 'centredrill')        
        self.AddMenuItem('End Mill...', self.NewProfileOp, None, 'endmill')        
        self.AddMenuItem('Slot Drill...', self.NewProfileOp, None, 'slotdrill')        
        self.AddMenuItem('Ball End Mill...', self.NewProfileOp, None, 'ballmill')        
        self.AddMenuItem('Chamfer Mill...', self.NewProfileOp, None, 'chamfmill')        
        self.EndMenu()      
        self.AddMenuItem('Create G-Code', self.PostProcessMenuCallback, None, 'postprocess')        
        self.AddMenuItem('Simulate', self.OnSimulate, None, 'simulate')        
        self.AddMenuItem('Open NC File', self.NewProfileOp, None, 'opennc')        
        self.AddMenuItem('Save NC File As', self.NewProfileOp, None, 'savenc')        
        self.EndMenu()      
        
        self.AddMenuItem('Output', self.OnViewOutput, self.OnUpdateViewOutput, check_item = True, menu = self.window_menu)
        self.AddMenuItem('Simulation Controls', self.OnViewSimControls, self.OnUpdateViewSimControls, check_item = True, menu = self.window_menu)
        
        self.bitmap_path = save_bitmap_path

    def AddExtraWindows(self):
        self.output_window = OutputWindow(self)
        self.aui_manager.AddPane(self.output_window, wx.aui.AuiPaneInfo().Name('Output').Caption('Output').Left().Bottom().BestSize(wx.Size(600, 200)))
        wx.GetApp().RegisterHideableWindow(self.output_window)
        self.sim_controls = SimControls(self)
        self.aui_manager.AddPane(self.sim_controls, wx.aui.AuiPaneInfo().Name('SimControls').Caption('Simulation Controls').Center().Bottom().BestSize(wx.Size(300, 80)))
        wx.GetApp().RegisterHideableWindow(self.sim_controls)
        
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
            cad.StartHistory()
            cad.AddUndoably(new_object, wx.GetApp().program.operations, None)
            
            first = True
            for sketch in sketches:
                if first:
                    first = False
                else:
                    copy = new_object.MakeACopy()
                    copy.sketch = sketch
                    cad.AddUndoably(copy, wx.GetApp().program.operations, None)
            
            cad.EndHistory()
    
    def NewProfileOp(self, e):
        sketches = self.GetSelectedSketches()
        sketch = 0
        if len(sketches) > 0: sketch = sketches[0]
        new_object = Profile.Profile(sketch)
        new_object.SetID(cad.GetNextID(Profile.type))
        new_object.AddMissingChildren()  # add the tags container
        
        self.EditAndAddSketchOp(new_object, sketches)
            
    def NewPocketOp(self, e):
        sketches = self.GetSelectedSketches()
        sketch = 0
        if len(sketches) > 0: sketch = sketches[0]
        new_object = Pocket.Pocket(sketch)
        new_object.SetID(cad.GetNextID(Pocket.type))
        
        self.EditAndAddSketchOp(new_object, sketches)
        
    def NewStock(self, e):
        solids = []
        for object in cad.GetSelectedObjects():
            if object.GetIDGroupType() == cad.OBJECT_TYPE_STL_SOLID:
                solids.append(object.GetID())

        new_object = Stock.Stock()
        new_object.solids += solids
        new_object.SetID(cad.GetNextID(Stock.type))
        if new_object.Edit():
            cad.AddUndoably(new_object, wx.GetApp().program.stocks, None)
            cad.EndHistory()
        
    def EditAndAddOp(self, op):
        if op.Edit():
            cad.StartHistory()
            cad.AddUndoably(op, wx.GetApp().program.operations, None)
            cad.EndHistory()
            
    def NewDrillingOp(self, e):
        new_object = Drilling.Drilling()
        new_object.points += self.GetSelectedPoints()
        new_object.SetID(cad.GetNextID(Drilling.type))
        self.EditAndAddOp(new_object)
            
    def NewScriptOp(self, e):
        new_object = ScriptOp.ScriptOp()
        new_object.SetID(cad.GetNextID(ScriptOp.type))
        self.EditAndAddOp(new_object)

    def on_post_process(self):
        import wx
        wx.MessageBox("post process")
        
    def PostProcessMenuCallback(self, e):
        self.output_window.textCtrl.Clear()
        wx.GetApp().program.MakeGCode()
        wx.GetApp().program.BackPlot()
        
    def OnSimulate(self, e):
        wx.GetApp().program.simulation.Reset()
        self.sim_controls.SetFromSimulation(wx.GetApp().program.simulation)

    def on_open_nc_file(self):
        import wx
        dialog = wx.FileDialog(self.cad.frame, "Open NC file", wildcard = "NC files" + " |*.*")
        dialog.CentreOnParent()
        
        if dialog.ShowModal() == wx.ID_OK:
            from PyProcess import HeeksPyBackplot
            HeeksPyBackplot(dialog.GetPath())
        
    def on_save_nc_file(self):
        import wx
        dialog = wx.FileDialog(self.cad.frame, "Save NC file", wildcard = "NC files" + " |*.*", style = wx.FD_SAVE + wx.FD_OVERWRITE_PROMPT)
        dialog.CentreOnParent()
        
        if dialog.ShowModal() == wx.ID_OK:
            nc_file_str = dialog.GetPath()
            f = open(nc_file_str, "w")
            if f.errors:
                wx.MessageBox("Couldn't open file" + " - " + nc_file_str)
                return
            f.write(self.ouput_window.textCtrl.GetValue())
            
            from PyProcess import HeeksPyPostProcess
            HeeksPyBackplot(dialog.GetPath())

    def OnViewOutput(self, e):
        pane_info = self.aui_manager.GetPane(self.output_window)
        if pane_info.IsOk():
            pane_info.Show(e.IsChecked())
            self.aui_manager.Update()
        
    def OnUpdateViewOutput(self, e):
        e.Check(self.aui_manager.GetPane(self.output_window).IsShown())

    def OnViewSimControls(self, e):
        pane_info = self.aui_manager.GetPane(self.sim_controls)
        if pane_info.IsOk():
            pane_info.Show(e.IsChecked())
            self.aui_manager.Update()
        
    def OnUpdateViewSimControls(self, e):
        e.Check(self.aui_manager.GetPane(self.sim_controls).IsShown())
        
        
