import nc.nc
import emc2b

class Creator(emc2b.Creator):
    def __init__(self):
        emc2b.Creator.__init__(self)
        self.fmt = Format(add_leading_zeros = 2, add_trailing_zeros = True, dp_wanted = False)

nc.nc.creator = Creator()

