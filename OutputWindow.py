import wx
from wx import glcanvas
import cam
import cad
import Mouse

class OutputWindow(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent,-1, attribList=[glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24], style = wx.VSCROLL)
        self.viewport = cam.NewNcCodeViewport()
        self.context = glcanvas.GLContext(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.OnScroll)
        self.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.OnScrollRelease)
        self.Bind(wx.EVT_SCROLLWIN_LINEUP, self.OnScrollLineUp)
        self.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self.OnScrollLineDown)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Resize()

    def OnSize(self, event):
       self.Resize()
       event.Skip()
       
    def GetLastLineToScrollTo(self):
        line = self.viewport.GetNumberOfLines() - self.viewport.GetLinesPerPage()
        if line < 0:
            line = 0
        return line

    def OnMouseWheel(self, event):
        x = event.GetWheelRotation()
        if event.controlDown:
            # zoom in or out
            scale = 1.1 if x > 0 else 0.909090909090909
            new_pixels_per_line = self.viewport.GetPixelsPerLine() * scale
            if new_pixels_per_line < 10.0:
                new_pixels_per_line = 10.0
            elif new_pixels_per_line > 150.0:
                new_pixels_per_line = 150.0
                
            old_lines_per_page = self.viewport.GetLinesPerPage()
            
            # set the new scale
            self.viewport.SetPixelsPerLine( new_pixels_per_line )
            
            # move to keep the middle in the middle
            
            new_lines_per_page = self.viewport.GetLinesPerPage()
            lines_shift = (new_lines_per_page - old_lines_per_page) * (float(event.GetY()) / self.viewport.GetHeight())
            self.viewport.SetCurrentLine(self.viewport.GetCurrentLine() - lines_shift)            
            
            if self.viewport.GetCurrentLine() > self.GetLastLineToScrollTo():
                self.viewport.SetCurrentLine(self.GetLastLineToScrollTo())
        else:
            line_number = self.viewport.GetCurrentLine()
            translation = 20 / self.viewport.GetPixelsPerLine()
            if x > 0:
                line_number -= translation
                if line_number < 0: line_number = 0
            else:
                line_number += translation
                last_line = self.GetLastLineToScrollTo()
                if line_number > last_line:
                    line_number = last_line
            self.viewport.SetCurrentLine(line_number)
        self.SetScrollBarToCurrentLine()
        self.Refresh()            

    def OnLeftDown(self, event):
        # select the block clicked on
        line_number = self.viewport.GetCurrentLine() + event.y / self.viewport.GetPixelsPerLine()
        block = self.viewport.GetBlockAtLine(int(line_number))
        cad.ClearSelection()
        cad.Select(block)
        self.viewport.SelectLine(line_number, False)
        wx.GetApp().frame.graphics_canvas.Refresh()
        self.Refresh()
        
    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW

    def Resize(self):
        s = self.GetClientSize()
        self.viewport.SetSize(s.GetWidth(), s.GetHeight())
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        self.viewport.Render()
        self.SwapBuffers()
        
    def SetScrollBarToCurrentLine(self):
        self.SetScrollbar(wx.VERTICAL, self.viewport.GetCurrentLine() * 100, self.viewport.GetLinesPerPage() * 100, self.viewport.GetNumberOfLines() * 100)
        
    def SetNcCodeObject(self, nccode):
        self.viewport.SetNcCode(nccode)
        self.SetScrollBarToCurrentLine()
        
    def OnScroll(self, event):
        fraction = float(event.GetPosition()) * 0.01 / self.viewport.GetNumberOfLines()
        cur_line = float(self.viewport.GetNumberOfLines()) * fraction
        self.viewport.SetCurrentLine(cur_line )
        self.Refresh()
        
    def OnScrollLineUp(self, event):
        pass

    def OnScrollLineDown(self, event):
        pass

    def OnScrollRelease(self, event):
        self.SetScrollBarToCurrentLine()
        