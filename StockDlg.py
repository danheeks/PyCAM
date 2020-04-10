import wx
import cad
import Stock
from SolidsDlg import SolidsDlg

class StockDlg(SolidsDlg):
    def __init__(self, object, title = 'Stock'):
        SolidsDlg.__init__(self, object, title)
        
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder(name, 'stock')
        
    def SetPictureByNameAndFolder(self, name, folder):
        if self.picture:
            self.picture.SetPicture(wx.GetApp().cam_dir + '/bitmaps/' + folder + '/' + name + '.png')
        
def Do(object):
    dlg = StockDlg(object)
    while True:
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            dlg.GetData()
            return True
        elif result == dlg.btnSolidsPick.GetId():
            dlg.PickSolids()
        else:
            return False

            
            
            
            
            
            
            
