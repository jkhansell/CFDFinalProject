import numpy as np 
import matplotlib.pyplot as plt
import os
import sys

def get_aoasweep_data(sweepdir):

    cwd = os.getcwd()
    files = os.listdir(sweepdir)
    coefficients = np.zeros((len(files),3))
    angles = np.arange(-6, 18, 2)

    print(files )
    for i, file in enumerate(files):
        os.chdir(os.path.join(sweepdir,file))
        coefs = np.loadtxt("postProcessing/forceCoeffs/0/forceCoeffs.dat", skiprows=9 , delimiter="\t")
        coefficients[i, 1:] = np.mean(coefs[-100, 2:4], axis=0)
        os.chdir(cwd) 
    return sorted(files), coefficients, angles


if __name__ == "__main__":

    try: 
        sweepdir = str(sys.argv[1])
    
    except (IndexError, ValueError) :
        raise SystemExit
    
    plt.rcParams.update({
        'text.usetex': True,
        'figure.dpi': 150
    })

    files, coefs, angles = get_aoasweep_data(sweepdir)

    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.plot(angles, coefs[:,1], marker=".")
    ax.set_xlabel("Angle of attack $(^\circ)$")
    ax.set_ylabel(r"C_l ")
    fig.savefig("AoA_Cl.png")