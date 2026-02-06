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
def EmbedCurveInSurface(Curve_List, Surface):
    gmsh.model.occ.synchronize()

    for Curve in Curve_List:
        gmsh.model.mesh.embed(1, [Curve], 2, Surface)
        
        # runs embed curve command in gmsh


def UI_Set_Variable(variable, variable_Name, Default_Setting):
    if Default_Setting:
        return(variable)
    
    #UI to set variables
    print(variable_Name + ": " , variable, "\nWould you like to change this?  y/n" )
    Change_Variable = input()
    if Change_Variable  == "y" or Change_Variable == "Y":
        print("Input New " + variable_Name + ": ")
        variable = input()
        print("New " + variable_Name + ": " , variable)

    return(variable)
    

def Curve_Loop_Generator(Curve_List):
    Closed_Loop_List = []
    Open_Loop_List = []

    for i in range(0, len(Curve_List)):
        
        Curve_id = Curve_List[i][1]

        try:
            Curve_id =(gmsh.model.occ.addCurveLoop([Curve_id]))
            Closed_Loop_List.append(Curve_id)
            print("Curve ", Curve_id, " is closed")

            #Surface_id = gmsh.model.occ.addPlaneSurface([Curve_Loop_id])
            #Surface_List.append(Surface_id)
            #Try to make surfaces to see if curve loops are closed
            
        except:
            Open_Loop_List.append(Curve_id)
            print("Curve ", Curve_id, " is open")


    return(Closed_Loop_List, Open_Loop_List)

    
