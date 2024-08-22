################################################################################
# bpmcp.py
#
# Post Processor for MCP's Bridgeport
# It is just an ISO machine, but I don't want the tool definition lines
#
# Dan Heeks, 13th Aug 2024

import nc
import iso_modal
import math

################################################################################
class Creator(iso_modal.Creator):

    def __init__(self):
        iso_modal.Creator.__init__(self)
        self.output_tool_definitions = False
        
#    def PROGRAM_END(self): return( 'M09\nT0' + self.SPACE() + 'M06\nM30')
    
    def spindle(self, s, clockwise):
        self.write('M08\n') # coolant on
        iso_modal.Creator.spindle(self, s, clockwise)

    def tool_change(self, id, newline = True):
        self.write('M09\n') # coolant off
        iso_modal.Creator.tool_change(self, id, newline)
        self.write('G43' + self.SPACE() + 'H' + str(id) + '\n')
            
################################################################################

nc.creator = Creator()
