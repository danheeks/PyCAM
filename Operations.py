from CamObject import CamObject
from Profile import Profile
from Pocket import Pocket

class Operations(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def TypeName(self):
        return "Operations"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "operations"
    
    def CanBeDeleted(self):
        return False
    
def AddOperationMenuItems(CAM_menu):
    wx.GetApp().heekscnc.cad.add_menu_item(CAM_menu, 'Profile Operation', on_profile_operation, HeeksCNC.heekscnc_path + '/bitmaps/opprofile.png')
    wx.GetApp().heekscnc.cad.add_menu_item(CAM_menu, 'Pocket Operation', on_pocket_operation, HeeksCNC.heekscnc_path + '/bitmaps/pocket.png')

def on_profile_operation():
    op = Profile()
    op.ReadDefaultValues()
    op.sketches = heekscnc.cad.get_selected_sketches()
    if op.Edit():
        heekscnc.program.operations.Add(op)
        heekscnc.tree.Add(op)
        heekscnc.tree.Refresh()

def on_pocket_operation():
    op = Pocket()
    op.ReadDefaultValues()
    op.sketches = heekscnc.cad.get_selected_sketches()
    if op.Edit():
        heekscnc.program.operations.Add(op)
        heekscnc.tree.Add(op)
        heekscnc.tree.Refresh()
