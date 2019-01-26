from Tools import Tools
from Operations import Operations
from RawMaterial import RawMaterial
from Machine import Machine
from NCCode import NCCode
from CNCConfig import CNCConfig
from consts import *
import wx
from CamObject import CamObject
import cad
from Object import PyProperty

class Program(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        config = CNCConfig()
        self.units = config.ReadFloat("ProgramUnits", 1.0) # set to 25.4 for inches
        self.alternative_machines_file = config.Read("ProgramAlternativeMachinesFile", "")
        self.raw_material = RawMaterial()    #// for material hardness - to determine feeds and speeds.
        machine_name = config.Read("ProgramMachine", "LinuxCNC")
        self.machine = self.GetMachine(machine_name)
        import wx
        default_output_file = str((wx.StandardPaths.Get().GetTempDir() + "/test.tap").replace('\\', '/'))
        self.output_file = config.Read("ProgramOutputFile", default_output_file)  #  // NOTE: Only relevant if the filename does NOT follow the data file's name.
        self.output_file_name_follows_data_file_name = config.ReadBool("OutputFileNameFollowsDataFileName", True) #    // Just change the extension to determine the NC file name
        self.python_program = ""
        self.path_control_mode = config.ReadInt("ProgramPathControlMode", PATH_CONTROL_UNDEFINED)
        self.motion_blending_tolerance = config.ReadFloat("ProgramMotionBlendingTolerance", 0.0001)    # Only valid if m_path_control_mode == eBestPossibleSpeed
        self.naive_cam_tolerance = config.ReadFloat("ProgramNaiveCamTolerance", 0.0001)        # Only valid if m_path_control_mode == eBestPossibleSpeed
        
    def TypeName(self):
        return "Program"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "program"
    
    def CanBeDeleted(self):
        return False
    
    def add_initial_children(self):
        # add tools, operations, etc.
        self.children = []
        self.tools = Tools()
        self.tools.load_default()
        cad.AddUndoably(self.tools, self, None)
        self.operations = Operations()
        cad.AddUndoably(self.operations, self, None)
        self.nccode = NCCode()
        cad.AddUndoably(self.nccode, self, None)
        
    def LanguageCorrection(self):
        '''
        // Language and Windows codepage detection and correction
        #ifndef WIN32
            python << _T("# coding=UTF8\n");
            python << _T("# No troubled Microsoft Windows detected\n");
        #else
            switch((wxLocale::GetSystemLanguage()))
            {
                case wxLANGUAGE_SLOVAK :
                    python << _T("# coding=CP1250\n");
                    python << _T("# Slovak language detected in Microsoft Windows\n");
                    break;
                case wxLANGUAGE_GERMAN:
                case wxLANGUAGE_GERMAN_AUSTRIAN:
                case wxLANGUAGE_GERMAN_BELGIUM:
                case wxLANGUAGE_GERMAN_LIECHTENSTEIN:
                case wxLANGUAGE_GERMAN_LUXEMBOURG:
                case wxLANGUAGE_GERMAN_SWISS  :
                    python << _T("# coding=CP1252\n");
                    python << _T("# German language or it's variant detected in Microsoft Windows\n");
                    break;
                case wxLANGUAGE_FRENCH:
                case wxLANGUAGE_FRENCH_BELGIAN:
                case wxLANGUAGE_FRENCH_CANADIAN:
                case wxLANGUAGE_FRENCH_LUXEMBOURG:
                case wxLANGUAGE_FRENCH_MONACO:
                case wxLANGUAGE_FRENCH_SWISS:
                    python << _T("# coding=CP1252\n");
                    python << _T("# French language or it's variant detected in Microsoft Windows\n");
                    break;
                case wxLANGUAGE_ITALIAN:
                case wxLANGUAGE_ITALIAN_SWISS :
                    python << _T("# coding=CP1252\n");
                    python << _T("#Italian language or it's variant detected in Microsoft Windows\n");
                    break;
                case wxLANGUAGE_ENGLISH:
                case wxLANGUAGE_ENGLISH_UK:
                case wxLANGUAGE_ENGLISH_US:
                case wxLANGUAGE_ENGLISH_AUSTRALIA:
                case wxLANGUAGE_ENGLISH_BELIZE:
                case wxLANGUAGE_ENGLISH_BOTSWANA:
                case wxLANGUAGE_ENGLISH_CANADA:
                case wxLANGUAGE_ENGLISH_CARIBBEAN:
                case wxLANGUAGE_ENGLISH_DENMARK:
                case wxLANGUAGE_ENGLISH_EIRE:
                case wxLANGUAGE_ENGLISH_JAMAICA:
                case wxLANGUAGE_ENGLISH_NEW_ZEALAND:
                case wxLANGUAGE_ENGLISH_PHILIPPINES:
                case wxLANGUAGE_ENGLISH_SOUTH_AFRICA:
                case wxLANGUAGE_ENGLISH_TRINIDAD:
                case wxLANGUAGE_ENGLISH_ZIMBABWE:
                    python << _T("# coding=CP1252\n");
                    python << _T("#English language or it's variant detected in Microsoft Windows\n");
                    break;
                default:
                    python << _T("# coding=CP1252\n");
                    python << _T("#Not supported language detected in Microsoft Windows. Assuming English alphabet\n");
                    break;
            }
        #endif
        '''
        pass
    
    def RewritePythonProgram(self):
        wx.GetApp().program_window.Clear()
        self.python_program = ""

        kurve_module_needed = False
        kurve_funcs_needed = False
        area_module_needed = False
        area_funcs_needed = False

        active_operations = []
        
        for operation in self.operations.children:
            if operation.active:
                active_operations.append(operation)

                if operation.__class__.__name__ == "Profile":
                    kurve_module_needed = True
                    kurve_funcs_needed = True
                elif operation.__class__.__name__ == "Pocket":
                    area_module_needed = True
                    area_funcs_needed = True
                    
        self.LanguageCorrection()

        # add standard stuff at the top
        self.python_program += "import sys\n"
        
        self.python_program += "sys.path.insert(0,'" + wx.GetApp().cam_dir + "')\n"
        self.python_program += "import math\n"

        if kurve_module_needed: self.python_program += "import kurve\n"
        if kurve_funcs_needed: self.python_program += "import kurve_funcs\n"
        if area_module_needed:
            self.python_program += "import area\n"
            self.python_program += "area.set_units(" + str(self.units) + ")\n"
        if area_funcs_needed: self.python_program += "import area_funcs\n"

        # machine general stuff
        self.python_program += "from nc.nc import *\n"

        # specific machine
        if self.machine.file_name == "not found":
            import wx
            wx.MessageBox("Machine name not set")
        else :
            self.python_program += "import nc." + self.machine.file_name + "\n"
            self.python_program += "\n"

        # output file
        self.python_program += "output('" + self.GetOutputFileName() + "')\n"

        # begin program
        self.python_program += "program_begin(123, 'Test program')\n"
        self.python_program += "absolute()\n"
        if self.units > 25.0:
            self.python_program += "imperial()\n"
        else:
            self.python_program += "metric()\n"
        self.python_program += "set_plane(0)\n"
        self.python_program += "\n"

        #self.python_program += self.raw_material.AppendTextToProgram()

        # write the tools setup code.
        for tool in self.tools.children:
            tool.AppendTextToProgram()

        for operation in active_operations:
            operation.AppendTextToProgram()

        self.python_program += "program_end()\n"
        self.python_program += "from nc.nc import creator\n"
        self.python_program += "creator.file_close()\n"
        
        wx.GetApp().program_window.AppendText(self.python_program)
        if len(self.python_program) > len(wx.GetApp().program_window.textCtrl.GetValue()):
            # The python program is longer than the text control object can handle.  The maximum
            # length of the text control objects changes depending on the operating system (and its
            # implementation of wxWidgets).  Rather than showing the truncated program, tell the
            # user that it has been truncated and where to find it.

            import wx
            standard_paths = wx.StandardPaths.Get()
            file_str = (standard_paths.GetTempDir() + "/post.py").replace('\\', '/')

            wx.GetApp().program_window.Clear();
            wx.GetApp().program_window.AppendText("The Python program is too long \n")
            wx.GetApp().program_window.AppendText("to display in this window.\n")
            wx.GetApp().program_window.AppendText("Please edit the python program directly at \n")
            wx.GetApp().program_window.AppendText(file_str)
    
    def GetOutputFileName(self):
        if self.output_file_name_follows_data_file_name == False:
            return self.output_file
        
        filepath = wx.GetApp().cad.GetFileFullPath()
        if filepath == None:
            # The user hasn't assigned a filename yet.  Use the default.
            return self.output_file

        pos = filepath.rfind('.')
        if pos == -1:
            return self.output_file
        
        filepath = filepath[0:pos] + ".tap"
        return filepath
    
    def GetMachines(self):
        machines_file = self.alternative_machines_file
        if machines_file == "":
            machines_file = wx.GetApp().cam_dir + "/nc/machines.xml"
                
        import re
        import xml.etree.ElementTree as ET

        with open(machines_file) as f:
            xml = f.read()
        root = ET.fromstring(re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>")        
        #root = tree.getroot()
        
        machines = []

        for item in root.findall('Machine'):
            machine = Machine()
            machine.post = item.attrib['post']
            machine.reader = item.attrib['reader']
            machine.suffix = item.attrib['suffix']
            machine.description = item.attrib['description']
            machines.append(machine)

        return machines
    
    def GetMachine(self, description):
        machines = self.GetMachines()
        for machine in machines:
            if machine.description == description:
                return machine
        if len(machines):
            return machines[0]
        return None
        
    def Edit(self):
        from wxProgramDlg import ProgramDlg
        import wx
        dlg = ProgramDlg(self)
        return dlg.ShowModal() == wx.ID_OK
    
    def GetProperties(self):
        properties = []
        properties.append(PropertyMachine(self))
        properties.append(PyProperty("output file name follows data file name", "output_file_name_follows_data_file_name", self))
        properties.append(PropertyOutputFile(self))    
        properties.append(PropertyProgramUnits(self))
        properties += CamObject.GetBaseProperties(self)
        return properties
        
    def WriteXML(self):
        cad.SetXmlValue('machine', self.machine.description)
        cad.SetXmlValue('output_file', self.output_file)
        cad.SetXmlValue('output_file_name_follows_data_file_name', str(self.output_file_name_follows_data_file_name))
        cad.SetXmlValue('program', self.python_program)
        cad.SetXmlValue('units', str(self.units))
        cad.SetXmlValue('ProgramPathControlMode', str(self.path_control_mode))
        cad.SetXmlValue('ProgramMotionBlendingTolerance', str(self.motion_blending_tolerance))
        cad.SetXmlValue('ProgramNaiveCamTolerance', str(self.naive_cam_tolerance))
        
class PropertyMachine(cad.Property):
    def __init__(self, program):
        self.program = program
        cad.Property.__init__(self, cad.PROPERTY_TYPE_CHOICE, 'Machine', program)
        self.choices = []
        machines = self.program.GetMachines()
        for machine in machines:
            self.choices.append(machine.description)
        
    def GetType(self):
        return cad.PROPERTY_TYPE_CHOICE
        
    def GetTitle(self):
        # why is this not using base class?
        return 'Machine'
        
    def editable(self):
        # why is this not using base class?
        return True
    
    def SetInt(self, value):
        self.program.machine = self.program.GetMachine(self.choices[value])
    
    def GetChoices(self):
        return self.choices
    
    def GetInt(self):
        index = 0
        for choice in self.choices:
            if choice == self.program.machine.description:
                return index
            index += 1
        return 0
    
class PropertyProgramUnits(cad.Property):
    def __init__(self, program):
        self.program = program
        cad.Property.__init__(self, cad.PROPERTY_TYPE_CHOICE, '', program)
        
    def GetType(self):
        return cad.PROPERTY_TYPE_CHOICE
        
    def GetTitle(self):
        # why is this not using base class?
        return 'units for nc output'
        
    def editable(self):
        # why is this not using base class?
        return True
    
    def SetInt(self, value):
        self.program.units = 25.4 if value == 1 else 1.0
    
    def GetChoices(self):
        return ['mm', 'inch']
    
    def GetInt(self):
        return 1 if self.program.units > 25.0 else 0
    
    
class PropertyPathControlMode(cad.Property):
    def __init__(self, program):
        self.program = program
        cad.Property.__init__(self, cad.PROPERTY_TYPE_CHOICE, '', program)
        
    def GetType(self):
        return cad.PROPERTY_TYPE_CHOICE
        
    def GetTitle(self):
        # why is this not using base class?
        return 'path control mode'
        
    def editable(self):
        # why is this not using base class?
        return True
    
    def SetInt(self, value):
        self.program.path_control_mode = value
    
    def GetChoices(self):
        return ['Exact Path Mode', 'Exact Stop Mode', 'Best Possible Speed', 'Undefined']
    
    def GetInt(self):
        return self.program.path_control_mode
    
    
class PropertyOutputFile(cad.Property):
    def __init__(self, program):
        self.program = program
        cad.Property.__init__(self, cad.PROPERTY_TYPE_FILE, 'output file', program)
        
    def GetType(self):
        return cad.PROPERTY_TYPE_FILE
        
    def GetTitle(self):
        # why is this not using base class?
        return 'output file'
        
    def editable(self):
        # why is this not using base class?
        return True
    
    def GetString(self):
        return self.program.output_file
        
    def SetString(self, value):
        self.program.output_file = str(value)
        

def XMLRead():
    new_object = Program()
    new_object.machine = new_object.GetMachine( cad.GetXmlValue('machine') )
    new_object.output_file = cad.GetXmlValue('output_file')
    new_object.output_file_name_follows_data_file_name = bool(cad.GetXmlValue('output_file'))
    new_object.python_program = cad.GetXmlValue('program')
    new_object.units = float(cad.GetXmlValue('units'))
    new_object.path_control_mode = int(cad.GetXmlValue('ProgramPathControlMode'))
    new_object.motion_blending_tolerance = float(cad.GetXmlValue('ProgramMotionBlendingTolerance'))
    new_object.naive_cam_tolerance = float(cad.GetXmlValue('ProgramNaiveCamTolerance'))
    
    return new_object
        