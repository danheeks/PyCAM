from CamObject import CamObject

class Stocks(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def TypeName(self):
        return "Stocks"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "stocks"
    
    def CanBeDeleted(self):
        return False
