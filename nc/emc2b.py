import nc.nc
import nc.iso_modal
import math

class Creator(nc.iso_modal.Creator):
    def __init__(self):
        nc.iso_modal.Creator.__init__(self)
        self.output_block_numbers = False
        self.output_tool_definitions = False
        self.output_g43_on_tool_change_line = True
        self.output_time_created = True
    
    def GetTitle(self):
        return 'emc2b' + ' Cutter Radius Compensation' if self.useCrc else ''

    def SPACE(self):
        if self.start_of_line == True:
            self.start_of_line = False
            return ''
        else:
            return ' '

    def PROGRAM(self): return None
    def PROGRAM_END(self): return( 'T0' + self.SPACE() + 'M06' + self.SPACE() + 'M02')

nc.nc.creator = Creator()

