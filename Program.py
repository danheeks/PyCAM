import Tools
import Operations
import Patterns
import Surfaces
import Stocks
import NcCode
from RawMaterial import RawMaterial
from Machine import Machine
from HeeksConfig import HeeksConfig
from consts import *
import wx
from CamObject import CamObject
import cad
from Object import PyProperty
from nc.nc import *
import Surface
import cam

type = 0

class Program(CamObject):
    def __init__(self):
        CamObject.__init__(self, type)
        config = HeeksConfig()
        self.units = config.ReadFloat("ProgramUnits", 1.0) # set to 25.4 for inches
        self.alternative_machines_file = config.Read("ProgramAlternativeMachinesFile", "")
        self.raw_material = RawMaterial()    #// for material hardness - to determine feeds and speeds.
        machine_name = config.Read("ProgramMachine", "LinuxCNC")
        self.machine = self.GetMachine(machine_name)
        import wx
        default_output_file = str((wx.StandardPaths.Get().GetTempDir() + "/test.tap").replace('\\', '/'))
        self.output_file = config.Read("ProgramOutputFile", default_output_file)  #  // NOTE: Only relevant if the filename does NOT follow the data file's name.
        self.output_file_name_follows_data_file_name = config.ReadBool("OutputFileNameFollowsDataFileName", True) #    // Just change the extension to determine the NC file name
        self.path_control_mode = config.ReadInt("ProgramPathControlMode", PATH_CONTROL_UNDEFINED)
        self.motion_blending_tolerance = config.ReadFloat("ProgramMotionBlendingTolerance", 0.0001)    # Only valid if m_path_control_mode == eBestPossibleSpeed
        self.naive_cam_tolerance = config.ReadFloat("ProgramNaiveCamTolerance", 0.0001)        # Only valid if m_path_control_mode == eBestPossibleSpeed
        self.tools = None
        self.patterns = None
        self.surfaces = None
        self.stocks = None
        self.operations = None
        self.nccode = None
        
    def TypeName(self):
        return "Program"
    
    def GetType(self):
        return type
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "program"
        
    def OneOfAKind(self):
        return True
    
    def CanBeDeleted(self):
        return False
    
    def add_initial_children(self):
        # add tools, operations, etc.
        self.tools = Tools.Tools()
        self.tools.load_default()
        self.Add(self.tools)
        self.patterns = Patterns.Patterns()
        self.Add(self.patterns)
        self.surfaces = Surfaces.Surfaces()
        self.Add(self.surfaces)
        self.stocks = Stocks.Stocks()
        self.Add(self.stocks)
        self.operations = Operations.Operations()
        self.Add(self.operations)
        self.nccode = NcCode.NcCode()
        self.Add(self.nccode)

    def GetOutputFileName(self):
        if self.output_file_name_follows_data_file_name == False:
            return self.output_file
        
        filepath = wx.GetApp().filepath
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
    
    def HasEdit(self):
        return True
        
    def Edit(self):
        from ProgramDlg import ProgramDlg
        import wx
        dlg = ProgramDlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetData()
            return True
        return False
    
    def OnAdded(self, object):
        if object.GetType() == NcCode.type:
            self.nccode = object
    
    def GetProperties(self):
        properties = []
        properties.append(PropertyMachine(self))
        properties.append(PyProperty("output file name follows data file name", "output_file_name_follows_data_file_name", self))
        properties.append(PropertyOutputFile(self))    
        properties.append(PropertyProgramUnits(self))
        properties += CamObject.GetBaseProperties(self)
        return properties
        
    def WriteXml(self):
        cad.SetXmlValue('machine', self.machine.description)
        cad.SetXmlValue('output_file', self.output_file)
        cad.SetXmlValue('output_file_name_follows_data_file_name', self.output_file_name_follows_data_file_name)
        cad.SetXmlValue('units', self.units)
        cad.SetXmlValue('ProgramPathControlMode', self.path_control_mode)
        cad.SetXmlValue('ProgramMotionBlendingTolerance', self.motion_blending_tolerance)
        cad.SetXmlValue('ProgramNaiveCamTolerance', self.naive_cam_tolerance)
        CamObject.WriteXml(self)

    def ReadXml(self):
        self.machine = self.GetMachine( cad.GetXmlValue('machine') )
        self.output_file = cad.GetXmlValue('output_file')
        self.output_file_name_follows_data_file_name = bool(cad.GetXmlValue('output_file'))
        self.units = float(cad.GetXmlValue('units'))
        self.path_control_mode = int(cad.GetXmlValue('ProgramPathControlMode'))
        self.motion_blending_tolerance = float(cad.GetXmlValue('ProgramMotionBlendingTolerance'))
        self.naive_cam_tolerance = float(cad.GetXmlValue('ProgramNaiveCamTolerance'))
        
        CamObject.ReadXml(self)
        
        self.ReloadPointers()
        
    def ReloadPointers(self):
        object = self.GetFirstChild()
        while object:
            if object.GetType() == Tools.type:self.tools = object
            if object.GetType() == Patterns.type:self.patterns = object
            if object.GetType() == Surfaces.type:self.surfaces = object
            if object.GetType() == Stocks.type:self.stocks = object
            if object.GetType() == Operations.type:self.operations = object
            if object.GetType() == NcCode.type:self.nccode = object
            
            object = self.GetNextChild()
                
    def MakeACopy(self):
        copy = Program()
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, o):
        self.units = o.units
        self.alternative_machines_file = o.alternative_machines_file
        self.machine = o.machine
        self.output_file = o.output_file
        self.output_file_name_follows_data_file_name = o.output_file_name_follows_data_file_name
        self.path_control_mode = o.path_control_mode
        self.motion_blending_tolerance = o.motion_blending_tolerance
        self.naive_cam_tolerance = o.naive_cam_tolerance
        CamObject.CopyFrom(self, o)
    
    def AutoExpand(self):
        return True
    
