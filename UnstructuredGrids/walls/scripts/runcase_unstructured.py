# regular imports
import os
import argparse
import numpy as np
import json

# PyFoam imports 
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector

# local imports
import airfoilmesh

def Rethetat(Tu):
    if Tu <= 1.3: 
        Re = 1173.51 - 589.428*Tu + 0.2196/Tu**2
    else: 
        Re = 331.5/(Tu-0.5658)**0.671
    return Re 


def GRTairfoilsim(tScheme, Re, Tu, nu, nuratio, aoa,
                mesh_controls, chord_length, span, rhoInf,
                Nsteps, airfoilpath, save_path="../runs/"):

    # Physical variables setup

    U = Re*nu/chord_length
    k = 3/2*((Tu/100)*U)**2

    #omega = k**0.5/0.09**0.25/chord_length 
    omega = rhoInf*k/nu*nuratio**-1  
    gammaInt = 1

    # Case setup OpenFOAM

    if tScheme == "steady":
        templateCase = SolutionDirectory("../../../BaseCases/Unstructured/GRTsteady", archive=None, paraviewLink=False)
    else:
        templateCase = SolutionDirectory("../../BaseCases/GRTunsteady", archive=None, paraviewLink=False)
    
    case = templateCase.cloneCase(save_path+"GRT"+tScheme+str(int(aoa))+mesh_controls["name"])

    # Mesh airfoil 

    writepath = os.path.join(case.name,"airfoil.msh")
    airfoilmesh.mesh_airfoil(airfoilpath, aoa, writepath, 
                    chord_length=chord_length, span=span, mesh_controls=mesh_controls)

    cwd = os.getcwd()
    os.chdir(case.name)
    os.system("gmshToFoam airfoil.msh")
    os.system("rm airfoil.msh")
    os.chdir(cwd)
    
    os.system("pyFoamChangeBoundaryType.py "+case.name+ " sides empty")
    os.system("pyFoamChangeBoundaryType.py "+case.name+ " airfoil wall")
    #os.system("pyFoamChangeBoundaryType.py "+case.name+ " walls wall")


    # Modify initial conditions

    UFile = ParsedParameterFile(os.path.join(case.name,"0","U"))
    ReThetatFile = ParsedParameterFile(os.path.join(case.name,"0","ReThetat"))
    nutFile = ParsedParameterFile(os.path.join(case.name,"0","nut"))
    omegaFile = ParsedParameterFile(os.path.join(case.name,"0","omega"))
    kFile = ParsedParameterFile(os.path.join(case.name,"0","k"))
    gammaIntFile = ParsedParameterFile(os.path.join(case.name,"0","gammaInt"))

    nuFile1 = ParsedParameterFile(os.path.join(case.name,"constant","physicalProperties"))
    nuFile2 = ParsedParameterFile(os.path.join(case.name,"constant","transportProperties"))

    controlDict = ParsedParameterFile(os.path.join(case.name, "system", "controlDict"))
    aoa = aoa*np.pi/180
    UFile["internalField"].setUniform(Vector(U, 0, 0))
    ReThetatFile["internalField"].setUniform(Rethetat(Tu))
    omegaFile["omega_bound"] = omega
    kFile["kbound"] = k
    gammaIntFile["internalField"].setUniform(gammaInt)
    #nutFile["internalField"].setUniform(nu*nuratio)

    nuFile1["nu"][2] = nu
    nuFile2["nu"][1] = nu

    controlDict["time"] = Nsteps
    controlDict["writeInterval"] = int(Nsteps/4)
    controlDict["functions"]["forceCoeffs"]["rhoInf"] = rhoInf
    controlDict["functions"]["forceCoeffs"]["magUInf"] = U
    controlDict["functions"]["forceCoeffs"]["lRef"] = chord_length
    controlDict["functions"]["forceCoeffs"]["Aref"] = chord_length*span
  
    UFile.writeFile()
    ReThetatFile.writeFile()
    omegaFile.writeFile()
    kFile.writeFile()
    gammaIntFile.writeFile()
    nutFile.writeFile()
    
    nuFile1.writeFile()
    nuFile2.writeFile()

    controlDict.writeFile()


    #Run parallel simulation from python
    
    os.chdir(case.name)
    
    os.system("checkMesh > mesh.log")
    
    
    os.system("decomposePar")   
        
    if tScheme == "steady":
        os.system("mpirun -np 4 simpleFoam > log.airfoil -parallel")
    else:
        os.system("mpirun -np 4 pimpleFoam > log.airfoil -parallel")
    os.system("reconstructPar") 
    os.system("postProcess -func sampleObjectPatch")
    os.system("rm -r *proc*")
    
    #os.system("postProcess -func yplus")
    
    
    os.chdir(cwd)

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser()

    parser.add_argument("--scheme", 
                        help="Definition of airfoil Reynolds number for simulation.", 
                        type=str)

    parser.add_argument("--Reynolds", 
                        help="Definition of airfoil Reynolds number for simulation.", 
                        type=float)

    parser.add_argument("--Tu", 
                        help="Definition of turbulence intensity (%) for airfoil simulation.", 
                        type=float)

    parser.add_argument("--nu", 
                       help="Definition of kinematic viscosity for airfoil simulation.", 
                        type=float)

    parser.add_argument("--nuratio", 
                       help="Definition of kinematic viscosity for airfoil simulation.", 
                        type=float)

    parser.add_argument("--c", 
                        help="Definition of airfoil chord length.", 
                        type=float)

    parser.add_argument("--s", 
                        help="Definition of wing span.", 
                        type=float)

    parser.add_argument("--rho", 
                        help="Definition of density.", 
                        type=float)

    parser.add_argument("--aoa", 
                        help="Definition of angle of attack for airfoil simulation.", 
                        type=float)

    parser.add_argument("--nsteps", 
                        help="Definition of angle of attack for airfoil simulation.", 
                        type=int)
                        
    parser.add_argument("--airfoil",
                        help="Definition of airfoil filepath for simulation.\
                                (text file with two columns; no headers)",
                        type=str)

    parser.add_argument("--savepath",
                        help="Definition of save directory",
                        type=str)

    parser.add_argument("--meshcontrols",
                        help="Definition of save directory",
                        type=str)

    args = parser.parse_args()


    with open(args.meshcontrols) as meshfile: 
        meshcontrols = json.load(meshfile)

    GRTairfoilsim(args.scheme, args.Reynolds, args.Tu, 
                    args.nu, args.nuratio, args.aoa, 
                    meshcontrols, args.c, args.s, 
                    args.rho, args.nsteps, 
                    args.airfoil, args.savepath)

# Example run ------ python3 runcase.py --Reynolds 1e5 --Tu 20 --nu 1.1516e-5 --aoa 0 --c 0.1 --s 0.1 --airfoil "./mesh/NRELs809.txt" --savepath "../"
