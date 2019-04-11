from CamObject import CamObject

type = 0

class Patterns(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def TypeName(self):
        return "Patterns"
    
    def GetType(self):
        return type
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "patterns"
    
    def CanBeDeleted(self):
        return False