#    def OnRenderTriangles(self):
#        if self.operations:
#            object = self.operations.GetFirstChild()
#            while object:
#                object.OnRenderTriangles()
#                object = self.GetNextChild()

#        if self.nccode:
#            self.nccode.OnRenderTriangles()
    
    def MakeGCode(self):
        wx.GetApp().attached_to_surface = None
        wx.GetApp().number_for_stl_file = 1
        wx.GetApp().tool_number = 0
        
        #exec('import nc.emc2b', globals())
        machine_module = __import__('nc.' + self.machine.post, fromlist = ['dummy'])
        import importlib
        importlib.reload(machine_module)
        output(self.GetOutputFileName())
        program_begin(self.GetID(), self.GetTitle())

        absolute()
        
        if self.units > 25.0:
            imperial()
        else:
            metric()

        set_plane(0)
        
        if self.path_control_mode != PATH_CONTROL_UNDEFINED:
            set_path_control_mode(self.path_control_mode, self.motion_blending_tolerance, self.naive_cam_tolerance)
        
        for tool in self.tools.GetChildren():
            tool.DoGCodeCalls()

        for op in self.operations.GetChildren():
            if op.active:
                # to do          surface = cad.GetObjectFromId(Surface.type, op.surface)
                # to do          if(surface && !surface->m_same_for_each_pattern_position)ApplySurfaceToText(python, surface, surfaces_written);
                # to do          ApplyPatternToText(python, op->m_pattern, patterns_written);
                # to do          if(surface && surface->m_same_for_each_pattern_position)ApplySurfaceToText(python, surface, surfaces_written);
                op.DoGCodeCalls()
                # to do          if(surface && surface->m_same_for_each_pattern_position)python << _T("attach.attach_end()\n");
                # to do          if(op->m_pattern != 0)python << _T("transform.transform_end()\n");
                # to do          if(surface && !surface->m_same_for_each_pattern_position)python << _T("attach.attach_end()\n");
                # to do          theApp.m_attached_to_surface = NULL;
        
        program_end()
        
    def GetBackplotFilePath(self):
        return str((wx.StandardPaths.Get().GetTempDir() + "/backplot.xml").replace('\\', '/'))   
        
    def CreateBackplotFile(self):
        from nc.hxml_writer import HxmlWriter
        machine_module = __import__('nc.' + self.machine.reader, fromlist = ['dummy'])
        parser = machine_module.Parser(HxmlWriter())
        parser.Parse(self.GetOutputFileName())
        
    def BackPlot(self):
        self.CreateBackplotFile()
        cad.Import(self.GetBackplotFilePath(), self)
        cad.Repaint()
        
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
        
