import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def get_aoasweep_data(sweepdir):

    cwd = os.getcwd()
    files = os.listdir(sweepdir)
    files = np.array(files)
    coefficients = np.zeros((len(files),3))
    angles = np.arange(-10, 22, 2)

    sfiles = [ifile.replace("GRTsteady", "") for ifile in files]
    sfiles = np.array([ifile.replace("Mesh8", "") for ifile in sfiles]).astype(int)
    #print(sfiles)

    files = files[sfiles.argsort()]
    #print(files)

    for i, file in enumerate(files):
        os.chdir(os.path.join(sweepdir,file))
        coefs = np.loadtxt("postProcessing/forceCoeffs/0/forceCoeffs.dat", skiprows=9 , delimiter="\t")
        coefsmean = np.mean(coefs[-100:], axis=0)
        #print(coefs)
        coefficients[i, 1] = coefsmean[2]
        coefficients[i, 2] = coefsmean[3]
        os.chdir(cwd)

    return sorted(files), coefficients, angles


if __name__ == "__main__":

    try: 
        sweepdir = str(sys.argv[1])
    
    except (IndexError, ValueError):
        raise SystemExit
    
    """
    plt.rcParams.update({
        'text.usetex': True,
        'figure.dpi': 150
    })
    """

    # Get experimental data from table
    
    cl_data = pd.read_csv("./data/Cl_data.csv")
    cd_data = pd.read_csv("./data/Cd_data.csv")

    files, coefs, angles = get_aoasweep_data(sweepdir)

    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    #ax.set_title("Lift coefficient vs angle of attack")
    ax.plot(cl_data["aoa"], cl_data["400k"], marker=".", label="Experiment (Bartl, Sagmo, Bracchi, Sætran)")
    ax.plot(angles, coefs[:,2], marker=".", label=r"$\gamma-Re_\theta$  SST simulation")
    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=15)
    ax.set_ylabel(r"$C_l\quad[-]$", fontsize=15)
    ax.legend()
    
    fig.savefig("AoA_Cl.png")

    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    #ax.set_title("Lift coefficient vs angle of attack")
    ax.plot(cd_data["aoa"], cd_data["400k"], marker=".", label="Experiment (Bartl, Sagmo, Bracchi, Sætran)")
    ax.plot(angles, coefs[:,1], marker=".", label=r"$\gamma-Re_\theta$ SST simulation")
    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=15)
    ax.set_ylabel(r"$C_d\quad[-]$", fontsize=15)
    ax.legend()
    
    fig.savefig("AoA_Cd.png")

    ind = np.where(np.isin(cl_data["aoa"], angles))
    clexp = np.array(cl_data["400k"])[ind]
    cdexp = np.array(cd_data["400k"])[ind]
    