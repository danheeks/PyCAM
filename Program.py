import Tools
import Operations
import Patterns
import Surfaces
import Stocks
import NcCode
from Machine import Machine
from HeeksConfig import HeeksConfig
from consts import *
import wx
from CamObject import CamObject
import cad
from Object import PyProperty
from nc.nc import *
import Surface
import Pattern
import cam
import geom
import math

type = 0

class Program(CamObject):
    def __init__(self):
        CamObject.__init__(self, type)
        self.units = 1.0 # set to 25.4 for inches
        self.alternative_machines_file = ""
        self.material = 'Alu Alloy'
        self.machine = self.GetMachine("LinuxCNC")
        import wx
        self.output_file = str((wx.StandardPaths.Get().GetTempDir() + "/test.tap").replace('\\', '/')) #  // NOTE: Only relevant if the filename does NOT follow the data file's name.
        self.output_file_name_follows_data_file_name = True #    // Just change the extension to determine the NC file name
        self.path_control_mode = PATH_CONTROL_UNDEFINED
        self.motion_blending_tolerance = 0.0001   # Only valid if m_path_control_mode == eBestPossibleSpeed
        self.naive_cam_tolerance = 0.0001        # Only valid if m_path_control_mode == eBestPossibleSpeed
        self.add_comments = True
        self.ReadDefaultValues()
        self.tools = None
        self.patterns = None
        self.surfaces = None
        self.stocks = None
        self.operations = None
        self.nccode = None
        
    def ReadDefaultValues(self):
        config = HeeksConfig()
        self.units = config.ReadFloat("ProgramUnits", self.units)
        self.alternative_machines_file = config.Read("ProgramAlternativeMachinesFile", self.alternative_machines_file)
        self.machine = self.GetMachine(config.Read("ProgramMachine", self.machine.description))
        self.output_file = config.Read("ProgramOutputFile", self.output_file)
        self.output_file_name_follows_data_file_name = config.ReadBool("OutputFileNameFollowsDataFileName", self.output_file_name_follows_data_file_name)
        self.path_control_mode = config.ReadInt("ProgramPathControlMode", self.path_control_mode)
        self.motion_blending_tolerance = config.ReadFloat("ProgramMotionBlendingTolerance", self.motion_blending_tolerance)
        self.naive_cam_tolerance = config.ReadFloat("ProgramNaiveCamTolerance", self.naive_cam_tolerance)
        self.add_comments = config.ReadBool('AddCommentsOp', self.add_comments)        
        self.material = config.Read('Material', self.material)        
        
    def WriteDefaultValues(self):
        config = HeeksConfig()
        config.WriteFloat("ProgramUnits", self.units)
        config.Write("ProgramAlternativeMachinesFile", self.alternative_machines_file)
        config.Write("ProgramMachine", self.machine.description)
        config.Write("ProgramOutputFile", self.output_file)
        config.WriteBool("OutputFileNameFollowsDataFileName", self.output_file_name_follows_data_file_name)
        config.WriteInt("ProgramPathControlMode", self.path_control_mode)
        config.WriteFloat("ProgramMotionBlendingTolerance", self.motion_blending_tolerance)
        config.WriteFloat("ProgramNaiveCamTolerance", self.naive_cam_tolerance)
        config.WriteBool('AddCommentsOp', self.add_comments)
        config.Write('Material', self.material)
        
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
    
    def CallsObjListReadXml(self):
        return True
    
    def add_initial_children(self):
        # add tools, operations, etc.
        if self.tools == None:
            self.tools = Tools.Tools()
            self.tools.load_default()
            self.Add(self.tools)

        if self.patterns == None:
            self.patterns = Patterns.Patterns()
            self.Add(self.patterns)
            
        if self.surfaces == None:
            self.surfaces = Surfaces.Surfaces()
            self.Add(self.surfaces)
            
        if self.stocks == None:
            self.stocks = Stocks.Stocks()
            self.Add(self.stocks)
            
        if self.operations == None:
            self.operations = Operations.Operations()
            self.Add(self.operations)
            
        if self.nccode == None:
            self.nccode = NcCode.NcCode()
            self.Add(self.nccode)
            
