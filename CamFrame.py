import sys
import os
import wx
import cad
cam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(cam_dir + '/../../PyCAD/trunk')
sys.path.append(pycad_dir)

from Frame import Frame # from CAD
import Profile

class CamFrame(Frame):
    def __init__(self, parent, id=-1, title='CAM ( Computer Aided Manufacturing )', pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr):
        Frame.__init__(self, parent, id, title, pos, size, style, name)
        self.program_window = None
        self.output_window = None
        
    def AddExtraMenus(self):
        save_bitmap_path = self.bitmap_path
        self.bitmap_path = cam_dir + '/bitmaps'
        
        self.AddMenu('&Machining')
        self.AddMenu('Add New Milling Operation', 'ops')        
        self.AddMenuItem('Profile Operation...', self.NewProfileOpMenuCallback, None, 'opprofile')        
        self.AddMenuItem('Pocket Operation...', self.NewProfileOpMenuCallback, None, 'drilling')        
        self.AddMenuItem('Drilling Operation...', self.NewProfileOpMenuCallback, None, 'pocket')  
        self.EndMenu()      
        self.AddMenu('Add Other Operation', 'ops')        
        self.AddMenuItem('Script Operation...', self.NewProfileOpMenuCallback, None, 'scriptop')        
        self.AddMenuItem('Pattern...', self.NewProfileOpMenuCallback, None, 'pattern')        
        self.AddMenuItem('Surface...', self.NewProfileOpMenuCallback, None, 'surface')        
        self.AddMenuItem('Stock...', self.NewProfileOpMenuCallback, None, 'stock')        
        self.EndMenu()      
        self.AddMenu('Add New Tool', 'tools')        
        self.AddMenuItem('Drill...', self.NewProfileOpMenuCallback, None, 'drill')        
        self.AddMenuItem('Centre Drill...', self.NewProfileOpMenuCallback, None, 'centredrill')        
        self.AddMenuItem('End Mill...', self.NewProfileOpMenuCallback, None, 'endmill')        
        self.AddMenuItem('Slot Drill...', self.NewProfileOpMenuCallback, None, 'slotdrill')        
        self.AddMenuItem('Ball End Mill...', self.NewProfileOpMenuCallback, None, 'ballmill')        
        self.AddMenuItem('Chamfer Mill...', self.NewProfileOpMenuCallback, None, 'chamfmill')        
        self.EndMenu()      
        self.AddMenuItem('Run Python Script', self.NewProfileOpMenuCallback, None, 'runpython')        
        self.AddMenuItem('Post-Process', self.NewProfileOpMenuCallback, None, 'postprocess')        
        self.AddMenuItem('Simulate', self.NewProfileOpMenuCallback, None, 'simulate')        
        self.AddMenuItem('Open NC File', self.NewProfileOpMenuCallback, None, 'opennc')        
        self.AddMenuItem('Save NC File As', self.NewProfileOpMenuCallback, None, 'savenc')        
        self.EndMenu()      
        
        self.bitmap_path = save_bitmap_path

    def NewProfileOpMenuCallback(self, e):
        
        # to do find selected sketches
        sketch = 0
        new_object = Profile.Profile(sketch)
        #new_object->SetID(heeksCAD->GetNextID(ProfileType));
        #new_object->AddMissingChildren(); // add the tags container
        if new_object.Edit():
            cad.StartHistory()
            cad.AddUndoably(new_object, wx.GetApp().program.operations, None)
            
            # to do, add a copy of the operation for each of the sketches found
            
            cad.EndHistory()

    def on_post_process(self):
        import wx
        wx.MessageBox("post process")
        
    def RunPythonScript(self):
        # clear the output file
        f = open(self.program.GetOutputFileName(), "w")
        f.write("\n")
        f.close()
        
        # Check to see if someone has modified the contents of the
        # program canvas manually.  If so, replace the m_python_program
        # with the edited program.  We don't want to do this without
        # this check since the maximum size of m_textCtrl is sometimes
        # a limitation to the size of the python program.  If the first 'n' characters
        # of m_python_program matches the full contents of the m_textCtrl then
        # it's likely that the text control holds as much of the python program
        # as it can hold but more may still exist in m_python_program.
        text_control_length = self.program_window.textCtrl.GetLastPosition()
        
        if self.program.python_program[0:text_control_length] != self.program_window.textCtrl.GetValue():
            # copy the contents of the program canvas to the string
            self.program.python_program = self.program_window.textCtrl.GetValue()

        from PyProcess import HeeksPyPostProcess
        HeeksPyPostProcess(True)
        
    def on_make_python_script(self):
        self.program.RewritePythonProgram()
        
    def on_run_program_script(self):
        self.RunPythonScript()
        
    def on_post_process(self):
        self.program.RewritePythonProgram(self)
        self.RunPythonScript()

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
        
    def on_cancel_script(self):
        from PyProcess import HeeksPyCancel
        HeeksPyCancel()
        
    def add_menus(self):
        machining_menu = self.cad.addmenu('Machining')
        global heekscnc_path
        print("heekscnc_path = " + str(heekscnc_path))
        AddOperationMenuItems(machining_menu)
        self.cad.add_menu_item(machining_menu, 'Make Program Script', self.on_make_python_script, heekscnc_path + '/bitmaps/python.png')
        self.cad.add_menu_item(machining_menu, 'Run Program Script', self.on_run_program_script, heekscnc_path + '/bitmaps/runpython.png')
        self.cad.add_menu_item(machining_menu, 'Post Process', self.on_post_process, heekscnc_path + '/bitmaps/postprocess.png')
        self.cad.add_menu_item(machining_menu, 'Open NC File', self.on_open_nc_file, heekscnc_path + '/bitmaps/opennc.png')
        self.cad.add_menu_item(machining_menu, 'Save NC File', self.on_save_nc_file, heekscnc_path + '/bitmaps/savenc.png')
        self.cad.add_menu_item(machining_menu, 'Cancel Python Script', self.on_cancel_script, heekscnc_path + '/bitmaps/cancel.png')
        
    def add_windows(self):
        from Tree import Tree
        self.tree = Tree()
        self.tree.Add(self.program)
        self.tree.Refresh()
        if self.widgets == WIDGETS_WX:
            from wxProgramWindow import ProgramWindow
            from wxOutputWindow import OutputWindow
            self.program_window = ProgramWindow(self.cad.frame)
            self.output_window = OutputWindow(self.cad.frame)
            self.cad.add_window(self.program_window)
            self.cad.add_window(self.output_window)
        
    def on_new(self):
        self.add_program_with_children()
        self.tree.Recreate()

    def on_open(self):
        # to do, load the program
        pass

    def on_save(self):
        # to do, save the program
        pass

    def start(self):
        global heekscnc_path
        
        import wx
        import os
        import sys

        full_path_here = os.path.abspath( __file__ )
        full_path_here = full_path_here.replace("\\", "/")
        heekscnc_path = full_path_here
        slash = heekscnc_path.rfind("/")
        print('heekscnc_path = ' + str(heekscnc_path))
        
        if slash != -1:
            heekscnc_path = heekscnc_path[0:slash]
            slash = heekscnc_path.rfind("/")
            if slash != -1: heekscnc_path = heekscnc_path[0:slash]
        print('heekscnc_path = ' + str(heekscnc_path))
        
        self.add_program_with_children()
        self.add_menus()
        self.add_windows()
        self.cad.on_start() 

    def add_program_with_children(self):
        self.program = Program()
        self.program.add_initial_children()
