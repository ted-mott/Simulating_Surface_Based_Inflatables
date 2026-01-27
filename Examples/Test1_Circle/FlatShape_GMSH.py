"""
FlatShape_GMSH.py
Using to create a GMSH file that can be used in Abaqus or SOFA
27.01.2026
Ted M
"""

"""
Libraries
"""
import gmsh
import os


"""
Functions
"""
def EmbedCurveInSurface(CurveTagList, SurfaceTag):

        for CurveTag in CurveTagList:
            gmsh.model.mesh.embed(1, CurveTag, 2, SurfaceTag)
    # runs embed curve command in gmsh


"""
Main
"""
if __name__ == "__main__":

    """"Input config"""
    STEP_Folder_Path = "Examples/Test1_Circle/STEP_geometry"
    #Set as the path for folder containing STEP files, retain naming convention for files for this to work


    """Output config"""
    Output_Folder_Path = "Examples/Test1_Circle/MESH_geometry"
    #Set as the path for output files
    Output_Filename = "Test1_Circle.msh"
    #Set end path as .inp for use in Abaqus or .msh for use in SOFA


    gmsh.initialize()
    #initialises GMSH environment
        
    gmsh.clear()
    #clear all previous GMSH geometry


    """Import STEP files"""
    Laser_Weld_Perimeter_Curve = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Laser_Weld_Perimeter.stp"))

    Outer_Laser_Cut_Curve = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Laser_Cut_Curve.stp"))
    
    Laser_Weld_Curves_File = False
    if os.path.exists(os.path.join(STEP_Folder_Path, "Laser_Weld_Curves.stp")):
        Laser_Weld_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Laser_Weld_Curves.stp"))
        Laser_Weld_Curves_File = True
        print("Laser_Weld_Curves.stp found")

    Anchor_Curves_File = False
    if os.path.exists(os.path.join(STEP_Folder_Path, "Anchor_Curves.stp")):
        Anchor_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Anchor_Curves.stp"))
        Anchor_Curves_File = True
        print("Anchor_Curves.stp found")


    """Curve Loops"""
    Laser_Weld_Perimeter_Loop = gmsh.model.occ.addCurveLoop([Laser_Weld_Perimeter_Curve[0][1]])

    Outer_Laser_Cut_Loop = gmsh.model.occ.addCurveLoop([Outer_Laser_Cut_Curve[0][1]])
    #Only one curve expected in Laser_Weld_Perimeter.stp and Laser_Cut_Curve.stp
   
    Anchor_Loop = []
    if Anchor_Curves_File:
        for i in range(0, len(Anchor_Curves)+1):
            i = gmsh.model.occ.addCurveLoop(Anchor_Curves[i][1])
            Anchor_Loop.append(i)
    
    Loops = [Laser_Weld_Perimeter_Loop] + Anchor_Loop + [Outer_Laser_Cut_Loop]
    #First loops define holes in surface, last loop is surface
    
    Outer_Laser_Cut_Surface = gmsh.model.occ.addPlaneSurface(Loops)
    # Create surface between welded perimeter and cutting curve

    Laser_Weld_Surface = gmsh.model.occ.addPlaneSurface([Laser_Weld_Perimeter_Loop])

    Weld_Curves = []
    if(Laser_Weld_Curves_File):
        EmbedCurveInSurface(Weld_Curves, Laser_Weld_Surface)
    # Create Laser weld surface


    



    """
    Outer_Laser_Cut_Surface = gmsh.model.occ.addPlaneSurface([Outer_Laser_Cut_Loop])
    gmsh.model.occ.fragment( [(2, Outer_Laser_Cut_Surface)], [(2, Laser_Weld_Surface)] )
    #Alternative method for cutting out surface
    """


    gmsh.model.occ.synchronize()
    #using open cascade, need to synchronise geometry with GMSH

    gmsh.model.mesh.generate(2)
    #Generate surface mesh

    #gmsh.write(os.path.join(Output_Folder_Path, Output_Filename ))
    #Save gmsh file

    gmsh.fltk.run()
    #opens up GMSH pop up window
        
    gmsh.finalize()
    #end gmsh process