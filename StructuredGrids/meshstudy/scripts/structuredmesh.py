import gmsh
import numpy as np
import scipy.interpolate as sint
import argparse
import json


def structured_mesh(airfoilpath, writepath, mesh_params):

    """
        A pygmsh function to create a structure transfinite airfoil for suitable for OpenFOAM
        simulation. 
    """


    chord_length =  mesh_params["chordlength"]
    L_x = mesh_params["DomainLength"]
    L_y = mesh_params["DomainHeight"]
    N_r = mesh_params["Rdivs"]
    N_1 = mesh_params["Zone1"]
    N_2 = mesh_params["Zone2"]
    N_3 = mesh_params["Zone3"]
    N_H = mesh_params["Hdivs"]
    gratio = mesh_params["R_ratio"]
    hratio = mesh_params["H_ratio"]
    span = mesh_params["span"]

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
    # airfoil point generation
    for i in range(len(coords)):
        gmsh.model.occ.addPoint(coords[i,0], coords[i,1], 0.0, tag=i+1)
        tags.append(i+1)
    tags.append(1)

    # spline interpolation of curve using gmsh module
    spl = gmsh.model.occ.addSpline(tags, 1)
    airfoilloop = gmsh.model.occ.addCurveLoop([spl])
    

    # point definition
    center = gmsh.model.occ.addPoint(0.0,0.0,0.0)
    p1 = gmsh.model.occ.addPoint(3.3*chord_length, AFcentroid[1], 0.0)
    p3 = gmsh.model.occ.addPoint(7*chord_length, L_y*chord_length, 0.0)
    p4 = gmsh.model.occ.addPoint(7*chord_length,-L_y*chord_length, 0.0)
    p5 = gmsh.model.occ.addPoint(L_x*chord_length, L_y*chord_length,0.0)
    p6 = gmsh.model.occ.addPoint(L_x*chord_length,-L_y*chord_length,0.0)
    p7 = gmsh.model.occ.addPoint(L_x*chord_length, 0.0, 0.0)

    C1 = gmsh.model.occ.addPoint(0.0,
                                 L_y*chord_length,
                                 0.0)
    C5 = gmsh.model.occ.addPoint(0.0,
                                -L_y*chord_length,
                                 0.0)

    # exterior 1d domain definition

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

    gmsh.model.occ.synchronize()

    # cut sections for different mesh types
    fragments_sect1 = gmsh.model.occ.fragment([(1, airfoilloop)], [(1, l10), (1, l11)])

    gmsh.model.occ.synchronize()
    

    # add curve loops for extrusion
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

    # add Planar surface entities

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

    # set domains to be meshed by a transfinite algorithm (structured mesh)
    # all radial divisions will have a number N_r of divisions with the same growth ratio
    
    # Radially outward divisions
    gmsh.model.mesh.setTransfiniteCurve(l7, N_r, "Progression", gratio)
    gmsh.model.mesh.setTransfiniteCurve(l8, N_r, "Progression", gratio)
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][1][1][1], N_r, "Progression", gratio)
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][2][1][1], N_r, "Progression", gratio)
    gmsh.model.mesh.setTransfiniteCurve(l3, N_r,"Progression", -gratio)
    gmsh.model.mesh.setTransfiniteCurve(l4, N_r,"Progression", gratio)

    # inlet and front of airfoil 
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][0][1][1], N_1)
    gmsh.model.mesh.setTransfiniteCurve(circ1, N_1)

    #spline top/bottom hourglass sections
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][0][0][1], N_2)
    gmsh.model.mesh.setTransfiniteCurve(l1, N_2)
    gmsh.model.mesh.setTransfiniteCurve(l6, N_3)
    gmsh.model.mesh.setTransfiniteCurve(fragments_sect1[1][0][2][1], N_3)

    # horizontal outlet
    gmsh.model.mesh.setTransfiniteCurve(l2, N_H, "Progression", hratio)
    gmsh.model.mesh.setTransfiniteCurve(l9, N_H, "Progression", hratio) 
    gmsh.model.mesh.setTransfiniteCurve(l5, N_H, "Progression",-hratio)
    
    # set transfinite surfaces for gridding
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

    # Extrude model for OpenFOAM compatibility
    OFairfoil = gmsh.model.occ.extrude(surfaces, 0, 0, span, numElements=[1], \
                    heights = [1], recombine=True) 

    gmsh.model.occ.synchronize()

    # physical domain identification for OpenFOAM compatibility

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
    gmsh.write(writepath) 
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--airfoil", 
                        help="Airfoil path definition",
                        type=str)

    parser.add_argument("--writepath", 
                        help="Write path definition",
                        type=str)
    
    parser.add_argument("--meshparams",
                        help="Mesh parameters json file path",
                        type=str)

    args = parser.parse_args()

    with open(args.meshparams) as meshfile: 
        mesh_params = json.load(meshfile)

    structured_mesh(args.airfoil, args.writepath, mesh_params)