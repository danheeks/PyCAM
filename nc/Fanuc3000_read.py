import nc.iso_read

class Parser(nc.iso_read.Parser):
    def __init__(self, writer):
        nc.iso_read.Parser.__init__(self, writer)
        
    def eval_float(self, value):
        # there are no decimal places, so divide the number by 1000
        v = nc.iso_read.Parser.eval_float(self, value) * 0.001
        return v