import gmsh
import os

gmsh.initialize()
#initialises GMSH environment
    
gmsh.clear()
#clear all previous GMSH geometry

STEP__Folder_Path = "Simulating_Surface_Based_Inflatables/Examples/Test1_Circle/STEP_geometry"
#Set as the path for folder containing STEP files

Laser_Weld = gmsh.model.occ.importShapes(os.path.join(STEP__Folder_Path, "Lasere.stp"))
Laser_Cut = gmsh.model.occ.importShapes(os.path.join(STEP__Folder_Path, "Outer_Circle.stp"))
Laser_Cut = gmsh.model.occ.importShapes(os.path.join(STEP__Folder_Path, "Outer_Circle.stp"))
Laser_Cut = gmsh.model.occ.importShapes(os.path.join(STEP__Folder_Path, "Outer_Circle.stp"))


Laser_Weld_Loop = gmsh.model.occ.addCurveLoop(Laser_Weld[0])
Laser_Cut_Loop = gmsh.model.occ.addCurveLoop([2])

Laserz = []

for i in range(3, len(Laser_Cut)+2):
    i = gmsh.model.occ.addCurveLoop([i])
    Laserz.append(i)

print(Laserz)

loops = [Laser_Weld_Loop] + Laserz + [Laser_Cut_Loop]

print(loops)

surf = gmsh.model.occ.addPlaneSurface(loops)
#First loop defines hole in surface




gmsh.model.occ.synchronize()
#using open cascade, need to synchronise geometry with GMSH

gmsh.fltk.run()
#opens up GMSH pop up window
    
gmsh.finalize()
#end gmsh process