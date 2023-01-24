# Costa Rica High Technology Center (CeNAT)
# Costa Rica Advanced Computing Collaboratory (CNCA)
# Programmer: Johansell Villalobos
# Structured airfoil mesh creation for 2D OpenFOAM simulation

import gmsh
import numpy as np
import scipy.interpolate as sint
import argparse
import json

def structured_mesh(airfoilpath, writepath,
                    mesh_params):
    """
        A pygmsh function to create a structure transfinite airfoil for suitable for OpenFOAM
        simulation. 
    
    
    """

    angleofattack = mesh_params["aoa"]
    chord_length =  mesh_params["chordlength"]
    L_x = mesh_params["DomainLength"]
    L_y = mesh_params["DomainHeight"]
    N_r = mesh_params["Rdivs"]
    N_1 = mesh_params["Zone1"]
    N_2 = mesh_params["Zone2"]
    N_3 = mesh_params["Zone3"]
    N_4 = mesh_params["Zone4"]
    N_5 = mesh_params["Zone5"]

    # initialize gmsh CAD engine
    gmsh.initialize()

    # set model name
    gmsh.model.add(mesh_params["name"])

    # airfoildata read 
    # example: airfoilpath -> "./mesh/NRELs826.txt"
    
    airfoildata = chord_length*np.loadtxt(airfoilpath, delimiter=',')
    airfoildata = airfoildata + np.array([3*chord_length, 0.])
    
    # calculate centroid of data points
    AFcentroid = np.mean(airfoildata, axis=0) 

    # interpolate data via a Bspline (optional)
    spline = sint.splprep(airfoildata.T, s=0.0, k=2)
    t = np.linspace(0, 1, 300)
    coords = np.array(sint.splev(t, spline[0], der=0)).T

    # gmsh uses the OpenCASCADE kernel for CAD I/O and generation

    tags = []
    #airfoil point generation
    for i in range(len(coords)):
        gmsh.model.occ.addPoint(coords[i,0], coords[i,1], 0.0, tag=i+1)
        tags.append(i+1)
    tags.append(1)

    #spline interpolation of curve using gmsh module
    spl = gmsh.model.occ.addSpline(tags, 1)
    airfoilloop = gmsh.model.occ.addCurveLoop([spl])
    
    #gmsh.model.occ.mesh.setSize(gmsh.model.occ.getEntities(0), 0.002)

    center = gmsh.model.occ.addPoint(0.0,0.0,0.0)

    p1 = gmsh.model.occ.addPoint(3.1*chord_length, AFcentroid[1], 0.0)
    p3 = gmsh.model.occ.addPoint(7*chord_length, L_y*chord_length, 0.0)
    p4 = gmsh.model.occ.addPoint(7*chord_length,-L_y*chord_length, 0.0)
    p5 = gmsh.model.occ.addPoint(L_x*chord_length, L_y*chord_length,0.0)
    p6 = gmsh.model.occ.addPoint(L_x*chord_length,-L_y*chord_length,0.0)
    p7 = gmsh.model.occ.addPoint(L_x*chord_length, 0.0, 0.0)

    C1 = gmsh.model.occ.addPoint(0.0,
                                 L_y*chord_length,
                                 0.0)
    C2 = gmsh.model.occ.addPoint(-L_y*chord_length*np.cos(np.pi/3),
                                 L_y*chord_length*np.sin(np.pi/3),
                                 0.0)
    C4 = gmsh.model.occ.addPoint(-L_y*chord_length*np.cos(np.pi/3),
                                -L_y*chord_length*np.sin(np.pi/3),
                                 0.0)
    C5 = gmsh.model.occ.addPoint(0.0,
                                -L_y*chord_length,
                                 0.0)


    circ1 = gmsh.model.occ.addCircleArc(C5, center, C1)
    
    l1 = gmsh.model.occ.addLine(C1, p3)
    l6 = gmsh.model.occ.addLine(p4, C5)

    l2 = gmsh.model.occ.addLine(p3, p5)
    l3 = gmsh.model.occ.addLine(p5, p7)
    l4 = gmsh.model.occ.addLine(p7, p6)
    l5= gmsh.model.occ.addLine(p6, p4)

    l7 = gmsh.model.occ.addLine(tags[0], p3)
    l8 = gmsh.model.occ.addLine(tags[0], p4)
    l9 = gmsh.model.occ.addLine(tags[0], p7)
    l10 = gmsh.model.occ.addLine(p1, C1)
    l11 = gmsh.model.occ.addLine(p1, C5)

    #cutline1 = gmsh.model.occ.addLine(C3, p1)
    #cutline2 = gmsh.model.occ.addLine(C2, p1)
    #cutline3 = gmsh.model.occ.addLine(C4, p1)

    gmsh.model.occ.synchronize()

    fragments_sect1 = gmsh.model.occ.fragment([(1, airfoilloop)], [(1, l10), (1, l11)])

    #print(fragments_sect1)

    gmsh.model.occ.synchronize()
    
    outlet1 = gmsh.model.occ.addCurveLoop([l2, l3, l9, l7])
    outlet2 = gmsh.model.occ.addCurveLoop([l5, l4, l9, l8])

    inletmid = gmsh.model.occ.addCurveLoop([circ1, 
                                fragments_sect1[1][1][1][1],
                                fragments_sect1[1][0][1][1], 
                                fragments_sect1[1][2][1][1]])

    inlettop = gmsh.model.occ.addCurveLoop([l1, l7,  
                                fragments_sect1[1][0][0][1],
                                fragments_sect1[1][1][1][1]])

    inletbottom = gmsh.model.occ.addCurveLoop([l6, l8, 
                                fragments_sect1[1][0][2][1],
                                fragments_sect1[1][2][1][1]])

    gmsh.model.occ.synchronize()


    surfout1 = gmsh.model.occ.addPlaneSurface([outlet1])
    surfout2 = gmsh.model.occ.addPlaneSurface([outlet2])
    surfinmid = gmsh.model.occ.addPlaneSurface([inletmid])
    surfintop = gmsh.model.occ.addPlaneSurface([inlettop])
    surfinbottom =gmsh.model.occ.addPlaneSurface([inletbottom])
    gmsh.model.occ.synchronize()
    surfaces = [(2, surfout1),
                (2, surfout2),
                (2, surfinmid),
                (2, surfintop),
                (2, surfinbottom)]

    # side 1
    gmsh.model.mesh.setTransfiniteCurve(l7, 100, "Progression", 1.06)

    # side 2
    gmsh.model.mesh.setTransfiniteCurve(l8, 100, "Progression", 1.06)
    # front inlet 
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][1][1][1], 100, "Progression", 1.06)
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][2][1][1], 100, "Progression", 1.06)
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][0][1][1], 100)
    gmsh.model.mesh.setTransfiniteCurve(circ1, 100)


    gmsh.model.mesh.setTransfiniteCurve(circ1, 100)

    #spline and top/bottom hourglass sections

    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][0][0][1], N) #top
    gmsh.model.mesh.setTransfiniteCurve(l1, N) #top
    gmsh.model.mesh.setTransfiniteCurve(l6, N) # bottom
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][0][2][1], N) #bottom



    gmsh.model.mesh.setTransfiniteCurve(l3, 100,"Progression", -1.06)
    gmsh.model.mesh.setTransfiniteCurve(l4, 100,"Progression", 1.06)


    # horizontal outlet
    gmsh.model.mesh.setTransfiniteCurve(l2, 100, "Progression", 1.06)
    gmsh.model.mesh.setTransfiniteCurve(l9, 100, "Progression", 1.06) 
    gmsh.model.mesh.setTransfiniteCurve(l5, 100, "Progression", -1.06)


 
    gmsh.model.mesh.setTransfiniteSurface(surfout1, "Left")
    gmsh.model.mesh.setTransfiniteSurface(surfout2, "Left")
    gmsh.model.mesh.setTransfiniteSurface(surfinmid, "Left")
    gmsh.model.mesh.setTransfiniteSurface(surfintop, "Left")
    gmsh.model.mesh.setTransfiniteSurface(surfinbottom, "Left")


    gmsh.model.mesh.setRecombine(2, surfout1)
    gmsh.model.mesh.setRecombine(2, surfout2)
    gmsh.model.mesh.setRecombine(2, surfinmid)
    gmsh.model.mesh.setRecombine(2, surfintop)
    gmsh.model.mesh.setRecombine(2, surfinbottom)

    gmsh.model.occ.synchronize()

    OFairfoil = gmsh.model.occ.extrude(surfaces, 0, 0, 0.3, numElements=[1], \
                    heights = [1], recombine=True) 

    gmsh.model.occ.synchronize()


    volumes = []
    fusedvol = []
    surfs = []

    for x in OFairfoil:
        if x[0] == 3:
            fusedvol.append(x)
            volumes.append(x[1])
        elif x[0]==2: 
            surfs.append(x)
        else: 
            continue
    

    sides = [surf[1] for surf in surfaces]
    inlet = []
    outlet= []
    object= []
    
    
    for x in surfs: 
        if x[1] == 21 or x[1] == 17 or x[1] == 24: 
            object.append(x[1])
        elif x[1] == 10 or x[1] == 14 or x[1] == 25 or x[1] == 22 or x[1] == 19:
            sides.append(x[1])
        elif x[1] == 1 or x[1] == 2 or x[1] == 3 or x[1] == 4 or x[1] == 5:
            sides.append(x[1])
        elif x[1] == 7 or x[1] == 13:
            outlet.append(x[1])
        elif x[1] == 6 or x[1] == 36 or x[1] == 15 or x[1] == 23 or x[1] == 11 or x[1] == 20: 
            inlet.append(x[1])
        else: 
            continue

    gmsh.model.addPhysicalGroup(2, object, name="airfoil")
    gmsh.model.addPhysicalGroup(2, sides, name="sides")
    gmsh.model.addPhysicalGroup(2, inlet, name="inlet")
    gmsh.model.addPhysicalGroup(2, outlet, name="outlet")
    gmsh.model.addPhysicalGroup(3, volumes, name="fluid")

    gmsh.model.occ.synchronize()

    gmsh.option.setNumber("Mesh.Smoothing", 100)
    gmsh.model.mesh.generate(2)    
    gmsh.model.occ.synchronize()
    
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.)
    gmsh.write("airfoil.msh") 

    gmsh.finalize()


if __name__ == '__main__':
    structured_mesh("./meshstudy/scripts/airfoils/NRELs826.txt", 0., 1, 40, 25)