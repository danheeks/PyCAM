from Operation import Operation
from HeeksConfig import HeeksConfig
import cad
from nc.nc import *
import wx
from Object import PyProperty
from Object import PyPropertyLength

ABS_MODE_ABSOLUTE = 1
ABS_MODE_INCREMENTAL = 2

class SpeedOp(Operation):
    def __init__(self):
        Operation.__init__(self)
        self.horizontal_feed_rate = 200.0
        self.vertical_feed_rate = 50.0
        self.spindle_speed = 7000.0
        
    def ReadDefaultValues(self):
        Operation.ReadDefaultValues(self)
        config = HeeksConfig()
        self.horizontal_feed_rate = config.ReadFloat("SpeedOpHFeedrate", 200.0)
        self.vertical_feed_rate = config.ReadFloat("SpeedOpVFeedrate", 50.0)
        self.spindle_speed = config.ReadFloat("SpeedOpSpindleSpeed", 7000.0)

    def WriteDefaultValues(self):
        Operation.WriteDefaultValues(self)
        config = HeeksConfig()
        config.WriteFloat("SpeedOpHFeedrate", self.horizontal_feed_rate)
        config.WriteFloat("SpeedOpVFeedrate", self.vertical_feed_rate)
        config.WriteFloat("SpeedOpSpindleSpeed", self.spindle_speed)
        
    def AppendTextToProgram(self):
        Operation.AppendTextToProgram(self)

        if self.spindle_speed != 0.0:
            wx.GetApp().program.python_program += "spindle(" + str(self.spindle_speed) + ")\n"

        wx.GetApp().program.python_program += "feedrate_hv(" + str(self.horizontal_feed_rate / wx.GetApp().program.units) + ", "
        wx.GetApp().program.python_program += str(self.vertical_feed_rate / wx.GetApp().program.units) + ")\n"
        wx.GetApp().program.python_program += "flush_nc()\n"

    def CopyFrom(self, object):
        Operation.CopyFrom(self, object)
        self.horizontal_feed_rate = object.horizontal_feed_rate
        self.vertical_feed_rate = object.vertical_feed_rate
        self.spindle_speed = object.spindle_speed
        
    def WriteXml(self):
        cad.BeginXmlChild('speedop')
        cad.SetXmlValue('hfeed', self.horizontal_feed_rate)
        cad.SetXmlValue('vfeed', self.vertical_feed_rate)
        cad.SetXmlValue('spin', self.spindle_speed)
        cad.EndXmlChild()
        Operation.WriteXml(self)
        
    def ReadXml(self):
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'speedop':
                self.horizontal_feed_rate = cad.GetXmlFloat('hfeed', self.horizontal_feed_rate)
                self.vertical_feed_rate = cad.GetXmlFloat('vfeed', self.vertical_feed_rate)
                self.spindle_speed = cad.GetXmlFloat('spin', self.spindle_speed)
            child_element = cad.GetNextXmlChild()
        Operation.ReadXml(self)
            
    def GetProperties(self):
        properties = []

        properties.append(PyPropertyLength("Horizontal Feed Rate", 'horizontal_feed_rate', self))
        properties.append(PyPropertyLength("Vertical Feed Rate", 'vertical_feed_rate', self))
        properties.append(PyProperty("Spindle Speed", 'spindle_speed', self))
        
        properties += Operation.GetProperties(self)

        return properties
            
    def DoGCodeCalls(self):
        Operation.DoGCodeCalls(self)
        if self.spindle_speed != 0:
            spindle(self.spindle_speed)
        feedrate_hv(self.horizontal_feed_rate / wx.GetApp().program.units, self.vertical_feed_rate / wx.GetApp().program.units)
        flush_nc()