#        if self.simulation == None:
#            self.simulation = Simulation.Simulation()
#            self.Add(self.simulation)

    def GetOutputFileName(self):
        if self.output_file_name_follows_data_file_name == False:
            return self.output_file
        
        filepath = wx.GetApp().filepath

        if filepath == None:
            # The user hasn't assigned a filename yet.  Use the default.
            return self.output_file
        
        pos = filepath.rfind('.')
        
        filepath = filepath[0:pos] + self.machine.suffix
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
#        if object.GetType() == Simulation.type:
#            self.simulation = object
    
    def GetProperties(self):
        properties = []
        properties.append(PropertyMachine(self))
        properties.append(PyProperty("output file name follows data file name", "output_file_name_follows_data_file_name", self))
        properties.append(PropertyOutputFile(self))    
        properties.append(PropertyProgramUnits(self))
        properties.append(PyProperty("add comments", "add_comments", self))
        properties.append(PyProperty("material", "material", self))
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
        cad.SetXmlValue('AddComments', self.add_comments)
        cad.SetXmlValue('Material', self.material)
        CamObject.WriteXml(self)

    def ReadXml(self):
        self.machine = self.GetMachine( cad.GetXmlValue('machine') )
        self.output_file = cad.GetXmlValue('output_file')
        self.output_file_name_follows_data_file_name = cad.GetXmlBool('output_file_name_follows_data_file_name')
        self.units = cad.GetXmlFloat('units')
        self.path_control_mode = cad.GetXmlInt('ProgramPathControlMode')
        self.motion_blending_tolerance = cad.GetXmlFloat('ProgramMotionBlendingTolerance')
        self.naive_cam_tolerance = cad.GetXmlFloat('ProgramNaiveCamTolerance')
        self.add_comments = cad.GetXmlBool('AddComments')
        self.material = cad.GetXmlValue('Material', self.material)        
        
        CamObject.ReadXml(self)
        
        self.ReloadPointers()
        
        self.add_initial_children() # add any missing children
        
    def ReloadPointers(self):
        object = self.GetFirstChild()
        while object:
            if object.GetType() == Tools.type:self.tools = object
            if object.GetType() == Patterns.type:self.patterns = object
            if object.GetType() == Surfaces.type:self.surfaces = object
            if object.GetType() == Stocks.type:self.stocks = object
            if object.GetType() == Operations.type:self.operations = object
            if object.GetType() == NcCode.type:self.nccode = object
