# Array handling and numerical methods
import numpy as np 
from scipy.optimize import fixed_point

# plotting and visualizing

import matplotlib.pyplot as plt

# OpenFOAM file handling

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

class AirfoilSimValidation(object):
    """
        Methods adopted from  the"Procedure for Estimation and Reporting of Uncertainty Due to 
        Discretization in CFD Applications" to validate CFD simulations.
    """
    

    def __init__(self, case_dir, meshcases) -> None:
        
        self.case_dir = case_dir
        self.meshcases = meshcases
        
        self.getVolumes()
        self.getCoeffs()
        self.getHs()


    
    def getData(self): 
        
        self.volume = []
        self.coeffs = []
        self.h = []
        self.r = []

        for meshcase in self.meshcases:
            volumes = ParsedParameterFile(self.case_dir+meshcase)
            self.volume.append(np.array(volumes["internalField"]))
            self.coeffs.append(np.loadtxt(self.case_dir+meshcase+
                                "/postProcessing/forceCoeffs/0/forceCoeffs.dat").mean(axis=0)[3])

        for i in range(len(self.volume)): 
            self.h.append(np.mean(self.volume[i])**(1/3))

        for i in range(len(self.h)-1):
            self.r.append(self.h[i+1]/self.h[i])


