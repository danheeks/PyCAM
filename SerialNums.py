import geom
import cad
import Tool
import wx
from nc.nc import *
import kurve_funcs
from HeeksConfig import HeeksConfig
import math
from consts import *
from DepthOp import DepthOp
from Object import PyProperty
from Object import PyPropertyLength

type = 0

# SerialNums does everything that Profile does, but ignores the sketch and uses a series of serial numbers instead

class SerialNums(DepthOp):
    def __init__(self):
        DepthOp.__init__(self)
        self.start_number = '' # can have letters but must end in a number, eg. SNZ0001, or 1G3r1
        self.quantity = 0# must be greater than 0, if greater than 1, then number will be incremented, SNZ0001 will become SNZ0002, 1G3r1 will become 1G3r2
        self.height = 0.0# the height in mm of the character '0'

    def TypeName(self):
        return "SerialNums"

    def GetType(self):
        return type

    def op_icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "serialnums"

    def HasEdit(self):
        return True

    def Edit(self):
        import SerialNumsDlg
        res =  SerialNumsDlg.Do(self)
        return res

    def MakeACopy(self):
        copy = SerialNums()
        cad.PyIncref(copy)
        copy.CopyFrom(self)
        return copy

    def CopyFrom(self, object):
        DepthOp.CopyFrom(self, object)
        self.start_number = object.start_number
        self.quantity = object.quantity
        self.height = object.height

    def WriteXml(self):
        cad.SetXmlValue('start_number', self.start_number)
        cad.SetXmlValue('quantity', self.quantity)
        cad.SetXmlValue('height', self.height)
        DepthOp.WriteXml(self)

    def ReadXml(self):
        self.start_number = cad.GetXmlValue('start_number', self.start_number)
        print('self.start_number = ' + self.start_number)
        self.quantity = cad.GetXmlInt('quantity', self.quantity)
        self.height = cad.GetXmlFloat('height', self.height)
        DepthOp.ReadXml(self)

    def ReadDefaultValues(self):
        DepthOp.ReadDefaultValues(self)
        config = HeeksConfig()
        
        self.start_number = config.Read("SerialStart", 'SN0001')
        self.quantity = config.ReadInt("SNQuantity", 1)
        self.height = config.ReadFloat("SNTextHeight", 6.0)

    def WriteDefaultValues(self):
        DepthOp.WriteDefaultValues(self)
        config = HeeksConfig()
        config.Write("SerialStart", self.start_number)
        config.WriteInt("SNQuantity", self.quantity)
        config.WriteFloat("SNTextHeight", self.height)

    def GetProperties(self):
        properties = []

        properties.append(PyProperty("Start Number", 'start_number', self))
        properties.append(PyProperty("Quantity", 'quantity', self))
        properties.append(PyProperty("Text Height", 'height', self))

        properties += DepthOp.GetProperties(self)

        return properties

    def DoGCodeCalls(self):
        if self.quantity < 1:
            raise NameError("Serial Numbers operation must have quantity of at least 1")
        
        # split serial number into end number and preceding text
        first_of_last_numeric = None
        for i in range(len(self.start_number) - 1, -1, -1):
            if self.start_number[i].isnumeric():
                first_of_last_numeric = i
            else:
                break
        if first_of_last_numeric == None:
            raise NameError("can't increment serial number, serial number doesn't end with a number")
            
        precedor = self.start_number[0:first_of_last_numeric]
        number = self.start_number[first_of_last_numeric:]
        number_length = len(number)
        inumber = int(number)
        
        depthparams = self.GetDepthParams()
        
        sm = geom.Matrix()
        sm.Scale(self.height)
        
        from TextCurve import GetTextCurves
        
        for i in range(0, self.quantity):
            wx.GetApp().tool_number = 0 # force a new tool change command for each serial number
            
            DepthOp.DoGCodeCalls(self)
            
            text = precedor
            number = str(inumber)
            for i in range(len(number), number_length):
                text += '0' # add leading zeros
            text += number
            inumber += 1
            
            curves = GetTextCurves(text)
            
            for curve in curves:
                curve.Transform(sm) # scale by text height
                # profile the kurve
                kurve_funcs.profile(curve, depthparams = depthparams)