#            if object.GetType() == Simulation.type:self.simulation = object
            
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

    def ApplyPatternToText(self, p, patterns_written):
        pattern = cad.GetObjectFromId(Pattern.type, p)
        if pattern != None:
            # write a transform redirector
            import transform
            transform.transform_begin(pattern.GetMatrices())
            return True
        return False

    def ApplySurfaceToText(self, surface, surfaces_written):
        if not surface in surfaces_written:
            surfaces_written[surface] = True
            
            tris = geom.Stl()
            
            for solid in surface.solids:
                o = cad.GetObjectFromId(cad.OBJECT_TYPE_STL_SOLID, solid)
                tris += o.GetTris(surface.tolerance)

            # name the stl file
            import tempfile
            temp_filename = tempfile.gettempdir()+'/surface%d.stl' % self.number_for_stl_file
            self.number_for_stl_file += 1
    
            # write stl file
            tris.WriteStl(temp_filename)
            
            import attach
            import ocl_funcs
            
            attach.units = self.units
            attach.attach_begin()
            import nc.nc
            nc.nc.creator.stl = ocl_funcs.STLSurfFromFile(temp_filename)
            nc.nc.creator.minz = -10000.0
            nc.nc.creator.material_allowance = surface.material_allowance

        wx.GetApp().attached_to_surface = surface
    
    def AddComments(self):
        multiple = False
        box = None
        if self.stocks.GetNumChildren() == 1:
            stock = self.stocks.GetFirstChild()
            if len(stock.solids) > 1:
                multiple = True
            else:
                object = cad.GetObjectFromId(cad.OBJECT_TYPE_STL_SOLID, stock.solids[0])
                box = object.GetBox()
                comment(str(box.Width()) + "mm x " + str(box.Height()) + "mm x " + str(box.Depth()) + "mm " + self.material)
        elif self.stocks.GetNumChildren() > 1:
            multiple = True
        else:
            comment('no stock has been defined')
        if multiple:
            comment('multiple stocks were defined')
                    
        # list tools
        for object in self.tools.GetChildren():
            comment('T' + str(object.tool_number) + " " + object.GetTitle())

        if box != None:         
            comment('X0 Y0 at bottom left')    
            comment('or X' + str(box.Width() * 0.5) + " Y" + str(box.Height() * 0.5) + ' in middle')
            if math.fabs(box.MaxZ()) < 0.001: 
                comment('Z0 on top of metal')    
                comment(' ')    

    def MakeGCode(self):
        wx.GetApp().attached_to_surface = None
        self.number_for_stl_file = 1
        wx.GetApp().tool_number = 0

        # import the relevant machine        
        machine_module = __import__('nc.' + self.machine.post, fromlist = ['dummy'])
        import importlib
        importlib.reload(machine_module)
        output(self.GetOutputFileName())
        program_begin(self.GetID(), self.GetTitle())

        if self.add_comments:
            self.AddComments()

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
            
        surfaces_written = {}
        patterns_written = {}

        for op in self.operations.GetChildren():
            if op.active:
                surface = cad.GetObjectFromId(Surface.type, op.surface)
                if surface != None: import attach
                surface_apply_before_pattern = (surface != None) and not surface.same_for_each_pattern_position 
                surface_apply_after_pattern = (surface != None) and surface.same_for_each_pattern_position 
                if surface_apply_before_pattern: self.ApplySurfaceToText(surface, surfaces_written)
                tranform_begun = self.ApplyPatternToText(op.pattern, patterns_written)
                if surface_apply_after_pattern: self.ApplySurfaceToText(surface, surfaces_written)
                failure = op.DoGCodeCalls()
                if surface_apply_after_pattern: attach.attach_end()
                if tranform_begun: transform.transform_end()
                if surface_apply_before_pattern: attach.attach_end()
                wx.GetApp().attached_to_surface = None
                if failure:
                    wx.MessageBox(failure)
                    cad.Select(op)
                    return
        
        program_end()
        
    def BackPlot(self):
        from NcCode import NcCodeWriter        
        machine_module = __import__('nc.' + self.machine.reader, fromlist = ['dummy'])
        parser = machine_module.Parser(NcCode.NcCodeWriter(self.nccode))
        self.nccode.Clear()
        parser.Parse(self.GetOutputFileName())
        wx.GetApp().output_window.SetNcCodeObject(self.nccode.nc_code)
        cad.Repaint()
        
    def MakeSetupSheet(self, pdf_file_path):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, mm
        from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
         
        doc = SimpleDocTemplate(pdf_file_path, pagesize=A4)
        doc.title = 'Setup Sheet'
        # container for the 'Flowable' objects
        elements = []
         
        styles = getSampleStyleSheet()
        
        # strip path from output file
        filename = self.GetOutputFileName()
        filename = filename.replace('\\', '/')
        pos = filename.rfind('/')
        filename = filename[pos+1:]
        
        elements.append(Paragraph('Setup Sheet for ' + filename, styles['Title']))
        
        box = wx.GetApp().program.stocks.GetBoxWithInvisibles()

        elements.append(Paragraph('Stock', styles['Heading2']))
        elements.append(Paragraph('Width(X) = ' + '{:.1f}'.format(box.Width()) + 'mm' , styles['Normal']))
        elements.append(Paragraph('Height(Y) = ' + '{:.1f}'.format(box.Height()) + 'mm' , styles['Normal']))
        elements.append(Paragraph('Thickness(Z) = ' + '{:.1f}'.format(box.Depth()) + 'mm' , styles['Normal']))

        elements.append(Paragraph('Tools', styles['Heading2']))
        for tool in self.tools.GetChildren():
            elements.append(Paragraph('T' + str(tool.tool_number) + ' ' + tool.GetTitle(), styles['Normal']))

        elements.append(Paragraph('Tool Changes', styles['Heading2']))
        elements.append(Paragraph('to do with program.nc_code', styles['Normal']))
        
        # write the document to disk
        doc.build(elements)  

        
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
        
