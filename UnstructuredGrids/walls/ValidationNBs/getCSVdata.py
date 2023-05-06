import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

plt.rcParams.update({
    'text.usetex': True,
    'figure.dpi': 150})

plt.tight_layout()

def getsweepdata(sweepdir):

    cwd = os.getcwd()
    files = os.listdir(sweepdir)
    files = np.array(files)
    coefficients = np.zeros((len(files),3))
    angles = np.arange(-8, 18, 2)

    sfiles = [ifile.replace("GRTsteady", "") for ifile in files]
    sfiles = np.array([ifile.replace("Mesh8", "") for ifile in sfiles]).astype(int)
    #print(sfiles)

    files = files[sfiles.argsort()]
    #print(files)

    for i, file in enumerate(files):
        os.chdir(os.path.join(sweepdir,file))
        coefs = np.loadtxt("postProcessing/forceCoeffs/0/forceCoeffs.dat", skiprows=9 , delimiter="\t")
        coefsmean = np.mean(coefs[-300:-100], axis=0)
        #print(coefs)
        coefficients[i, 1] = coefsmean[2]
        coefficients[i, 2] = coefsmean[3]
        os.chdir(cwd)

    return sorted(files), coefficients, angles

def get_coefficients(resultsdir):

    airdict = {}
    cwd = os.getcwd()

    fig1, ax1 = plt.subplots(figsize=(7,5), dpi=150)
    ax1.set_axisbelow(True)
    fig2, ax2 = plt.subplots(figsize=(7,5), dpi=150)
    ax2.set_axisbelow(True)
    fig3, ax3 = plt.subplots(figsize=(7,5), dpi=150)
    ax3.set_axisbelow(True)
    

    for i, sweepdir in enumerate(sorted(os.listdir(resultsdir))):

        if sweepdir != "aoasweep0":
            os.chdir(os.path.join(resultsdir, sweepdir))
            _, coef, angles = getsweepdata(os.getcwd())

            coef = coef[1:-2]

            airdict["mod"+str(i)+"lift"] = coef[:,2]
            airdict["mod"+str(i)+"drag"] = coef[:,1]

            ax1.plot(angles, coef[:, 1], marker='.', label='SG6043 mod'+str(i))
            ax1.set_ylabel(r"$C_\mathrm{drag}$")
            ax1.set_xlabel(r"Angle of attack $[^\circ]$")
            ax2.plot(angles, coef[:, 2], marker='.', label='SG6043 mod'+str(i))
            ax2.set_ylabel(r"$C_\mathrm{lift}$")
            ax2.set_xlabel(r"Angle of attack $[^\circ]$")
            ax3.plot(angles, coef[:,2]/coef[:,1], marker='.', label='SG6043 mod'+str(i))
            ax3.set_ylabel(r"$C_\mathrm{lift}/C_\mathrm{drag}$")
            ax3.set_xlabel(r"Angle of attack $[^\circ]$")
            os.chdir(cwd)
        else: 
            os.chdir(os.path.join(resultsdir, sweepdir))
            _, coef, angles = getsweepdata(os.getcwd())
            angles = angles[angles!=-6.]
            coef = coef[1:-2]

            airdict["mod"+str(i)+"lift"] = coef[:,2].tolist().append(0)
            airdict["mod"+str(i)+"drag"] = coef[:,1].tolist().append(0)

            ax1.plot(angles, coef[:, 1], marker='.', label='SG6043 mod'+str(i))
            ax1.set_ylabel(r"$C_\mathrm{drag}$")
            ax1.set_xlabel(r"Angle of attack $[^\circ]$")
            ax2.plot(angles, coef[:, 2], marker='.', label='SG6043 mod'+str(i))
            ax2.set_ylabel(r"$C_\mathrm{lift}$")
            ax2.set_xlabel(r"Angle of attack $[^\circ]$")
            ax3.plot(angles, coef[:,2]/coef[:,1], marker='.', label='SG6043 mod'+str(i))
            ax3.set_ylabel(r"$C_\mathrm{lift}/C_\mathrm{drag}$")
            ax3.set_xlabel(r"Angle of attack $[^\circ]$")
            os.chdir(cwd)



    box1 = ax1.get_position()
    ax1.set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
    ax1.grid()

    # Put a legend to the right of the current axis
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    box2 = ax2.get_position()
    ax2.set_position([box2.x0, box2.y0, box2.width * 0.8, box2.height])
    ax2.grid()

    # Put a legend to the right of the current axis
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    box3 = ax3.get_position()
    ax3.set_position([box3.x0, box3.y0, box3.width * 0.8, box3.height])
    ax3.grid()

    # Put a legend to the right of the current axis
    ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig1.savefig("modifieddrag.svg")
    fig2.savefig("modifiedlift.svg")
    fig3.savefig("modifiedliftdragratio.svg")
    
    p = pd.DataFrame(airdict)
    p.to_csv("coefs.csv")


if __name__ == "__main__":

    try: 
        resultsdir = str(sys.argv[1])
    
    except (IndexError, ValueError):
        raise SystemExit
    
    get_coefficients(resultsdir)
    
