import ContextTool
import wx

class CamContextTool(ContextTool.CADContextTool):
    def __init__(self, title, bitmap_name, method):
        ContextTool.CADContextTool.__init__(self, title, bitmap_name, method)
        
    def BitmapPath(self):
        return wx.GetApp().cam_dir + '/bitmaps/'+ self.BitmapName() + '.png'
   

class CamObjectContextTool(CamContextTool):
    def __init__(self, object, title, bitmap_name, method):
        CamContextTool.__init__(self, title, bitmap_name, method)
        self.object = object
        
    def Run(self, event):
        self.method(self.object)
        
     