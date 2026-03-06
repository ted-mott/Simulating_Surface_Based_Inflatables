"""
Simulation_Meshing.py
Using to create a GMSH file that can be used in Abaqus or SOFA
27.01.2026
Ted M
________________________________________________________________________________________________
"""

"""
Libraries
________________________________________________________________________________________________
"""
import gmsh
import os


"""
Functions
________________________________________________________________________________________________
"""

def UI_Set_Variable(variable, variable_Name, Default_Setting):
    #Function used for simple command line UI to set parameters

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
    #Function generates curve loops, good for planar curves, can be used to find which curves are open adnd closed for fragment

    Closed_Loop_List = []
    Open_Loop_List = []

    for Curve in Curve_List:
        Curve_id = Curve[1]

        try:
            (gmsh.model.occ.addCurveLoop([Curve_id]))
            #curve loop id 
            Closed_Loop_List.append(Curve_id)
            print("Curve ", Curve_id, " is closed")
            
        except:
            Open_Loop_List.append(Curve_id)
            print("Curve ", Curve_id, " is open")

    return(Closed_Loop_List, Open_Loop_List)


def TagFromList(entityList):
    #Function to strip tags out of list of (dim,tag) used for physical groups
    tags = []
    for entity in entityList:
        tag = entity[1]
        tags.append(tag)

    return(tags)
    

def PhysicalGroupTag2Dim(Physical_Group_Tag):
    #Returns physical group dim from tag
    PhysicalGroups = gmsh.model.getPhysicalGroups()
    for dim,tag in PhysicalGroups:
        if tag == Physical_Group_Tag:
            return dim


def ConstructDimTag(dim, tags):
    #
    dim_tag = []
    for tag in tags:
        dim_tag.append((dim, tag))
    return(dim_tag)


def FragmentSurface(Surface_DimTag_List: list[int], Curve_DimTag_List: list[int]):

    #print(Surface_DimTag_List)
    #print(Curve_DimTag_List)

    gmsh.model.occ.synchronize()
    surfaces_before = set(gmsh.model.getEntities(dim=2))

    gmsh.model.occ.fragment(Surface_DimTag_List, Curve_DimTag_List)
    #default args fragment(objectDimTags, toolDimTags, tag=-1, removeObject=True, removeTool=True)
    gmsh.model.occ.synchronize()

    surfaces_after = set(gmsh.model.getEntities(dim=2))
    surfaces_created = surfaces_after.difference(surfaces_before)
    CurveSurfaces = list(surfaces_created)
    #comparing surfaces before to after

    gmsh.model.occ.synchronize()

    if Surface_DimTag_List[0] in surfaces_after:

        print("surface exists", Surface_DimTag_List)
        
        return(Surface_DimTag_List, CurveSurfaces)
    
    else:
        print("surface destroyed, assuming main surface is largest")
        
        surfaces_sorted = sorted(surfaces_created, key=BoundingBox, reverse=True)
        MainSurface = surfaces_sorted[0]
        surfaces_created.remove(MainSurface)

        print("MainSurface", MainSurface)
        
        return([MainSurface], surfaces_created)


def BoundingBox(dimtag):
    dim, tag = dimtag
    #sort Geometric entities by bounding box volume in descending order
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin
    return dx * dy * dz



def EmbedCurveInSurface(Curve_List, Surface):
    #Function that embeds list of curves in a surface

    gmsh.model.occ.synchronize()

    for Curve in Curve_List:
        gmsh.model.mesh.embed(1, [Curve], 2, Surface)
        
        # runs embed curve command in gmsh
    

def Duplicate(Physical_Group):
    #Function used to copy physical groups so that inflatable has 2 layers

    entities = gmsh.model.getEntitiesForPhysicalName(Physical_Group)
    Group_dim = entities[0][0]
    print(Group_dim)

    copied_entities = []

    for dim,tag in entities:
        copied = gmsh.model.occ.copy([(dim, tag)])
        copied_entities.append(copied)

    # gmsh.model.add_physical_group(Group_dim, [Outer_Cut_Surface], name=Physical_Group +"Duplicate" )

    print(entities , "\n" , copied_entities)

    return()


