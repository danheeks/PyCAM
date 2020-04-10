import wx
import math

class SimControls(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent )
        self.simulation = None

        sizer = wx.BoxSizer()
        self.play_button = wx.BitmapButton(self, bitmap = wx.Bitmap('bitmaps/play.png'))
        self.pause_button = wx.BitmapButton(self, bitmap = wx.Bitmap('bitmaps/pause.png'))
        self.reset_button = wx.BitmapButton(self, bitmap = wx.Bitmap('bitmaps/reset.png'))
        self.view_reset_button = wx.BitmapButton(self, bitmap = wx.Bitmap('bitmaps/view_reset.png'))
        
        self.play_button.SetBitmapDisabled(wx.Bitmap('bitmaps/play_d.png'))
        self.pause_button.SetBitmapDisabled(wx.Bitmap('bitmaps/pause_d.png'))
        self.reset_button.SetBitmapDisabled(wx.Bitmap('bitmaps/reset_d.png'))
        
        button_sizer = wx.BoxSizer()
        button_sizer.Add(self.play_button)
        button_sizer.Add(self.pause_button)
        button_sizer.Add(self.reset_button)
        button_sizer.Add(self.view_reset_button)
        
        self.SpeedLabel = wx.StaticText(self, label = 'mm per second')
        self.SpeedEdit = wx.TextCtrl(self)
        
        speed_text_sizer = wx.BoxSizer()
        speed_text_sizer.Add(self.SpeedLabel)
        speed_text_sizer.Add(self.SpeedEdit)
        
        self.SpeedSlider = wx.Slider(self, value = 0, minValue = 0.0, maxValue = 100.0)
        
        speed_sizer = wx.BoxSizer(wx.VERTICAL)
        speed_sizer.Add(speed_text_sizer)
        speed_sizer.Add(self.SpeedSlider)        
        
        sizer.Add(speed_sizer)
        sizer.Add(button_sizer)
        
        #mark all controls as disabled until a simulation object has been set
        self.play_button.Enable(False)
        self.pause_button.Enable(False)
        self.reset_button.Enable(False)
        self.view_reset_button.Enable(False)
        self.SpeedLabel.Enable(False)
        self.SpeedEdit.Enable(False)
        self.SpeedSlider.Enable(False)

        self.Bind(wx.EVT_TEXT, self.OnSpeedEdit, self.SpeedEdit)
        self.Bind(wx.EVT_SLIDER, self.OnSpeedSlider, self.SpeedSlider)
        self.Bind(wx.EVT_BUTTON, self.OnPlayButton, self.play_button)
        self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pause_button)
        self.Bind(wx.EVT_BUTTON, self.OnResetButton, self.reset_button)
        self.Bind(wx.EVT_BUTTON, self.OnViewResetButton, self.view_reset_button)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizer)

        sizer.SetSizeHints(self)
        sizer.Layout()
        sizer.SetSizeHints(self)
        
    def SetFromSimulation(self, simulation):
        self.simulation = simulation
        self.SpeedEdit.SetValue(str(self.simulation.mm_per_sec))
        self.SpeedSlider.SetValue(math.sqrt(self.simulation.mm_per_sec))
        self.play_button.Enable(True)
        self.pause_button.Enable(False)
        self.reset_button.Enable(False)
        self.view_reset_button.Enable(True)
        self.SpeedLabel.Enable(True)
        self.SpeedEdit.Enable(True)
        self.SpeedSlider.Enable(True)
        
    def OnSpeedSlider(self, event):
        self.simulation.mm_per_sec = math.pow(self.SpeedSlider.GetValue(), 2)
        self.SpeedEdit.SetValue(str(self.simulation.mm_per_sec))
        
    def OnSpeedEdit(self, event):
        self.simulation.mm_per_sec = float(self.SpeedEdit.GetValue())
        self.SpeedSlider.SetValue(math.sqrt(self.simulation.mm_per_sec))

    def OnPlayButton(self, event):
        self.simulation.running = True
        self.pause_button.Enable(True)
        self.reset_button.Enable(True)
        self.play_button.Enable(False)
        
    def OnPauseButton(self, event):
        self.simulation.running = False
        self.pause_button.Enable(False)
        self.play_button.Enable(True)
        
    def OnResetButton(self, event):
        self.pause_button.Enable(False)
        self.play_button.Enable(True)
        self.reset_button.Enable(False)
        self.simulation.OnReset()
         
    def OnViewResetButton(self, event):
        self.simulation.OnViewReset()
        