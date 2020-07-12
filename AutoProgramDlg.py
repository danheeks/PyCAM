import wx
from HDialog import control_border

class AutoProgramDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent)
        
        panel = wx.Panel(self, style = wx.TAB_TRAVERSAL)
        
        ok_button = wx.Button(panel, wx.ID_OK, 'OK')
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.SetTitle(wx.GetApp().version_number.replace(' ', '.'))
        
        self.text_ctrl = wx.TextCtrl( panel, size = wx.Size(600, 400), style = wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_AUTO_URL )
        text = 'Copyright Dan Heeks 2020\nOpen source CAD software, source code here:\n'
        text += 'https://github.com/danheeks/PyCAD\n'

        self.text_ctrl.SetValue(text)
        
        main_sizer.Add(self.text_ctrl, 1, wx.ALL | wx.GROW, control_border)
        main_sizer.Add(ok_button, 0, wx.ALL | wx.GROW, control_border)
        
        panel.SetAutoLayout( True )
        panel.SetSizer( main_sizer )
        
        main_sizer.SetSizeHints( self )
        
        ok_button.Bind(wx.EVT_BUTTON, self.OnButtonOK )
        self.text_ctrl.Bind(wx.EVT_TEXT_URL, self.OpenURL)
        
        self.Show( True )
        
    def OnButtonOK(self, event):
        self.EndModal(wx.ID_OK)
        
    def OpenURL(self, event):
        if event.MouseEvent.LeftUp():
            import webbrowser
            url = self.text_ctrl.GetRange(event.GetURLStart(), event.GetURLEnd())
            webbrowser.open_new_tab(url)
        event.Skip()

