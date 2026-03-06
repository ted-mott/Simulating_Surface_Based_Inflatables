import gmsh

gmsh.initialize()


gmsh.model.occ.importShapes("C:/Perimeter.stp")
gmsh.model.occ.synchronize()

# curves = gmsh.model.getEntities(1)
# curve_ids = [c[1] for c in curves]

# wire = gmsh.model.occ.addWire(curve_ids)
# gmsh.model.occ.synchronize()

# gmsh.model.occ.fillet([(1, wire)], 5)
# gmsh.model.occ.synchronize()


print("Open GMSH window? y/n")
GMSHWindow = input()
if GMSHWindow == "y" or GMSHWindow == "Y":
    gmsh.fltk.run()
    #opens up GMSH pop up window

gmsh.finalize()