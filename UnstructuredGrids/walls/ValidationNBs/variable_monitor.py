import numpy as np
import matplotlib.pyplot as plt
import sys
import os

def plot_case_variables(sweepdir, casepath, ax):


    casecoeffs = np.loadtxt(sweepdir+casepath+"/postProcessing/forceCoeffs/0/forceCoeffs.dat", 
                skiprows=9 , delimiter="\t")
    
    residuals = np.loadtxt(sweepdir+casepath+"/postProcessing/residuals/0/residuals.dat", skiprows=3, 
                delimiter="\t")

    ax.plot(casecoeffs[10:,3], label=casepath[10:])
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Lift coefficient")
    #plt.axhline(y=coeff[3], c='r')

if __name__ == "__main__": 

    try: 
        sweeppath = str(sys.argv[1])
    
    except (IndexError, ValueError) :
        raise SystemExit

    fig, ax = plt.subplots(figsize=(7,5), dpi=150)
    for iDir in sorted(os.listdir(sweeppath)):
        plot_case_variables(sweeppath, iDir, ax)
    
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.savefig("Convergence_plot.png")
