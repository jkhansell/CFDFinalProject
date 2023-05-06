import numpy as np
import matplotlib.pyplot as plt
import os
import sys


def get_meshsweep_data(sweepdir):

    cwd = os.getcwd()
    files = os.listdir(sweepdir)
    #print(files)
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
        coefficients[i,1:] = np.mean(coefs[-300:,2:4], axis=0)
        os.chdir(cwd)
    return sorted(files),sizes, coefficients

if __name__ == "__main__":
    try: 
        sweepdir = str(sys.argv[1])
    
    except (IndexError, ValueError) :
        raise SystemExit
    
    plt.rcParams.update({
    'text.usetex': True,
    'figure.dpi': 150
    })
    plt.tight_layout()
    
    files, sizes, coeffs = get_meshsweep_data(sweepdir)
    
    fig, ax = plt.subplots()
    ax.grid()
    ax.set_axisbelow(True)

    ax.plot(sizes[sizes.argsort()], marker=".")
    ax.set_ylabel("Number of mesh elements")
    ax.set_xticks(range(0,len(files)), np.array([x.replace("GRTsteady0","") for x in files])[sizes.argsort()])
    fig.savefig("meshsizes.svg")

    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)
    
    fig.subplots_adjust(left=0.15)

    coeffs = coeffs[sizes.argsort()] 
    ax.scatter(coeffs[:,0], coeffs[:,1])
    
    #ax.set_title(r"Mesh convergence graph for NRELs826 airfoil at $\theta = 0.0^{\circ}$",fontsize=15)
    ax.ticklabel_format(axis="x", style="sci", scilimits=(1,2))
    ax.tick_params(axis='both', which='major', labelsize=17)
    ax.set_ylim(0.0, 0.03)
    ax.set_xlabel("Number of mesh elements", fontsize=17)
    ax.set_ylabel(r"$C_d$", fontsize=17)
    fig.savefig("Cd_conv.svg")
    
    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)

    ax.scatter(coeffs[:,0], coeffs[:,2])
    #ax.set_title(r"Mesh convergence graph for NRELs826 airfoil at $\theta = 0.0^{\circ}$",fontsize=15)
    ax.ticklabel_format(axis="x", style="sci", scilimits=(1,2))
    ax.tick_params(axis='both', which='major', labelsize=17)
    ax.set_ylim(0.3, 0.8)
    ax.set_xlabel("Number of mesh elements", fontsize=17)
    ax.set_ylabel(r"$C_l$", fontsize=17)
    fig.savefig("Cl_conv.svg")


    print("\n", coeffs[-4:,2])
    print(coeffs[-4:,2].mean(), coeffs[-4:,2].std())

    