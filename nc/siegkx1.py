################################################################################
# siegkx1.py
#
# Post Processor for the Sieg KX1 machine
# It is just an ISO machine, but I don't want the tool definition lines
#
# Dan Heeks, 5th March 2009

import nc.nc
import nc.iso_modal
import math
import datetime

now = datetime.datetime.now()

################################################################################
class Creator(nc.iso_modal.Creator):

    def __init__(self):
        nc.iso_modal.Creator.__init__(self)
        self.output_tool_definitions = False
        self.output_time_created = True

    def GetTitle(self):
        return 'siegkx1'

nc.nc.creator = Creator()
