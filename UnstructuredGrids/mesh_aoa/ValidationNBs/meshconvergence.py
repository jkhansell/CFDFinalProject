import numpy as np
import matplotlib.pyplot as plt
import os
import sys


def get_meshsweep_data(sweepdir):

    cwd = os.getcwd()
    files = os.listdir(sweepdir)
    coefficients = np.zeros((len(files), 3))
    sizes = np.zeros(len(files))
    for i, file in enumerate(sorted(files)):
        os.chdir(os.path.join(sweepdir, file))
        with open("mesh.log") as f:
            lines = f.readlines()
            coefficients[i,0] = float(lines[30][10:])
            sizes[i] = float(lines[30][10:])
            f.close()
        coefs = np.loadtxt("postProcessing/forceCoeffs/0/forceCoeffs.dat", skiprows=9 , delimiter="\t")
        coefficients[i,1:] = np.mean(coefs[-100:,2:4], axis=0)
        os.chdir(cwd)
    return sorted(files),sizes, coefficients

if __name__ == "__main__":
    try: 
        sweepdir = str(sys.argv[1])
    
    except (IndexError, ValueError) :
        raise SystemExit

    files, sizes, coeffs = get_meshsweep_data(sweepdir)
    
    fig, ax = plt.subplots()
    ax.plot(sizes[sizes.argsort()], marker=".")
    ax.set_xlabel("Case")
    ax.set_ylabel("Number of mesh elements")
    ax.set_xticks(range(0,len(files)), np.array(files)[sizes.argsort()], rotation=50)
    fig.savefig("meshsizes.png")

    fig, ax = plt.subplots()

    ax.plot(coeffs[:,0], coeffs[:,2],marker=".")
    ax.set_xlabel("Number of mesh elements")
    ax.set_ylabel("Lift Coefficient")
    fig.savefig("Cl_conv.png")
    
    print("\n", coeffs[-4:,2])
    print(coeffs[-4:,2].mean(), coeffs[-4:,2].std())

    