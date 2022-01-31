import ocl
import math
from nc.nc import *
import tempfile

def STLSurfFromFile(filepath):
    s = ocl.STLSurf()
    ocl.STLReader(filepath, s)
    return s

def cut_path(path, dcf, z1, mat_allowance, mm, units, rapid_to, incremental_rapid_to):
    dcf.setPath(path)
    dcf.setSampling(0.1) # FIXME: this should be adjustable by the (advanced) user
    dcf.run()
    plist = dcf.getCLPoints()
    f = ocl.LineCLFilter()
    f.setTolerance(0.01) # FIXME: this should be adjustable by and advanced user
    for p in plist:
        f.addCLPoint(p)
    f.run()
    plist = f.getCLPoints()
    n = 0
    for p in plist:
       p.z = p.z + mat_allowance
       if n == 0:
          if mm: rapid(p.x, p.y)
          else: rapid(p.x / units, p.y / units)
          rz = rapid_to
          if p.z > z1: rz = p.z + incremental_rapid_to
          if mm:
             rapid(z = rz)
             feed(z = p.z)
          else:
             rapid(z = rz / units)
             feed(z = p.z / units)
       else:
          if mm:
             feed(p.x, p.y, p.z)
          else:
             feed(p.x / units, p.y / units, p.z / units)
       n = n + 1
       
def zigzag( filepath, tool_diameter = 3.0, corner_radius = 0.0, step_over = 1.0, x0= -10.0, x1 = 10.0, y0 = -10.0, y1 = 10.0, direction = 'X', mat_allowance = 0.0, style = 0, clearance = 5.0, rapid_safety_space = 2.0, start_depth = 0.0, step_down = 2.0, final_depth = -10.0, units = 1.0):
   mm = True
   if math.fabs(units)>0.000000001:
      # ocl works in mm, so convert all values to mm
      mm = False
      tool_diameter *= units
      corner_radius *= units
      step_over *= units
      x0 *= units
      x1 *= units
      y0 *= units
      y1 *= units
      mat_allowance *= units
      clearance *= units
      rapid_safety_space *= units
      start_depth *= units
      step_down *= units
      final_depth *= units
      # read the stl file, we know it is an ascii file because HeeksCNC made it
      s = STLSurfFromFile(filepath)
   cutter = ocl.CylCutter(1.0,1.0) # a dummy-cutter for now
   if corner_radius == 0.0:
      cutter = ocl.CylCutter(tool_diameter + mat_allowance, 100.0)
   elif corner_radius > tool_diameter / 2 - 0.000000001:
      cutter = ocl.BallCutter(tool_diameter + mat_allowance, 100.0)
   else:
      cutter = ocl.BullCutter(tool_diameter + mat_allowance, corner_radius, 100.0)
   if final_depth > start_depth:
      raise 'final_depth > start_depth'
   height = start_depth - final_depth
   zsteps = int( height / math.fabs(step_down) + 0.999999 )
   zstep_down = height / zsteps
   incremental_rapid_to = rapid_safety_space - start_depth
   if incremental_rapid_to < 0: incremental_rapid_to = 0.1
   dcf = ocl.PathDropCutter()
   dcf.setSTL(s)
   dcf.setCutter(cutter)
   for k in range(0, zsteps):
      z1 = start_depth - k * zstep_down
      z0 = start_depth - (k + 1) * zstep_down
      dcf.setZ(z0)
      steps = int((y1 - y0)/step_over) + 1
      if direction == 'Y': steps = int((x1 - x0)/step_over) + 1
      sub_step_over = (y1 - y0)/ steps
      if direction == 'Y': sub_step_over = (x1 - x0)/ steps
      rapid_to = z1 + incremental_rapid_to
      path = ocl.Path()
      for i in range(0, steps + 1):
         odd_numbered_pass = (i%2 == 1)
         u = y0 + float(i) * sub_step_over
         if direction == 'Y': u = x0 + float(i) * sub_step_over
         if style == 0: # one way
            if direction == 'Y': path.append(ocl.Line(ocl.Point(u, y0, 0), ocl.Point(u, y1, 0)))
            else: path.append(ocl.Line(ocl.Point(x0, u, 0), ocl.Point(x1, u, 0)))
            cut_path(path, dcf, z1, mat_allowance, mm, units, rapid_to, incremental_rapid_to)
            path = ocl.Path()
            if mm:
               rapid(z = clearance)
            else:
               rapid(z = clearance / units)
               
         else: # back and forth
            if direction == 'Y':
               if odd_numbered_pass:
                  path.append(ocl.Line(ocl.Point(u, y1, 0), ocl.Point(u, y0, 0)))
                  if i < steps: path.append(ocl.Line(ocl.Point(u, y0, 0), ocl.Point(u + sub_step_over, y0, 0))) # feed across to next pass
               else:
                  path.append(ocl.Line(ocl.Point(u, y0, 0), ocl.Point(u, y1, 0)))
                  if i < steps: path.append(ocl.Line(ocl.Point(u, y1, 0), ocl.Point(u + sub_step_over, y1, 0))) # feed across to next pass
            else: # 'X'
               if odd_numbered_pass:
                  path.append(ocl.Line(ocl.Point(x1, u, 0), ocl.Point(x0, u, 0)))
                  if i < steps: path.append(ocl.Line(ocl.Point(x0, u, 0), ocl.Point(x0, u + sub_step_over, 0))) # feed across to next pass
               else:
                  path.append(ocl.Line(ocl.Point(x0, u, 0), ocl.Point(x1, u, 0)))
                  if i < steps: path.append(ocl.Line(ocl.Point(x1, u, 0), ocl.Point(x1, u + sub_step_over, 0))) # feed across to next pass

      if style != 0: # back and forth
         cut_path(path, dcf, z1, mat_allowance, mm, units, rapid_to, incremental_rapid_to)
         if mm:
            rapid(z = clearance)
         else:
            rapid(z = clearance / units)


