from CamObject import CamObject

class Surfaces(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def TypeName(self):
        return "Surfaces"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "surfaces"
    
    def CanBeDeleted(self):
        return False
