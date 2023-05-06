#!usr/bin/python3

import gmsh
import numpy as np
import argparse
import json
import scipy.interpolate as sint

def mesh_airfoil(airfoilpath, angleofattack, writepath, 
            chord_length=1, span=0.1, 
            mesh_controls={
                "generalMesh": 
                {
                    "setSize": 0.006,
                    "SizeMin": 0.01, 
                    "SizeMax": 0.5,
                    "DistMin": 0.01, 
                    "DistMax": 2,
                }, 
                "boundaryLayer": 
                {
                    "Size": 1e-3, 
                    "Ratio": 1.1, 
                    "Thickness": 0.02, 
                    "NElements": 15
                }
            }):
    
    gmsh.initialize()
    gmsh.model.add("airfoil")

    #domain parameters

    #rotation matrix set up
    angle = np.pi*angleofattack/180
    RM = np.array([[np.cos(angle),-np.sin(angle)],
                [np.sin(angle),np.cos(angle)]])


    #airfoildata read 
    airfoildata = chord_length*np.loadtxt(airfoilpath, delimiter=',') # example: airfoilpath -> "./mesh/NRELs826.txt"
    airfoildata = airfoildata @ RM
    AFcentroid = np.mean(airfoildata, axis=0)
    
    spline = sint.splprep(airfoildata.T, s=0.0, k=2)
    t = np.linspace(0, 1, 1000)
    coords = np.array(sint.splev(t, spline[0], der=0)).T

    tags = []
    #airfoil point generation
    for i in range(len(coords)):
        gmsh.model.occ.addPoint(coords[i,0], coords[i,1], 0.0, tag=i+1)
        tags.append(i+1)
    tags.append(1)


    #spline interpolation of curve
    spl = gmsh.model.occ.addSpline(tags, 1)
    airfoilloop = gmsh.model.occ.addCurveLoop([spl])
    gmsh.model.occ.mesh.setSize(gmsh.model.occ.getEntities(0), 
        mesh_controls["generalMesh"]["setSize"]*chord_length)

    #rectangle domain specification
    p1 = gmsh.model.occ.addPoint(AFcentroid[0]-15*chord_length, AFcentroid[1]-15*chord_length,0.0)
    p2 = gmsh.model.occ.addPoint(AFcentroid[0]+15*chord_length, AFcentroid[1]-15*chord_length,0.0)
    p3 = gmsh.model.occ.addPoint(AFcentroid[0]+15*chord_length, AFcentroid[1]+15*chord_length,0.0)
    p4 = gmsh.model.occ.addPoint(AFcentroid[0]-15*chord_length, AFcentroid[1]+15*chord_length,0.0)

    l1 = gmsh.model.occ.addLine(p1, p2)
    l2 = gmsh.model.occ.addLine(p2, p3) 
    l3 = gmsh.model.occ.addLine(p3, p4)
    l4 = gmsh.model.occ.addLine(p4, p1)

    cout = gmsh.model.occ.addCurveLoop([l1, l2, l3, l4])
    airfoil = gmsh.model.occ.addPlaneSurface([cout, airfoilloop])
    gmsh.model.occ.synchronize()
    #gmsh.model.mesh.setTransfiniteCurve(airfoilloop, 500)

    #gmsh.model.mesh.setRecombine(2, airfoil)

    OFairfoil = gmsh.model.occ.extrude([(2,airfoil)], 0, 0, span, numElements=[1], \
                        heights = [1], recombine=True) 

    gmsh.model.occ.synchronize()

    gmsh.model.addPhysicalGroup(2, [OFairfoil[6][1]], name="airfoil")
    gmsh.model.addPhysicalGroup(2, [OFairfoil[5][1], OFairfoil[2][1], OFairfoil[4][1]], name="inlet")
    gmsh.model.addPhysicalGroup(2, [OFairfoil[3][1]], name="outlet")
    gmsh.model.addPhysicalGroup(2, [OFairfoil[0][1], airfoil], name="sides")
    #gmsh.model.addPhysicalGroup(2, [OFairfoil[2][1], OFairfoil[4][1]], name="walls")

    #gmsh.model.addPhysicalGroup(2, [OFairfoil[3][1]], name="back")
    #gmsh.model.addPhysicalGroup(2, [OFairfoil[2][1]], name="bottom")

    #gmsh.model.addPhysicalGroup(2, [airfoil], name="right")
    gmsh.model.addPhysicalGroup(3, [OFairfoil[1][1]], name="Fluid")

    gmsh.model.occ.synchronize() 


    gmsh.model.mesh.field.add("Distance", 1)
    gmsh.model.mesh.field.setNumbers(1, "CurvesList", [spl])
    gmsh.model.mesh.field.setNumber(1, "Sampling", 200)

    gmsh.model.mesh.field.add("Threshold", 2)
    gmsh.model.mesh.field.setNumber(2, "InField", 1)
    gmsh.model.mesh.field.setNumber(2, "SizeMin", mesh_controls["generalMesh"]["SizeMin"]*chord_length)
    gmsh.model.mesh.field.setNumber(2, "SizeMax", mesh_controls["generalMesh"]["SizeMax"]*chord_length)
    gmsh.model.mesh.field.setNumber(2, "DistMin", mesh_controls["generalMesh"]["DistMin"]*chord_length)
    gmsh.model.mesh.field.setNumber(2, "DistMax", mesh_controls["generalMesh"]["DistMax"]*chord_length)
    
    """
    gmsh.model.mesh.field.add("Box", 6)
    gmsh.model.mesh.field.setNumber(6, "VIn", 0.08)
    gmsh.model.mesh.field.setNumber(6, "VOut", 1)
    gmsh.model.mesh.field.setNumber(6, "XMin", AFcentroid[0]-chord_length)
    gmsh.model.mesh.field.setNumber(6, "XMax", AFcentroid[0]+7*chord_length)
    gmsh.model.mesh.field.setNumber(6, "YMin", AFcentroid[1]-1.1*chord_length)
    gmsh.model.mesh.field.setNumber(6, "YMax", AFcentroid[1]+1.1*chord_length)
    gmsh.model.mesh.field.setNumber(6, "Thickness", 2)
    
    
    f = gmsh.model.mesh.field.add('BoundaryLayer')
    gmsh.model.mesh.field.setNumbers(f, 'CurvesList', [airfoilloop,])
    gmsh.model.mesh.field.setNumber(f, 'Size', 0.001)
    gmsh.model.mesh.field.setNumber(f, 'Ratio', 1.01)
    gmsh.model.mesh.field.setNumber(f, 'Quads', 1)
    gmsh.model.mesh.field.setNumber(f, 'Thickness', 0.01)
    gmsh.option.setNumber('Mesh.BoundaryLayerFanElements', 25)
    gmsh.model.mesh.field.setNumbers(f, 'FanPointsList', [tags[-1]])
    gmsh.model.mesh.field.setAsBoundaryLayer(f)
    
    """
    #######################################################################

    gmsh.option.setNumber("Mesh.Algorithm", 8)
    gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 2)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 1)


    gmsh.model.mesh.field.add("Min", 7)
    gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
    gmsh.model.mesh.field.setAsBackgroundMesh(7)
    gmsh.option.setNumber("Mesh.Algorithm", 2)
    
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.)
    gmsh.write(writepath)
    gmsh.finalize()

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    
    
    parser.add_argument("--airfoil",
                        help="Definition of save directory",
                        type=str)

    parser.add_argument("--AoA",
                        help="Definition of save directory",
                        type=float)

    parser.add_argument("--writepath",
                        help="Definition of save directory",
                        type=str)

    parser.add_argument("--c",
                        help="Definition of save directory",
                        type=float)

    parser.add_argument("--s",
                        help="Definition of save directory",
                        type=float)

    parser.add_argument("--meshcontrols",
                        help="Definition of save directory",
                        type=str)

    args = parser.parse_args()

    with open(args.meshcontrols) as meshfile: 
        meshcontrols = json.load(meshfile)

    mesh_airfoil(args.airfoil, args.AoA, args.writepath, 
            args.c, args.c, meshcontrols)