def cutting_tool( diameter, corner_radius, length ):
   cutter = ocl.CylCutter(1.0, length) # dummy cutter
   if corner_radius == 0.0:
      cutter = ocl.CylCutter(diameter, length)
   elif corner_radius > diameter / 2 - 0.000000001:
      cutter = ocl.BallCutter(diameter, length)
   else:
      cutter = ocl.BullCutter(diameter, corner_radius, length)

   return(cutter)


def waterline( filepath, tool_diameter = 3.0, corner_radius = 0.0, step_over = 1.0, x0= -10.0, x1 = 10.0, y0 = -10.0, y1 = 10.0, mat_allowance = 0.0, clearance = 5.0, rapid_safety_space = 2.0, start_depth = 0.0, step_down = 2.0, final_depth = -10.0, units = 1.0, tolerance = 0.01 ):
   mm = True
   if math.fabs(units)>0.000000001:
      # ocl works in mm, so convert all values to mm
      mm = False
      tool_diameter *= units
      corner_radius *= units
      step_over *= units
      x0 *= units
      x1 *= units
      y0 *= units
      y1 *= units
      mat_allowance *= units
      clearance *= units
      rapid_safety_space *= units
      start_depth *= units
      step_down *= units
      final_depth *= units
      tolerance *= units

   # read the stl file, we know it is an ascii file because HeeksCNC made it
   s = STLSurfFromFile(filepath)

   if final_depth > start_depth:
      raise 'final_depth > start_depth'
   height = start_depth - final_depth
   zsteps = int( height / math.fabs(step_down) + 0.999999 )
   zstep_down = height / zsteps
   incremental_rapid_to = rapid_safety_space - start_depth
   if incremental_rapid_to < 0: incremental_rapid_to = 0.1

   tool_location = ocl.Point(0.0, 0.0, 0.0)

   for k in range(0, zsteps):
      z = start_depth - k * zstep_down
      working_diameter = tool_diameter + mat_allowance

      room_to_expand = True
      # while (room_to_expand == True):
      cutter = cutting_tool(working_diameter, corner_radius, 10)

      waterline = ocl.Waterline()
      waterline.setSTL(s)
      waterline.setSampling(tolerance)
      waterline.setCutter(cutter)
      waterline.setZ(z)
      waterline.run()
      cutter_loops = waterline.getLoops()

      for cutter_loop in cutter_loops:
         if ((cutter_loop[0].z != tool_location.z) or (tool_location.distance(cutter_loop[0]) > (tool_diameter / 2.0))):
            # Move above the starting point.
            rapid(z = clearance / units)
            rapid(x=cutter_loop[0].x, y=cutter_loop[0].y)
            tool_location.x = cutter_loop[0].x
            tool_location.y = cutter_loop[0].y
            tool_location.z = clearance / units

            # Feed down to the cutting depth
            rapid(x=cutter_loop[0].x, y=cutter_loop[0].y)
            tool_location.x = cutter_loop[0].x
            tool_location.y = cutter_loop[0].y

         # Cut around the solid at this level.
         for point in cutter_loop:
            feed( x=point.x, y=point.y, z=point.z )
            tool_location = point;
            #if (point.x < (x0-step_over)) or (point.x > (x1+step_over)) or (point.y < (y0-step_over)) or (point.y > (y1+step_over)):
            #   room_to_expand = False

            # And retract to the clearance height
         rapid(z = clearance / units)
         tool_location.z = clearance / units

         #working_diameter += step_over