"""
Main
"""
if __name__ == "__main__":

    """"Input config"""

    Default_Setting = True

    # print("Use Default Settings? y/n")
    # Default_Option = input()
    # if Default_Option == "n" or Default_Option == "N":
    #     Default_Setting = False
    # #Default Setting added to save having to input over and over again


    STEP_Folder_Path = "Examples\Test1_Circle\STEP_geometry"
    #Default path defined here
   
    STEP_Folder_Path = UI_Set_Variable(STEP_Folder_Path, "STEP Folder Path", Default_Setting)
    #UI asks if you want to change this

    gmsh.initialize()
    #initialises GMSH environment
        
    gmsh.clear()
    #clear all previous GMSH geometry

    gmsh.model.add("FlatShape_GMSH")

    print(os.path.join(STEP_Folder_Path, "Laser_Weld_Perimeter.stp"))

    """Import STEP files"""
    Inflated_Surface_Perimeter_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Laser_Weld_Perimeter.stp"))

    

    Outer_Cut_Curve = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Laser_Cut_Curve.stp"))
    
    Coincident_Curves = None
    if os.path.exists(os.path.join(STEP_Folder_Path, "Laser_Weld_Curves_2.stp")):
         Coincident_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Laser_Weld_Curves_2.stp"))
         print("Laser_Weld_Curves.stp found")
    
    Anchor_Curves = None
    if os.path.exists(os.path.join(STEP_Folder_Path, "Anchor_Curves.stp")):
        Anchor_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Anchor_Curves.stp"))
        print("Anchor_Curves.stp found")
    #Laser weld perimeter and Outer laser curve are the only expected files


    """Curve Loops"""
    Inflated_Surface_Perimeter_Loop = gmsh.model.occ.addCurveLoop([Inflated_Surface_Perimeter_Curves[0][1]])
    Outer_Cut_Loop = gmsh.model.occ.addCurveLoop([Outer_Cut_Curve[0][1]])
    #Only one curve expected in Laser_Weld_Perimeter.stp and Laser_Cut_Curve.stp
    
    Outer_Cut_Surface_Loops = [Inflated_Surface_Perimeter_Loop] + [Outer_Cut_Loop]
    #First loops define holes in surface, last loop is surface

    if Anchor_Curves:
        Anchor_Curves_Closed, Anchor_Curves_Open = Curve_Loop_Generator(Anchor_Curves)
        #Curve_Loop_Generator(Curve_List), return(Closed_Loop_List, Open_Loop_List)

        Outer_Cut_Surface_Loops = [Inflated_Surface_Perimeter_Loop] + Anchor_Curves_Closed + [Outer_Cut_Loop]
        #First loops define holes in surface, last loop is surface
    
    Inflated_Surface_Loops = [Inflated_Surface_Perimeter_Loop]

    if Coincident_Curves:
        Coincident_Curves_Closed, Coincident_Curves_Open = Curve_Loop_Generator(Coincident_Curves)
        if Coincident_Curves_Closed:
            Inflated_Surface_Loops = Coincident_Curves_Closed + [Inflated_Surface_Perimeter_Loop]
    

    """Surfaces"""

    Outer_Cut_Surface = gmsh.model.occ.addPlaneSurface(Outer_Cut_Surface_Loops)
    # Create surface between welded perimeter and cutting curve
    
    Inflated_Surface = gmsh.model.occ.addPlaneSurface(Inflated_Surface_Loops)

    Coincident_Surfaces = []
    for Coincident_Surface_Loop in Coincident_Curves_Closed:
        Coincident_Surface = gmsh.model.occ.addPlaneSurface([Coincident_Surface_Loop])
        Coincident_Surfaces.append(Coincident_Surface)

    print(Coincident_Curves_Open)
    EmbedCurveInSurface(Coincident_Curves_Open, Inflated_Surface)
    #EmbedCurveInSurface(Curve_List, Surface)



    """Set Physical Groups"""




    """Mesh Element Length"""
    lc = 4.0
    #Default Global element size
    lc = UI_Set_Variable(lc, "Global Element Size", Default_Setting)
    #User input for global element size

    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)
    #set Global element size


    #Physical groups


    """
    Outer_Laser_Cut_Surface = gmsh.model.occ.addPlaneSurface([Outer_Laser_Cut_Loop])
    gmsh.model.occ.fragment( [(2, Outer_Laser_Cut_Surface)], [(2, Laser_Weld_Surface)] )
    #Alternative method for cutting out surface
    """
    gmsh.model.occ.synchronize()
    #using open cascade, need to synchronise geometry with GMSH


    """Meshing"""
    print("Set Mesh ELement Type Quad(q) or Tri(t)? \n*Tri required for use with SOFA")
    element_type = input()
    
    if element_type == "q" or element_type == "Q":
        try:
            gmsh.option.setNumber("Mesh.RecombineAll", 1)
            #Option 1 for quad, 0 for tri
            gmsh.model.mesh.generate(2)
            #(2) corresponds to dimension of mesh generated, 2 = surface, 1 = curve .etc.
        except:
            print("Angle in curve to sharp for quad mesh, meshing with triangles...")
            gmsh.option.setNumber("Mesh.RecombineAll", 0) #if multiple surfaces
            gmsh.model.mesh.generate(2)
        #If quad mesh is not possible flags error and continues with triangle mesh
    else:
            gmsh.option.setNumber("Mesh.RecombineAll", 0) #if multiple surfaces
            gmsh.model.mesh.generate(2)


    """Saving GMSH file"""

    print("Save GMSH file? y/n")
    GMSHSave = input()
    
    if GMSHSave == "y" or GMSHSave == "Y":

        """Output Config"""
        Output_Folder_Path = "Examples/Test1_Circle/MESH_geometry"
        #Set as the path for output files
        Output_Folder_Path = UI_Set_Variable(Output_Folder_Path, "Output Folder Path", Default_Setting)
        #UI set Output Folder Path

        Output_Filename = "Test1_Circle.msh"
        #Set end path as .inp for use in Abaqus or .msh for use in SOFA
        Output_Filename = UI_Set_Variable(Output_Filename, "Output Filename", Default_Setting)
        
        Output_Filepath = os.path.join(Output_Folder_Path, Output_Filename )
        gmsh.write(Output_Filepath)
        #Save gmsh file

        print("Mesh saved at " + Output_Filepath)


    print("Open GMSH window? y/n")
    GMSHWindow = input()
    if GMSHWindow == "y" or GMSHWindow == "Y":
        gmsh.fltk.run()
        #opens up GMSH pop up window
    

    gmsh.finalize()
    #end gmsh process