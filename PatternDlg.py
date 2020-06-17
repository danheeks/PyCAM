import wx
import cad
from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import ObjectIdsCtrl
from NiceTextCtrl import LengthCtrl
from Pattern import Pattern
import math
import geom

PATTERN_MARGIN_X = 24
PATTERN_MARGIN_Y = 26

class PatternDlg(HeeksObjDlg):
    def __init__(self, object, title = 'Pattern', add_picture = True):
        HeeksObjDlg.__init__(self, object, title, add_picture)
        
    def AddLeftControls(self):
        # add the controls in one column
        self.txtCopies1 = wx.TextCtrl(self)
        self.MakeLabelAndControl('Number of Copies A', self.txtCopies1).AddToSizer(self.sizerLeft)
        self.lgthXShift1 = LengthCtrl(self)
        self.MakeLabelAndControl("X Shift A", self.lgthXShift1).AddToSizer(self.sizerLeft)
        self.lgthYShift1 = LengthCtrl(self)
        self.MakeLabelAndControl("Y Shift A", self.lgthYShift1).AddToSizer(self.sizerLeft)
        self.txtCopies2 = wx.TextCtrl(self)
        self.MakeLabelAndControl('Number of Copies B', self.txtCopies2).AddToSizer(self.sizerLeft)
        self.lgthXShift2 = LengthCtrl(self)
        self.MakeLabelAndControl("X Shift B", self.lgthXShift2).AddToSizer(self.sizerLeft)
        self.lgthYShift2 = LengthCtrl(self)
        self.MakeLabelAndControl("Y Shift B", self.lgthYShift2).AddToSizer(self.sizerLeft)

    def SetDefaultFocus(self):
        self.txtCopies1.SetFocus()

    def GetDataRaw(self):
        self.object.copies1 = int(self.txtCopies1.GetValue())
        self.object.x_shift1 = self.lgthXShift1.GetValue()
        self.object.y_shift1 = self.lgthYShift1.GetValue()
        self.object.copies2 = int(self.txtCopies2.GetValue())
        self.object.x_shift2 = self.lgthXShift2.GetValue()
        self.object.y_shift2 = self.lgthYShift2.GetValue()

    def SetFromDataRaw(self):
        self.txtCopies1.SetValue(str(self.object.copies1))
        self.lgthXShift1.SetValue(self.object.x_shift1)
        self.lgthYShift1.SetValue(self.object.y_shift1)
        self.txtCopies2.SetValue(str(self.object.copies2))
        self.lgthXShift2.SetValue(self.object.x_shift2)
        self.lgthYShift2.SetValue(self.object.y_shift2)
        
    def DrawPatternShape(self, dc, x, y, original_shape):
        dc.DrawBitmap(self.shape_bitmap if original_shape else self.shape_bitmap2, x -13, y - 16)

    def RedrawBitmap2(self, numA, numB, xshiftA, yshiftA, xshiftB, yshiftB):
        # paint a picture with Draw commands
        bitmap = wx.Bitmap(300,200)
        dc = wx.MemoryDC(bitmap)
        
        # paint background
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawRectangle(0,0,300,200)
        
        #limit numbers for the drawing
        if numA > 20: numA = 20
        if numB > 20: numB = 20
        
        total_x = math.fabs(xshiftA) * numA + math.fabs(xshiftB) * numB
        total_y = math.fabs(yshiftA) * numA + math.fabs(yshiftB) * numB
        
        box = geom.Box3D()
        box.InsertPoint(0,0,0)
        if numA > 0 and numB > 0:
            box.InsertPoint(xshiftA * (numA-1), yshiftA * (numA-1), 0)
            box.InsertPoint(xshiftB * (numB-1), yshiftB * (numB-1), 0)
            box.InsertPoint(xshiftA * (numA-1) + xshiftB * (numB-1), yshiftA * (numA-1) + yshiftB * (numB-1), 0)
        
        with_margins_x = box.Width() + 2*PATTERN_MARGIN_X
        with_margins_y = box.Height() + 2*PATTERN_MARGIN_Y
        
        scale_x = 1000000000.0
        if box.Width() > 0.000000001: 
            scale_x = (300.0 - 2*PATTERN_MARGIN_X)/box.Width()
        scale_y = 1000000000.0
        if box.Height() > 0.000000001:
            scale_y = (200.0 - 2*PATTERN_MARGIN_Y)/box.Height()
            
        # use the smallest scale
        scale = scale_x
        if scale_y < scale: scale = scale_y
        
        ox = -box.MinX()
        oy = -box.MinY()
        
        img = wx.Image(wx.GetApp().cam_dir + '/bitmaps/pattern/shape.png')
        img2 = wx.Image(wx.GetApp().cam_dir + '/bitmaps/pattern/shape2.png')
        
        num = numA
        if numB > num: num = numB
        if num > 5:
            s = (24.0 - num)/19.0
            neww = 26.0 * s
            newh = 31.0 * s
            img.Rescale(neww, newh)
            img2.Rescale(neww, newh)
            
        self.shape_bitmap = wx.Bitmap(img)
        self.shape_bitmap2 = wx.Bitmap(img2)
        
        # draw the pattern
        for j in range(0, numB):
            for i in range(0, numA):
                x = PATTERN_MARGIN_X + (ox + i * xshiftA + j * xshiftB)*scale
                ix = x
                y = PATTERN_MARGIN_Y + (oy + i * yshiftA + j * yshiftB)*scale
                iy = 200 - y
                self.DrawPatternShape(dc, ix, iy, i==0 and j==0)
                
        dc.SelectObject(wx.NullBitmap)
        
        return bitmap
    
    def RedrawBitmap(self):
        copies1 = int(self.txtCopies1.GetValue())
        x_shift1 = float(self.lgthXShift1.GetValue())
        y_shift1 = float(self.lgthYShift1.GetValue())
        copies2 = int(self.txtCopies2.GetValue())
        x_shift2 = float(self.lgthXShift2.GetValue())
        y_shift2 = float(self.lgthYShift2.GetValue())
        return self.RedrawBitmap2(copies1, copies2, x_shift1, y_shift1, x_shift2, y_shift2)
        
    def SetPictureByWindow(self, w):
        self.picture.bitmap = self.RedrawBitmap()
        self.picture.Refresh()
