from SketchOp import SketchOp
import geom
import cad

PROFILE_RIGHT_OR_INSIDE = -1
PROFILE_ON = 0
PROFILE_LEFT_OR_OUTSIDE = 1

PROFILE_CONVENTIONAL = 0
PROFILE_CLIMB = 1

class Profile(SketchOp):
    def __init__(self, sketch, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        SketchOp.__init__(self, sketch, tool_number, operation_type)
        self.tool_on_side = PROFILE_ON
        self.cut_mode = PROFILE_CONVENTIONAL
        self.auto_roll_radius = 2.0
        self.auto_roll_on = True
        self.auto_roll_off = True
        self.roll_on_point = geom.Point3D(0,0,0)
        self.roll_off_point = geom.Point3D(0,0,0)
        self.start_given = False
        self.end_given = False
        self.start = geom.Point3D(0,0,0)
        self.end = geom.Point3D(0,0,0)
        self.extend_at_start = 0.0
        self.extend_at_end = 0.0
        self.lead_in_line_len = 1.0
        self.lead_out_line_len = 1.0
        self.end_beyond_full_profile = False
        self.sort_sketches = True
        self.offset_extra = 0.0
        self.do_finishing_pass = False
        self.only_finishing_pass = False
        self.finishing_h_feed_rate = 0.0
        self.finishing_cut_mode = PROFILE_CONVENTIONAL
        self.finishing_step_down = 1.0
        
    def TypeName(self):
        return "Profile"
    
    def op_icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "profile"

    def get_selected_sketches(self):        
        return 'hi'
    
    def HasEdit(self):
        return True

    def Edit(self):
        import ProfileDlg
        return ProfileDlg.Do(self)
        
    def MakeACopy(self):
        copy = Profile(self.sketch)
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        SketchOp.CopyFrom(self, object)
        self.tool_on_side = object.tool_on_side
        self.cut_mode = object.cut_mode
        self.auto_roll_radius = object.auto_roll_radius
        self.auto_roll_on = object.auto_roll_on
        self.auto_roll_off = object.auto_roll_off
        self.roll_on_point = object.roll_on_point
        self.roll_off_point = object.roll_off_point
        self.start_given = object.start_given
        self.end_given = object.end_given
        self.start = object.start
        self.end = object.end
        self.extend_at_start = object.extend_at_start
        self.extend_at_end = object.extend_at_end
        self.lead_in_line_len = object.lead_in_line_len
        self.lead_out_line_len = object.lead_out_line_len
        self.end_beyond_full_profile = object.end_beyond_full_profile
        self.sort_sketches = object.sort_sketches
        self.offset_extra = object.offset_extra
        self.do_finishing_pass = object.do_finishing_pass
        self.only_finishing_pass = object.only_finishing_pass
        self.finishing_h_feed_rate = object.finishing_h_feed_rate
        self.finishing_cut_mode = object.finishing_cut_mode
        self.finishing_step_down = object.finishing_step_down
                
