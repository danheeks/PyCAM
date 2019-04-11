import os
import sys

pycam_dir = os.path.dirname(os.path.realpath(__file__))
pycad_dir = os.path.realpath(pycam_dir + '/../../PyCAD/trunk')
 
sys.path.append(pycad_dir)

from CamApp import CamApp
app = CamApp()
app.MainLoop()
