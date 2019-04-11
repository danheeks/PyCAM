from CamObject import CamObject

type = 0

class Surface(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Surface"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "surface"
