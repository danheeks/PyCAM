from Object import Object
import os

cam_dir = os.path.dirname(os.path.realpath(__file__))

class CamObject(Object):
    def __init__(self, type = 0):
        Object.__init__(self, type)
        
    def icon(self):
        return "unknown"
    
    def TypeName(self):
        return "Unknown"
    
    def GetTypeString(self):
        return self.TypeName()
        
    def GetIconFilePath(self):
        return cam_dir + '/icons/' + self.icon() + '.png'
    
    def HasColor(self):
        return False