def Meshing():
    #Function used for simple command line UI to set meshing element type

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


def SaveGMSH(Output_Folder_Path):
    #Function used for simple command line UI to set save file parameters

    print("Save GMSH file? y/n")
    GMSHSave = input()
    
    if GMSHSave == "y" or GMSHSave == "Y":

        Output_Filename = "Test1_Circle.msh"
        print("Set file extension as .inp for use in Abaqus or .msh for use in SOFA")
        Output_Filename = UI_Set_Variable(Output_Filename, "Output Filename", Default_Setting)
        
        Output_Filepath = os.path.join(Output_Folder_Path, Output_Filename )
        gmsh.write(Output_Filepath)
        #Save gmsh file

        print("Mesh saved at " + Output_Filepath)



"""
Main
________________________________________________________________________________________________
"""
if __name__ == "__main__":

    """Default Settings"""
    
    Default_Setting = True

    STEP_Folder_Path = "Simulation_Examples/Test2_Patterned_Circle/STEP_geometry"
    #Default path defined here
    Output_Folder_Path = "Simulation_Examples/Test1_2D_Surface_Circle/MSH_geometry"
    #Set as the path for output files
    lc = 4.0
    #Default Global element size


    """"Input config"""

    # print("Use Default Settings? y/n")
    # Default_Option = input()
    # if Default_Option == "n" or Default_Option == "N":
    #     Default_Setting = False
    # #Default Setting added to save having to input over and over again
    
    STEP_Folder_Path = UI_Set_Variable(STEP_Folder_Path, "STEP Folder Path", Default_Setting)

    Output_Folder_Path = UI_Set_Variable(Output_Folder_Path, "Output Folder Path", Default_Setting)
    #UI set Output Folder Path
    lc = UI_Set_Variable(lc, "Global Element Size", Default_Setting)
    #User input for global element size

    gmsh.initialize()
    #initialises GMSH environment
        
    gmsh.clear()
    #clear all previous GMSH geometry

    gmsh.model.add("FlatShape_GMSH")


    """Import STEP files"""

    Inflated_Perimeter_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Perimeter.stp"))

    Outer = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Outer.stp"))
    if Outer[0][0] == 1:
        #geometry stored as tuple (dim,tag), Outer_Cut[0][0] points to dim tag of first item, assuming only one item for outer cut in .stp
        Outer_Loop = [gmsh.model.occ.addCurveLoop([Outer[0][1]])]
        Outer_Surface = gmsh.model.occ.addPlaneSurface(Outer_Loop)
    elif Outer[0][0] == 2:
        Outer_Surface = Outer
    else:
        print("Outer needs to contain surface or curve")

    Coincident_Curves = None
    if os.path.exists(os.path.join(STEP_Folder_Path, "Coincident.stp")):
         Coincident_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Coincident.stp"))
         print("Coincident.stp found")
    
    Anchor_Curves = None
    if os.path.exists(os.path.join(STEP_Folder_Path, "Anchor.stp")):
        Anchor_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Anchor.stp"))
        print("Anchor.stp found")
    #Laser weld perimeter and Outer laser curve are the only expected files


    # CordPoints = None
    # if os.path.exists(os.path.join(STEP_Folder_Path, "Cord_Points.stp")):
    #     CordPoints = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Cord_Points.stp"))
    #     print("Cord_Points.stp found")

    # JoinCurves = None
    # if os.path.exists(os.path.join(STEP_Folder_Path, "Join_Curves.stp")):
    #     CordPoints = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Join_Curves.stp"))
    #     print("Join_Curves.stp found")



    """Curve Loops"""

    Inflated_Surface_Perimeter_Loop = gmsh.model.occ.addCurveLoop([Inflated_Perimeter_Curves[0][1]])

    if Anchor_Curves:
        Anchor_Curves_Closed, Anchor_Curves_Open = Curve_Loop_Generator(Anchor_Curves)
        #Curve_Loop_Generator(Curve_List), return(Closed_Loop_List, Open_Loop_List)

    if Coincident_Curves:
        Coincident_Curves_Closed, Coincident_Curves_Open = Curve_Loop_Generator(Coincident_Curves)



    # """Physical Groups"""
    # #Names are set for usability at end, use internal tags for physical groups to avoid issue when using fragment
    # gmsh.model.occ.synchronize()

    # gmsh.model.addPhysicalGroup(1, TagFromList(Anchor_Curves), name = "AnchorCurves")
    # gmsh.model.addPhysicalGroup(1, TagFromList(Coincident_Curves), name = "CoincidentCurves")
    # #Groups used during simulation

    # OuterSurface = gmsh.model.addPhysicalGroup(2, [Outer_Cut_Surface])
    # InflatedPerimeter = gmsh.model.addPhysicalGroup(1, TagFromList(Inflated_Perimeter_Curves))
    # AnchorCurvesClosed = gmsh.model.addPhysicalGroup(1,  Anchor_Curves_Closed)
    # CoincidentCurvesClosed = gmsh.model.addPhysicalGroup(1,  Coincident_Curves_Closed)
    # #Groups used for fragmentation of surfaces


    """Embedding curves in Surfaces"""

    Outer_Surface, InflateSurface = FragmentSurface(ConstructDimTag(2, [Outer_Surface]), Inflated_Perimeter_Curves)
    # FragmentSurface(Surface_DimTag_List: list[int], Curve_DimTag_List: list[int]) pass as a dim,tag list, GMSH is inconsistent with what it accepts so function ConstructDimTag has been created
    # Returns [dim,tag]

    if Coincident_Curves:
        if Coincident_Curves_Closed :
            InflateSurface, CoincidentSurface = FragmentSurface(InflateSurface, ConstructDimTag(1, Coincident_Curves_Closed))
            gmsh.model.addPhysicalGroup(2, TagFromList(CoincidentSurface), name = "Coincident_Surface")

        if Coincident_Curves_Open :
            pass

    if Anchor_Curves:
        if Anchor_Curves_Closed :
            Outer_Surface, Anchor_Surfaces = FragmentSurface(Outer_Surface , ConstructDimTag(1, Anchor_Curves_Closed))
            gmsh.model.addPhysicalGroup(2, TagFromList(Anchor_Surfaces), name = "Anchor_Surfaces")

        if Anchor_Curves_Open :
            pass


    # gmsh.model.addPhysicalGroup(2, TagFromList(InflateSurface), name = "Inflate_Surface")
    # gmsh.model.addPhysicalGroup(2, TagFromList(Outer_Surface), name = "Outer_Surface")






    #return(CurveSurfaces)


    # OuterSurface, AnchorSurface = FragmentSurface(OuterSurface, AnchorCurvesClosed)
    # InflatedSurface, CoincidentSurface = FragmentSurface(InflatedSurface, CoincidentCurvesClosed)

    # gmsh.model.setPhysicalName(PhysicalGroupTag2Dim(OuterSurface), OuterSurface, "OuterSurface")
    # gmsh.model.setPhysicalName(PhysicalGroupTag2Dim(AnchorSurface), AnchorSurface, "AnchorSurface")
    # gmsh.model.setPhysicalName(PhysicalGroupTag2Dim(InflatedSurface), InflatedSurface, "InflatedSurface")
    # gmsh.model.setPhysicalName(PhysicalGroupTag2Dim(CoincidentSurface), CoincidentSurface, "CoincidentSurface")











    """Copy and Mirror"""
    # Duplicate("Outer_Cut_surface_group")
    



    """Meshing"""


    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)
    #set Global element size

    gmsh.model.occ.synchronize()
    #using open cascade, need to synchronise geometry with GMSH

    Meshing()


    """Output"""


    SaveGMSH(Output_Folder_Path) 

    print("Open GMSH window? y/n")
    GMSHWindow = input()
    if GMSHWindow == "y" or GMSHWindow == "Y":
        gmsh.fltk.run()
        #opens up GMSH pop up window
    
    gmsh.finalize()
    #end gmsh process